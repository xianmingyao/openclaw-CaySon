# Claude Code 大型项目最佳实践

> 来源：抖音@AI随风 + Anthropic官方文档 + Matt Pocock Skills + Addy Osmani认知债务理论
> 日期：2026-05-21
> 标签：Claude_Code / AI_编程 / 工程实践 / 大型项目

---

## 1. 🎯 这是什么（简介）

Claude Code 是 Anthropic 推出的**agentic 编程工具**，能读取代码库、编辑文件、运行命令、集成开发工具。区别于传统 chatbot，它**自主工作流**而非被动问答。

大型项目最佳实践是**让 Claude Code 在复杂项目中高效、安全、可控运作的工程规范**。

---

## 2. 📝 关键功能点

### 2.1 Agentic 核心能力

| 能力 | 说明 |
|------|------|
| **自主决策** | 自主探索、规划、实施 |
| **多工具集成** | 文件操作 + 命令执行 + API调用 |
| **多端支持** | Terminal / IDE / Desktop / Browser |
| **上下文理解** | 读取整个代码库 |
| **安全控制** | 权限分级、数据使用政策 |
| **可扩展性** | MCP / Plugins / Skills / Subagents |

### 2.2 大型项目核心功能

| 功能 | 说明 |
|------|------|
| **Plan Mode** | 探索→规划→实施，分离研究与执行 |
| **Subagents** | 子代理，独立上下文处理专项任务 |
| **Checkpointing** | 自动快照，任意回滚 |
| **Auto Mode** | 自主运行 + 后台安全检查 |
| **Sessions** | 多会话管理，类 git worktree |
| **Non-interactive Mode** | `claude -p "prompt"` 用于 CI/自动化 |

---

## 3. ⚡ 怎么使用

### 3.1 推荐工作流：探索→规划→实施→提交

```
┌─────────────────────────────────────────────────────────┐
│  Step 1: 探索 (Plan Mode)                               │
│  "read /src/auth, understand session handling"            │
├─────────────────────────────────────────────────────────┤
│  Step 2: 规划 (Plan Mode)                               │
│  "I want to add OAuth. What files need change? Plan."    │
├─────────────────────────────────────────────────────────┤
│  Step 3: 实施 (Default Mode)                            │
│  "implement from your plan, write tests"                 │
├─────────────────────────────────────────────────────────┤
│  Step 4: 提交                                           │
│  "commit with descriptive message, open PR"              │
└─────────────────────────────────────────────────────────┘
```

### 3.2 关键命令

```bash
# Plan Mode - 分离研究与执行
claude --plan

# Non-interactive - CI/自动化
claude -p "fix all lint errors"

# 子代理 - 隔离上下文
"use subagents to investigate authentication flow"

# 快照回滚
/rewind

# 上下文压缩
/compact <instructions>

# 清空上下文
/clear

# 会话管理
claude --continue    # 继续最近会话
claude --resume     # 选择会话
/rename             # 重命名会话
```

### 3.3 CLAUDE.md 配置

```markdown
# Code style
- Use ES modules (import/export), not CommonJS
- Destructure imports when possible

# Workflow
- Typecheck after code changes
- Prefer single test runs over full suite

# Gotchas
- API rate limits on unauthenticated requests
```

---

## 4. ✅ 优点

| 优点 | 说明 |
|------|------|
| **上下文管理** | 自动压缩、快照、回滚 |
| **子代理隔离** | 专项任务不污染主上下文 |
| **多端覆盖** | Terminal/IDE/Desktop/Browser |
| **自动化友好** | Non-interactive Mode + Auto Mode |
| **安全控制** | Permission Modes + Hooks |
| **并行扩展** | Worktrees + Agent Teams |

---

## 5. ❌ 缺点

| 缺点 | 说明 |
|------|------|
| **上下文膨胀** | 大项目上下文消耗快 |
| **Vibe Coding 陷阱** | AI写对你不知道为什么对 |
| **测试文件被改** | Claude可能改测试期望值"作弊" |
| **CLAUDE.md 过载** | 过长被忽略 |
| **无限探索** | 无 scoped 调查会读几百个文件 |

---

## 6. 🎬 使用场景

| 场景 | 最佳实践 |
|------|----------|
| **新代码库上手** | Plan Mode 探索 + 问答式学习 |
| **复杂功能实现** | 先规划再实施，加入验证 |
| **代码审查** | 新 session 避免 bias，Writer/Reviewer 模式 |
| **大型迁移** | Fan-out 并行 + `--allowedTools` 限制 |
| **CI/自动化** | `claude -p` + `stream-json` 输出 |
| **安全审查** | Subagent 专项审查 |
| **Bug 修复** | 先复现→验证→修复 |

---

## 7. 🔧 运行依赖环境

| 依赖 | 说明 |
|------|------|
| **Node.js/npm** | CLI 安装 |
| **Git** | 版本控制 |
| **API Key** | ANTHROPIC_API_KEY |
| **gh CLI** | GitHub 集成（可选）|
| **MCP Servers** | 外部工具集成（可选）|

---

## 8. 🚀 部署使用注意点

### 8.1 上下文管理策略

```javascript
// 核心原则：上下文是最宝贵资源
// 策略1：任务间 /clear
/clear  // 清空无关任务

// 策略2：自动压缩
// Claude 自动压缩保留重要信息

// 策略3：Subagent 隔离
"use subagents to investigate X"  // 探索不污染主上下文
```

### 8.2 权限配置

```javascript
// claude_code_config.json
{
  "permissions": {
    "allow": ["read", "edit", "Bash(npm run test)"],
    "deny": ["network", "dangerous_bash"]
  }
}
```

### 8.3 Auto Mode 安全分类器

```bash
claude --permission-mode auto -p "fix all lint errors"
# 分类器自动审批安全操作
# 阻止：范围升级、未知基础设施、恶意内容
```

---

## 9. 🕳️ 避坑指南

### 坑1：Kitchen Sink Session
**问题**：一个 session 干多件事，上下文充满无关信息

**解决**：
```bash
/clear  # 任务间必须清空
```

### 坑2：Correcting Over and Over
**问题**：两次修正后仍错，污染上下文

**解决**：
```bash
/clear  # 重新写更精确的初始 prompt
```

### 坑3：CLAUDE.md 过载
**问题**：规则太多，Claude 忽略重要指令

**解决**：
- 保持简洁
- 定期修剪
- 问自己："删了会导致错误吗？" → 否就删

### 坑4：Trust-Then-Verify Gap
**问题**：实现看起来对但实际不行

**解决**：
- 必须提供验证方式（测试/截图/输出）
- 无法验证就不交付

### 坑5：无限探索
**问题**：无 scoped 调查读几百个文件

**解决**：
```bash
"use subagents to investigate X"  # 隔离探索
/compact Focus on <topic>         # 压缩上下文
```

---

## 10. 📊 总结

### 学习价值：⭐⭐⭐⭐⭐（5星）

Claude Code 大型项目最佳实践是**现代 AI 编程工程的精髓**，融合了：
- Anthropic 官方工程规范
- Matt Pocock 的工程纪律（diagnose/caveman/grill-me）
- Addy Osmani 的认知债务理论

### 推荐指数：⭐⭐⭐⭐⭐（5星）

**核心收获**：
1. **上下文管理** > 代码能力
2. **验证机制** > 盲目相信
3. **探索→规划→实施** > 直接动手
4. **Subagent 隔离** > 单一 session
5. **认知债务意识** > 交付即结束

### 适合委托 vs 不能委托

| ✅ 可以委托 | ❌ 不能委托 |
|------------|-------------|
| 样板代码 | 系统架构 |
| 胶水代码 | 核心业务逻辑 |
| 格式化 | 安全关键代码 |
| 简单 CRUD | 性能优化 |
| 自动化脚本 | 调试（需理解原理）|

### 一句话总结

> Claude Code 是大型项目的**加速器**，但架构决策和核心逻辑必须自己懂——AI 可以帮你写代码，但不能替你做工程决策。

---

## 附录：Matt Pocock Skills 补充

CaySon 已安装的 Matt Pocock Skills 可配合使用：

- **`caveman`** — 极简交流，节省 75% token
- **`diagnose`** — 6阶段调试纪律
- **`grill-me`** — 面试式盘问达成共识

## 附录：Addy Osmani 认知债务 6 步法

1. 形成假说（先自己想，再问AI）
2. 解释后要代码（"我来解释需求，你来写"）
3. 打开学习模式（"给我讲原理"）
4. 评审AI输出（"这段在做什么？"）
5. 手写重推（关掉AI自己写）
6. 让模型解释Bug（"为什么这样修？"）
