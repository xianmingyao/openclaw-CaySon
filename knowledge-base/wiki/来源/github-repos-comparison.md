# 三大 Claude Code 相关仓库深度对比分析

> 研究日期：2026-04-02
> 来源：Web搜索 + 官方文档

---

## 0. 📚 背景故事（必看）

### Claude Code 源码泄露事件

**2026年3月31日**，Anthropic 在 npm 包中意外泄漏了 Claude Code 的源码（59.8MB sourcemap，512,000行TypeScript代码）。

**社区反应：**
- 有人直接托管泄露代码 → 法律风险
- **clean-room rewrite** 成为最安全的方案
- 2小时内诞生 GitHub 史上最快达成 50K Stars 的仓库

---

## 1. 🏠 三个仓库简介

### 仓库A：unohee/OpenSwarm
**定位：** Multi-Agent 编排器

```json
{
  "GitHub": "github.com/unohee/OpenSwarm",
  "Stars": "232+",
  "语言": "TypeScript",
  "定位": "Claude Code CLI 多智能体编排器"
}
```

**核心功能：**
- 编排多个 Claude Code CLI 实例作为自主代理
- 从 Linear 拾取 Issue
- Worker/Reviewer 流水线
- Discord 进度汇报
- LanceDB 向量记忆

---

### 仓库B：instructkr/claw-code ⭐
**定位：** Clean-Room Agent Harness

```json
{
  "GitHub": "github.com/instructkr/claw-code",
  "Stars": "48,000+ ⭐",
  "语言": "Python → Rust（重写中）",
  "定位": "Claude Code 架构的清洁室实现"
}
```

**核心亮点：**
- **GitHub史上最快达成50K Stars的仓库**（2小时）
- 清洁室重写，不含任何原始代码
- 提取 Claude Code 的 Agent Harness 架构
- 现在与 OmX (oh-my-codex) 合作
- 正在 Rust 重写，性能优化中

---

### 仓库C：sanbuphy/claude-code-source-code
**定位：** 泄露源码存档

```json
{
  "GitHub": "github.com/sanbuphy/claude-code-source-code",
  "Forks": "41,500+",
  "语言": "TypeScript（原始泄露）",
  "定位": "Claude Code 原始泄露源码存档"
}
```

**特点：**
- 直接托管泄露的源码
- **⚠️ 法律风险高**（含 Anthropic 专有代码）
- Fork 41,500+ 次
- 主要用于研究目的

---

## 2. 🎯 各仓库用途与场景

### 2.1 OpenSwarm

**适合谁用：**
- 有 Linear 项目管理习惯的团队
- 需要 AI 自动处理 Issue → PR 全流程
- 想有多 Agent 协作（Worker + Reviewer）
- 需要 Discord 通知

**使用场景：**
```
团队用 Linear 管任务
    ↓
OpenSwarm 自动分配给多个 Claude Code Agent
    ↓
Worker 写代码 → Reviewer 审查 → Tester 测试
    ↓
Discord 实时汇报进度
    ↓
代码自动合并
```

**不适用的场景：**
- ❌ 没有 Linear 的团队（集成成本高）
- ❌ 个人开发者（过度工程）
- ❌ 简单任务（单个 Claude Code 足够）

---

### 2.2 claw-code (instructkr) ⭐

**适合谁用：**
- 想构建自己的 Claude Code 风格 Agent
- 需要学习 Agent Harness 架构
- 想要一个可控的 AI 编程框架
- 愿意使用前沿技术（Rust 重写版）

**使用场景：**
```
学习 Agent 架构
    ↓
基于 claw-code 构建自定义 Agent
    ↓
接入自己的 LLM（OpenAI/Anthropic/本地）
    ↓
扩展工具集和工作流
```

**不适用的场景：**
- ❌ 想要开箱即用的完整产品
- ❌ 只需要简单调用 Claude Code
- ❌ 法律敏感项目（虽然 clean-room 但仍有争议）

---

### 2.3 claude-code-source-code (sanbuphy)

**适合谁用：**
- 安全研究人员
- 想深入研究 Claude Code 架构细节
- 确认 Claude Code 实际能力边界

**使用场景：**
```
安全审计
    ↓
学习 Claude Code 内部实现
    ↓
确认某些功能是否存在
```

**不适用的场景：**
- ❌ 生产环境使用（法律风险）
- ❌ 商业项目集成
- ❌ 任何需要稳定性的场景

---

## 3. ✅ 优点 vs ❌ 缺点

### OpenSwarm

| 优点 | 缺点 |
|------|------|
| ✅ 开箱即用的多 Agent 协作 | ❌ 强依赖 Linear（不是通用工具） |
| ✅ Discord 通知，团队友好 | ❌ 需要多个 Claude Code 许可证 |
| ✅ Worker/Reviewer 流水线设计 | ❌ 架构相对简单，定制有限 |
| ✅ LanceDB 记忆，持久化 | ❌ Stars 只有 232，社区小 |
| ✅ TypeScript，与现代工具链兼容 | ❌ 可能是 fork，活跃度待确认 |

---

### claw-code (instructkr) ⭐

| 优点 | 缺点 |
|------|------|
| ✅ **48K Stars，顶级社区认可** | ❌ Rust 重写中，Python 版可能过时 |
| ✅ Clean-room，合法安全 | ❌ 不是完整产品，是框架 |
| ✅ 架构完整，文档丰富 | ❌ 需要自己配置 LLM 和工具 |
| ✅ 多语言支持（Python → Rust） | ❌ 依赖外部 LLM API |
| ✅ 启发了一大波 "Claw" 系列项目 | ❌ 社区分裂（各种 fork） |

---

### claude-code-source-code (sanbuphy)

| 优点 | 缺点 |
|------|------|
| ✅ 完整源码，可深度研究 | ❌ **法律风险极高** |
| ✅ 41,500+ Fork，传播最广 | ❌ 不适合生产使用 |
| ✅ 无需理解"重写"的抽象 | ❌ 可能含恶意代码（未审计） |
| ✅ 确认 Claude Code 真实能力 | ❌ Anthropic 可随时要求删除 |

---

## 4. 👤 技术小白使用指南

### 如果你是小白，强烈建议：❌ 都不要直接使用！

**原因：**
- OpenSwarm：需要配置 Linear + Discord + Claude Code，成本高
- claw-code：需要编程能力配置 LLM 和工具链
- sanbuphy：法律风险 + 技术难度最高

### 建议路径：

```
1. 先用官方 Claude Code（最简单）
   ↓
2. 理解 Agent 是什么、能做什么
   ↓
3. 再考虑 OpenSwarm / claw-code
```

### 如果非要尝试：

**最简单的选择：claw-code**
```bash
# 安装
pip install claw-code

# 运行
claw-code

# 需要配置：
# - OPENAI_API_KEY 或 ANTHROPIC_API_KEY
# - 理解基本 Agent 概念
```

**不建议选 OpenSwarm，除非：**
- 你已经在用 Linear
- 你的团队需要自动化工作流
- 你有 Discord webhook 配置经验

**绝对不建议选 sanbuphy 版本**
- 法律风险
- 没有任何支持
- 随时可能被 DMCA

---

## 5. 🔍 三者深度对比

### 5.1 定位对比

| 维度 | OpenSwarm | claw-code | sanbuphy |
|------|-----------|-----------|----------|
| **定位** | 多 Agent 编排 | Agent Harness 框架 | 源码存档 |
| **类型** | 应用工具 | 开发框架 | 研究资料 |
| **法律风险** | 低 | 低 | **极高** |
| **Stars** | 232 | **48,000+** | Fork 41,500 |

### 5.2 技术架构对比

| 架构 | OpenSwarm | claw-code | sanbuphy |
|------|-----------|-----------|----------|
| **核心模式** | 多 CLI 实例编排 | Agent Loop + Tool Calling | 原始 TypeScript |
| **Agent 设计** | Worker/Reviewer | Human-in-the-loop | 单 Agent |
| **记忆系统** | LanceDB | 可扩展 | 无 |
| **工具集成** | Git/Linear/Discord | 插件系统 | 原始工具 |
| **扩展方式** | 修改代码 | 插件/模块 | 直接修改源码 |

### 5.3 社区生态对比

| 生态 | OpenSwarm | claw-code | sanbuphy |
|------|-----------|-----------|----------|
| **Stars** | 232 | **48,000+** | Fork 41,500 |
| **社区** | 小众 | **火热** | 历史事件 |
| **Fork** | 20+ | 100+ | 41,500 |
| **文档** | 基础 | 丰富 | 无官方 |
| **持续维护** | 待确认 | **活跃（Rust）** | 无 |

---

## 6. 🏆 哪个更好？如何选择？

### 评分总结

| 仓库 | 学习价值 | 使用难度 | 社区热度 | 法律安全 | 推荐指数 |
|------|---------|---------|---------|---------|---------|
| **OpenSwarm** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **claw-code** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **sanbuphy** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ |

### 选择建议

**选 OpenSwarm 如果：**
- 你在用 Linear 做项目管理
- 需要自动化团队工作流
- 想体验"AI开发团队"

**选 claw-code 如果：**
- 想学习 Agent 架构
- 想构建自己的编程 Agent
- 需要一个可控的框架

**选 sanbuphy 如果：**
- 安全研究人员
- 需要审计 Claude Code 能力
- 不在乎法律风险

---

## 7. 🔗 与 OpenClaw 的关系

### OpenClaw 是什么？

OpenClaw 是当前 AI 助手的运行环境，支持：
- 多渠道（微信/Telegram/Discord）
- Skills 技能系统
- sessions_spawn 多 Agent 协作
- Cron 定时任务

### OpenSwarm vs OpenClaw

| 维度 | OpenSwarm | OpenClaw |
|------|-----------|----------|
| **核心** | Claude Code CLI 编排 | AI 助手框架 |
| **Agent** | Claude Code 实例 | 自有 Agent |
| **集成** | Linear/Discord | 多渠道消息 |
| **记忆** | LanceDB | Mem0/ChromaDB |
| **定位** | AI 开发团队 | 个人 AI 助手 |

**关系：** 互补而非竞争
- OpenSwarm 专注 AI 编程工作流
- OpenClaw 专注个人效率助手

---

## 8. 📊 最终结论

### 核心结论

```
1. claw-code 赢了社区热度（48K Stars）
2. sanbuphy 赢了传播广度（41K Forks）
3. OpenSwarm 赢了特定场景（Linear集成）

但：
- 如果你是小白 → 都不建议用，先学官方Claude Code
- 如果你想学习 → 选 claw-code（clean-room，合法）
- 如果你想用 → 选 OpenSwarm（如果你有Linear）
- 如果你想研究 → 选 sanbuphy（注意法律）
```

### 对宁兄的建议

根据宁兄的背景（CTO、24年经验、Windows自动化、跨境电商）：

| 优先级 | 推荐 | 理由 |
|--------|------|------|
| **第一** | OpenClaw（当前系统） | 已经在用，深度集成 |
| **第二** | claw-code | 学习Agent架构，参考价值高 |
| **第三** | OpenSwarm | 有Linear需求时再用 |
| **不看** | sanbuphy | 法律风险，无实际使用价值 |

---

## 附录：相关链接

- OpenSwarm: https://github.com/unohee/OpenSwarm
- claw-code: https://github.com/instructkr/claw-code
- sanbuphy: https://github.com/sanbuphy/claude-code-source-code
- DeepWiki claw-code: https://deepwiki.com/instructkr/claw-code
- Cybernews报道: https://cybernews.com/tech/claude-code-leak-spawns-fastest-github-repo/

