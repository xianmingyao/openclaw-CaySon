---
name: control-agent
description: OpenClaw 智能体控制技能，包含子 Agent Spawn、Kill、Steer、Status、Session 管理等所有 Agent 控制操作
category: agent-control
version: 1.0.0
author: jingmai-agent
---

# Control-Agent 智能体控制指南

你是一个 OpenClaw 智能体控制系统。你可以通过以下预定义操作控制子 Agent 的生命周期和行为。

## 核心概念

**主 Agent 与子 Agent**：
- 你（主 Agent）负责任务分解、决策、结果整合
- 子 Agent（Spawn 创建）负责执行具体子任务
- 通过 `sessions_spawn` 创建子 Agent，通过 `sessions_send` 发送指令
- 通过 `sessions_yield` 回收子 Agent 结果

**Session Key**：
- 每个会话（主 Agent 或子 Agent）都有唯一 sessionKey
- 通过 `sessions_list` 查看所有活跃会话
- 通过 `sessions_history` 查看会话历史

**Agent 运行时**：
- `runtime: "subagent"` — 本地子 Agent，适合一次性任务
- `runtime: "acp"` — ACP 运行时，需要配置 acpx 插件（支持 thread 持久化）

## 可用操作列表

### 1. Agent 生命周期管理

#### sessions_spawn - 创建子 Agent
```json
{"type": "sessions_spawn", "task": "任务描述", "runtime": "subagent", "mode": "run", "model": "minimax/MiniMax-M2.5"}
```
- **参数**: `task`(必需, str), `runtime`(必需, "subagent"|"acp"), `mode`(必需, "run"|"session"), `agentId`(可选, str), `label`(可选, str), `model`(可选, str), `thread`(可选, bool), `cleanup`(可选, "delete"|"keep"), `sandbox`(可选, "inherit"|"require"), `attachments`(可选, array)
- **说明**: 创建新的子 Agent 会话并执行任务。
  - `mode="run"`: 单次执行，完成后自动结束
  - `mode="session"`: 持久会话，可多次交互（需要 `thread=true` 或 ACP runtime）
- **返回**: `{status: "success"|"error", sessionKey?: string, message?: string}`
- **示例**: 创建一次性子 Agent `{"type": "sessions_spawn", "task": "分析这个代码库", "runtime": "subagent", "mode": "run"}`
- **示例**: 创建持久子 Agent `{"type": "sessions_spawn", "task": "编码助手", "runtime": "acp", "agentId": "codex", "mode": "session", "thread": true}`
- **注意**: `runtime="acp"` 需要安装并启用 acpx 插件

#### subagents - 管理子 Agent
```json
{"type": "subagents", "action": "list"}
```
- **参数**: `action`(必需, "list"|"kill"|"steer"), `target`(可选, str), `message`(可选, str), `recentMinutes`(可选, int)
- **说明**: 管理和查看当前会话的子 Agent。
  - `action="list"`: 列出所有子 Agent 状态
  - `action="kill"`: 终止指定子 Agent
  - `action="steer"`: 向指定子 Agent 发送引导消息
- **返回**: 子 Agent 列表或操作结果
- **示例**: 列出子 Agent `{"type": "subagents", "action": "list"}`
- **示例**: 终止子 Agent `{"type": "subagents", "action": "kill", "target": "subagent-session-id"}`
- **示例**: 引导子 Agent `{"type": "subagents", "action": "steer", "target": "subagent-session-id", "message": "换个思路试试"}`

### 2. 会话查询与管理

#### sessions_list - 列出所有会话
```json
{"type": "sessions_list", "kinds": ["main", "subagent"], "limit": 10, "activeMinutes": 60, "messageLimit": 2}
```
- **参数**: `kinds`(可选, array, "main"|"subagent"|"acp"), `limit`(可选, int), `activeMinutes`(可选, int), `messageLimit`(可选, int)
- **说明**: 列出所有活跃会话及其最近消息。
- **返回**: 会话列表，包含 sessionKey、kind、lastMessage 等
- **示例**: 列出主会话 `{"type": "sessions_list", "kinds": ["main"], "messageLimit": 3}`
- **示例**: 列出最近活跃子 Agent `{"type": "sessions_list", "kinds": ["subagent"], "activeMinutes": 30}`

#### sessions_history - 获取会话历史
```json
{"type": "sessions_history", "sessionKey": "main", "limit": 50, "includeTools": false}
```
- **参数**: `sessionKey`(必需, str), `limit`(可选, int), `includeTools`(可选, bool)
- **说明**: 获取指定会话的消息历史。
- **返回**: 消息列表，包含角色、内容、时间戳
- **示例**: 获取主会话历史 `{"type": "sessions_history", "sessionKey": "main", "limit": 100}`
- **示例**: 获取子 Agent 历史（包含工具调用） `{"type": "sessions_history", "sessionKey": "sub-xxx", "includeTools": true}`

#### sessions_send - 向会话发送消息
```json
{"type": "sessions_send", "sessionKey": "sub-xxx", "message": "继续执行下一步"}
```
- **参数**: `sessionKey`(必需, str), `message`(必需, str), `agentId`(可选, str), `timeoutSeconds`(可选, int)
- **说明**: 向指定会话发送消息（支持子 Agent 或其他持久会话）。
- **返回**: 发送结果
- **示例**: 继续子 Agent 任务 `{"type": "sessions_send", "sessionKey": "sub-xxx", "message": "分析完成了，继续写测试代码"}`

#### sessions_yield - 交出控制权
```json
{"type": "sessions_yield", "message": "子 Agent 结果已回收"}
```
- **参数**: `message`(可选, str)
- **说明**: 在 Spawn 子 Agent 后调用，交出当前回合控制权，等待子 Agent 结果作为下一条消息返回。
- **用途**: 用于编排子 Agent，完成后接收其结果继续执行
- **示例**: `{"type": "sessions_yield", "message": "等待子 Agent 完成..."}`

### 3. Agent 状态查询

#### session_status - 获取会话状态
```json
{"type": "session_status", "sessionKey": "main"}
```
- **参数**: `sessionKey`(可选, str)
- **说明**: 获取当前或指定会话的状态信息（使用量、耗时、模型等）。
- **返回**: 状态卡片，包含 usage、time、cost、model 等信息
- **示例**: 查看当前会话状态 `{"type": "session_status"}`
- **示例**: 查看子 Agent 状态 `{"type": "session_status", "sessionKey": "sub-xxx"}`

### 4. 任务编排模式

#### 模式 1: Spawn → Yield → 整合结果
```
1. sessions_spawn(task="分析需求", runtime="subagent", mode="run")
2. sessions_yield(message="等待分析完成")
   → 收到子 Agent 结果
3. sessions_spawn(task="根据分析写代码", runtime="subagent", mode="run")
4. sessions_yield(message="等待代码完成")
   → 收到子 Agent 结果
5. 整合输出最终结果
```

#### 模式 2: 并行 Spawn → 收集所有结果
```
1. sessions_spawn(task="任务A", runtime="subagent", mode="run")  # Agent 1
2. sessions_spawn(task="任务B", runtime="subagent", mode="run")  # Agent 2
3. sessions_spawn(task="任务C", runtime="subagent", mode="run")  # Agent 3
4. sessions_yield()  # 等待所有子 Agent 完成
   → 按完成顺序接收结果
5. 整合所有结果
```

#### 模式 3: 持久会话 + 多次交互
```
1. sessions_spawn(task="作为代码审查助手", runtime="acp", agentId="codex", mode="session", thread=true)
   → 创建持久会话
2. sessions_send(sessionKey="xxx", message="审查这段代码：...")
   → 获取审查结果
3. sessions_send(sessionKey="xxx", message="修复发现的问题")
   → 获取修复结果
4. subagents(action="kill", target="xxx")  # 结束会话
```

#### 模式 4: 子 Agent 链式执行
```
1. sessions_spawn(task="步骤1", runtime="subagent", mode="run")
2. sessions_yield()  # 等待步骤1完成
3. sessions_spawn(task="基于步骤1结果执行步骤2", runtime="subagent", mode="run")
4. sessions_yield()  # 等待步骤2完成
5. ...
```

#### 模式 5: 动态引导子 Agent
```
1. sessions_spawn(task="研究主题X", runtime="subagent", mode="run")
2. subagents(action="steer", target="xxx", message="注意重点关注Y方面")
   → 动态调整子 Agent 行为
3. sessions_yield()
   → 收到调整后的结果
```

#### 模式 6: 条件分支
```
1. sessions_list(kinds=["subagent"])
   → 检查是否有活跃子 Agent
2. subagents(action="list")
   → 获取子 Agent 状态
3. 根据状态决定：
   - 有失败的 → sessions_spawn 重新执行
   - 有超时的 → sessions_send 继续或终止
   - 全部完成 → 整合结果
```

### 5. 错误处理

#### 超时处理
```json
{"type": "sessions_send", "sessionKey": "sub-xxx", "message": "继续", "timeoutSeconds": 30}
```
- **说明**: 向子 Agent 发送消息时设置超时
- **示例**: 30秒无响应则返回超时错误

#### 失败重试
```json
{"type": "subagents", "action": "list"}
```
- **说明**: 先检查子 Agent 状态，根据失败原因决定重试策略
- **重试逻辑**:
  1. 检查是否超时 → 增加超时时间重试
  2. 检查是否错误 → 调整指令后重试
  3. 检查是否卡住 → sessions_send 引导后继续

#### 清理孤儿会话
```json
{"type": "subagents", "action": "kill", "target": "orphan-session-id"}
```
- **说明**: 清理异常退出的子 Agent 会话，避免资源泄漏

### 6. 进阶操作

#### 并行 + 顺序混合编排
```
Phase 1 (并行):
1. sessions_spawn(task="并行任务A1", runtime="subagent", mode="run")
2. sessions_spawn(task="并行任务A2", runtime="subagent", mode="run")
3. sessions_yield() → 收集A阶段结果

Phase 2 (顺序):
4. sessions_spawn(task="基于A结果执行B1", runtime="subagent", mode="run")
5. sessions_yield()
6. sessions_spawn(task="基于B1结果执行B2", runtime="subagent", mode="run")
7. sessions_yield()

Phase 3 (汇总):
8. 整合所有阶段结果
```

#### 批量任务分发
```
1. 拆分大任务为 N 个子任务
2. 批量 sessions_spawn(N 个子 Agent)
3. sessions_yield() 收集所有结果
4. sessions_spawn(task="汇总结果", runtime="subagent", mode="run")
5. sessions_yield() → 最终结果
```

#### 跨会话协作
```json
{"type": "sessions_send", "sessionKey": "main", "message": "任务状态更新：已完成80%"}
```
- **说明**: 主 Agent 向自身发送消息记录进度
- **用途**: 在长任务中记录中间状态

## 重要规则

1. **每个步骤必须选择上述列表中的一个操作**，不要自行创造新的操作名称。
2. **Spawn 后必须调用 sessions_yield** 等待子 Agent 结果，除非是持久会话（mode="session"）。
3. **只包含该步骤需要的参数**，不需要的参数不要输出。
4. **使用 label 为会话命名**，方便后续管理和追踪。
5. **及时清理不需要的子 Agent**，避免资源浪费。
6. **合理选择 runtime**：
   - 一次性任务用 `runtime="subagent"`
   - 需要持久化的任务用 `runtime="acp"`（需配置 acpx 插件）
7. **使用 thread=true 创建 thread-bound 持久会话**，适用于 Discord 等需要线程绑定的场景。
8. **子 Agent 结果作为下一条消息返回**，主 Agent 继续执行整合逻辑。

## 与其他技能的关系

### 与 ralph-loop 的关系
- `control-agent`: 通用 Agent 控制，提供基础的 Spawn/Kill/Steer 能力
- `ralph-loop`: 特定的编码循环执行框架，内部使用 sessions_spawn 管理编码 Agent
- `ralph-loop` 是 `control-agent` 的上层应用

### 与 coding-agent 的关系
- `coding-agent`: 专门的编码任务委托（Codex/Claude Code/OpenCode）
- 内部通过 sessions_spawn 创建编码子 Agent
- 是 `control-agent` 的特化场景

### 与 multi-agent-collaboration 的关系
- `multi-agent-collaboration`: 多智能体协作框架（意图识别+智能路由）
- 底层使用 sessions_spawn 实现多 Agent 协作
- 是 `control-agent` 的协作增强层

## 附录：Agent 运行时说明

### runtime="subagent"
- 本地子 Agent，无需额外配置
- 适合一次性任务
- 不支持 thread 绑定

### runtime="acp"
- ACP 运行时，支持更多特性
- 需要安装 acpx 插件
- 支持 thread-bound 持久会话
- 配置方式：
```yaml
# ~/.openclaw/config.yaml
runtimes:
  acp:
    enabled: true
```
- 安装命令：`openclaw plugins install acpx`

### Agent 类型参考

| agentId | 说明 | 用途 |
|---------|------|------|
| codex | Codex 编码 Agent | 需要代码生成/修改时 |
| claude-code | Claude Code | 需要深度代码分析时 |
| (默认) | MiniMax/其他模型 | 通用任务 |
