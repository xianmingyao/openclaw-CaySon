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

用户输入 → messages[] → Claude API → 响应

↓

stop_reason == "tool_use"?

/                      \

是                       否

↓                        ↓

执行工具                  返回文本

追加 tool_result

循环回退 ────────────────> messages[]

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

// 工具定义通过 buildTool 创建，自动填充默认值

const tool = buildTool({

name: 'Bash',

description: (...) => Promise<string>,  // 动态描述

inputSchema: z.object({...}),

async call(args, context, canUseTool, onProgress) {

// 工具执行逻辑

}

})

### 工具核心接口

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

---