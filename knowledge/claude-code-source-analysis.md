# Claude Code v2.1.88 源码深度剖析

> 来源：https://github.com/sanbuphy/claude-code-source-code
> 时间：2026-04-01
> 免责声明：本仓库源码版权归 Anthropic 所有，仅用于技术研究

---

## 📊 项目概览

| 指标 | 数值 |
|------|------|
| 源文件 (.ts/.tsx) | ~1,884 个 |
| 代码行数 | ~512,664 行 |
| 最大单文件 | `query.ts` (~785KB) |
| 内置工具 | ~40+ 个 |
| 斜杠命令 | ~80+ 个 |
| 依赖包 | 192 个 |
| 运行时 | Bun（编译为 Node.js bundle）|

---

## 🏗️ 核心架构

### Agent 循环原理

```
用户输入 → messages[] → Claude API → 响应
                                    ↓
                        stop_reason == "tool_use"?
                       /                      \
                     是                       否
                      ↓                        ↓
                执行工具                  返回文本
                追加 tool_result
                循环回退 ────────────────> messages[]
```

**这就是最小的代理循环！** Claude Code 在此基础上加了：
- 权限系统
- 流式传输
- 并发控制
- 上下文压缩
- 子代理
- 持久化
- MCP 支持

---

## 🔧 工具系统（Tool.ts 核心要点）

### buildTool 工厂模式

```typescript
// 工具定义通过 buildTool 创建，自动填充默认值
const tool = buildTool({
  name: 'Bash',
  description: (...) => Promise<string>,  // 动态描述
  inputSchema: z.object({...}),
  async call(args, context, canUseTool, onProgress) {
    // 工具执行逻辑
  }
})
```

### 工具核心接口

```typescript
interface Tool<Input, Output, P> {
  name: string
  aliases?: string[]                    // 别名支持
  call(args, context, canUseTool, onProgress): Promise<ToolResult<Output>>
  description(...): Promise<string>     // 动态描述
  inputSchema: z.ZodType               // 输入校验
  
  // 安全相关
  isConcurrencySafe(): boolean         // 并发安全？
  isReadOnly(): boolean                // 只读？
  isDestructive(): boolean             // 破坏性操作？
  checkPermissions(): Promise<PermissionResult>
  
  // UI 渲染
  renderToolUseMessage(): ReactNode
  renderToolResultMessage(): ReactNode
  renderToolUseProgressMessage(): ReactNode
}
```

### 工具默认行为（buildTool 填充）

| 方法 | 默认值 | 安全策略 |
|------|--------|----------|
| `isEnabled` | `true` | - |
| `isConcurrencySafe` | `false` | 默认不安全 |
| `isReadOnly` | `false` | 默认会写 |
| `isDestructive` | `false` | 默认非破坏 |
| `checkPermissions` | `allow` | 默认允许 |
| `toAutoClassifierInput` | `''` | 默认跳过分类器 |

**重要洞察：Fail-closed 安全策略！**

---

## 📁 目录结构

```
src/
├── main.tsx              # REPL 引导程序 (4,683 行!)
├── QueryEngine.ts         # SDK/headless 查询引擎
├── query.ts              # 主代理循环 (785KB，最大文件)
├── Tool.ts               # 工具接口 + buildTool 工厂
├── Task.ts               # 任务类型、ID、状态基类
├── tools.ts              # 工具注册、预设、过滤
├── commands.ts           # 斜杠命令 (~80个)
├── context.ts            # 用户输入上下文
├── cost-tracker.ts       # API 成本累积
├── setup.ts             # 首次运行设置
│
├── bridge/               # Claude Desktop / 远程桥接
│   ├── bridgeMain.ts    # 会话生命周期
│   ├── bridgeApi.ts     # HTTP 客户端 (OAuth + JWT)
│   ├── bridgeMessaging.ts # 消息中继
│   └── ...
│
├── cli/                  # CLI 基础设施
├── commands/            # ~80 个斜杠命令
├── components/          # React/Ink 终端 UI
├── tasks/               # 任务实现
└── tools/               # 40+ 工具实现
```

---

## 🔐 权限系统

### 权限模式

```typescript
type PermissionMode = 
  | 'default'           // 标准模式
  | 'bypass-permissions' // 跳过权限（自动化）
  | 'no-permissions'    // 无权限模式

// 权限结果
type PermissionResult = {
  behavior: 'allow' | 'deny' | 'ask'
  updatedInput?: Record<string, unknown>  // 可修改输入
}
```

### 权限规则

```typescript
// 按来源的规则
alwaysAllowRules: ToolPermissionRulesBySource   // 总是允许
alwaysDenyRules: ToolPermissionRulesBySource    // 总是拒绝
alwaysAskRules: ToolPermissionRulesBySource     // 总是询问
```

### 安全分类器

```typescript
// 工具执行前的自动安全检查
toAutoClassifierInput(input: unknown): unknown
// 示例: `ls -la` for Bash, `/tmp/x: new content` for Edit
```

---

## 🧩 MCP (Model Context Protocol) 集成

### MCP 连接管理

```typescript
interface MCPServerConnection {
  serverName: string
  tools: Tool[]
  resources: ServerResource[]
}
```

### MCP 工具特点

- 通过 `mcpInfo` 标识 `{ serverName, toolName }`
- 支持 `shouldDefer` 延迟加载
- 支持 `alwaysLoad` 立即加载
- `_meta['anthropic/alwaysLoad']` 控制

---

## 🎯 任务系统（Task.ts）

### 任务类型

```typescript
type TaskType =
  | 'local_bash'       // 本地 Bash
  | 'local_agent'      // 本地子代理
  | 'remote_agent'     // 远程子代理
  | 'in_process_teamate' // 进程内队友
  | 'local_workflow'   // 本地工作流
  | 'monitor_mcp'      // MCP 监控
  | 'dream'            // 梦境模式
```

### 任务状态

```typescript
type TaskStatus = 'pending' | 'running' | 'completed' | 'failed' | 'killed'

// 终端状态检查
function isTerminalTaskStatus(status): boolean {
  return status === 'completed' || status === 'failed' || status === 'killed'
}
```

### 任务 ID 生成

```typescript
// 36^8 ≈ 2.8 万亿组合，防暴力攻击
function generateTaskId(type: TaskType): string {
  const prefix = TASK_ID_PREFIXES[type] ?? 'x'
  const bytes = randomBytes(8)
  let id = prefix
  for (let i = 0; i < 8; i++) {
    id += TASK_ID_ALPHABET[bytes[i]! % TASK_ID_ALPHABET.length]
  }
  return id
}
```

---

## 🌉 桥接系统（Bridge）

### OAuth + JWT 认证

```typescript
// Token 刷新机制
async function withOAuthRetry<T>(fn, context) {
  const response = await fn(accessToken)
  
  if (response.status === 401) {
    // 尝试刷新 token
    const refreshed = await deps.onAuth401(accessToken)
    if (refreshed) {
      // 重试请求
      return retry with new token
    }
  }
  return response
}
```

### API 端点

| 方法 | 端点 | 用途 |
|------|------|------|
| `POST` | `/v1/environments/bridge` | 注册环境 |
| `GET` | `/v1/environments/{id}/work/poll` | 轮询工作 |
| `POST` | `/v1/environments/{id}/work/{workId}/ack` | 确认工作 |
| `POST` | `/v1/environments/{id}/work/{workId}/heartbeat` | 心跳保活 |
| `POST` | `/v1/sessions/{id}/events` | 权限响应事件 |

---

## 🚀 代理开发秘诀

### 1. **工具设计模式**

```typescript
// ✅ 正确：使用 buildTool 工厂
const ReadTool = buildTool({
  name: 'Read',
  description: async (input, options) => {
    // 动态描述：根据输入返回不同描述
    return `Read file at ${input.file_path}`
  },
  inputSchema: z.object({
    file_path: z.string()
  }),
  async call(args, context, canUseTool, onProgress) {
    // 1. 检查权限
    // 2. 验证输入
    // 3. 执行操作
    // 4. 返回结果 + 新消息
    return {
      data: content,
      newMessages: [...] // 可追加消息
    }
  }
})
```

### 2. **权限规则配置**

```typescript
// 在上下文中配置权限
const context: ToolUseContext = {
  mode: 'default',
  alwaysAllowRules: {
    'Read': ['*.ts', '*.md'],      // 允许读特定文件
    'Bash': ['git status', 'ls *']  // 允许特定命令
  },
  alwaysDenyRules: {
    'Bash': ['rm -rf /*', 'dd *']   // 禁止危险命令
  }
}
```

### 3. **进度报告机制**

```typescript
// 长时间运行的工具应该报告进度
async call(args, context, canUseTool, onProgress) {
  onProgress?.({
    toolUseID,
    data: { type: 'progress', message: 'Reading...' }
  })
  
  // 执行...
  
  onProgress?.({
    toolUseID,
    data: { type: 'progress', message: 'Processing...' }
  })
}
```

### 4. **并发安全检查**

```typescript
// 关键：isConcurrencySafe 决定是否可以并行执行
const WriteTool = buildTool({
  name: 'Write',
  isConcurrencySafe: (input) => {
    // 检查是否写入同一个文件
    return false  // 默认不安全
  }
})
```

### 5. **MCP 工具集成**

```typescript
// MCP 工具自动包装
const mcpTool = buildTool({
  name: `mcp__${serverName}__${toolName}`,
  isMcp: true,
  mcpInfo: { serverName, toolName },
  shouldDefer: true,  // 延迟加载
  alwaysLoad: false,
  
  async call(args, context, canUseTool, onProgress) {
    // 调用 MCP 服务器
    const result = await mcpClient.callTool(toolName, args)
    return { data: result }
  }
})
```

---

## 💡 对 OpenClaw/Agent 开发的启示

### 1. **分层权限系统**

Claude Code 的权限系统值得借鉴：
- 规则匹配（ glob 模式）
- 来源追溯（哪个工具调用）
- 自动分类器（安全检查）
- 操作审计（决策日志）

### 2. **工具描述动态化**

```typescript
// 好的实践：根据上下文返回不同描述
description: async (input, options) => {
  if (options.isNonInteractiveSession) {
    return 'Execute command (non-interactive mode)'
  }
  return `Execute: ${input.command}`
}
```

### 3. **结果渲染分离**

```typescript
// UI 渲染与逻辑分离
mapToolResultToToolResultBlockParam(output, toolUseID)
// → 转为 API 格式

renderToolResultMessage(output, progressMessages, options)
// → React 组件渲染
```

### 4. **任务追踪**

```typescript
// 每个任务有唯一 ID + 输出文件
const task = {
  id: generateTaskId('local_bash'),
  outputFile: getTaskOutputPath(id),
  outputOffset: 0,  // 增量读取
  status: 'running'
}
```

### 5. **远程会话管理**

```typescript
// 心跳保活
async heartbeatWork(environmentId, workId, sessionToken) {
  const response = await axios.post(..., {
    headers: { Authorization: `Bearer ${sessionToken}` },
    timeout: 10_000
  })
  return { lease_extended, state }
}
```

---

## ⚠️ 缺失的 108 个模块

这些功能被 `feature()` 编译时消除，未发布：

| 模块 | 功能 | Feature Gate |
|------|------|--------------|
| `daemon/*` | 后台守护进程 | `DAEMON` |
| `proactive/*` | 主动通知 | `PROACTIVE` |
| `contextCollapse/*` | 上下文折叠 | `CONTEXT_COLLAPSE` |
| `coordinator/*` | 多代理协调 | `COORDINATOR_MODE` |
| `kairo/*` | 助手模式 | `KAIROS` |
| `workflows/*` | 工作流 | `WORKFLOW_SCRIPTS` |

---

## 📈 总结

### 核心学习点

1. **Agent 循环简单，工程化复杂**
   - 核心 loop 就是：API → 工具 → 循环
   - 生产级需要：权限、进度、并发、压缩、MCP

2. **工具接口设计精髓**
   - `buildTool` 工厂模式统一入口
   - Fail-closed 安全策略
   - 描述/渲染与逻辑分离

3. **权限系统设计**
   - 规则引擎（glob 匹配）
   - 来源追踪
   - 自动分类器

4. **任务系统设计**
   - 唯一 ID 生成
   - 状态机管理
   - 输出持久化

5. **远程桥接架构**
   - OAuth + JWT 双认证
   - 心跳保活
   - 幂等操作

### 对宁兄的建议

如果要开发类似的 Agent 系统，建议：

1. **先搭框架**：权限 + 任务 + 工具注册
2. **核心循环**：参考 query.ts 的实现
3. **渐进功能**：MCP → 子代理 → 工作流
4. **安全第一**：权限系统要 fail-closed

---

## 🔗 资源链接

- GitHub: https://github.com/sanbuphy/claude-code-source-code
- 原版 npm: `@anthropic-ai/claude-code@2.1.88`
- 中文分析: README_CN.md (17KB)

---

## 标签

#ClaudeCode #Agent开发 #源码分析 #工具设计 #权限系统 #MCP
