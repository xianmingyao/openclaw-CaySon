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

{

"GitHub": "github.com/unohee/OpenSwarm",

"Stars": "232+",

"语言": "TypeScript",

"定位": "Claude Code CLI 多智能体编排器"

}

**核心功能：**

- 编排多个 Claude Code CLI 实例作为自主代理

- 从 Linear 拾取 Issue

- Worker/Reviewer 流水线

- Discord 进度汇报

- LanceDB 向量记忆

---

### 仓库B：instructkr/claw-code ⭐

**定位：** Clean-Room Agent Harness

{

"GitHub": "github.com/instructkr/claw-code",

"Stars": "48,000+ ⭐",

"语言": "Python → Rust（重写中）",

"定位": "Claude Code 架构的清洁室实现"

}

**核心亮点：**

- **GitHub史上最快达成50K Stars的仓库**（2小时）

- 清洁室重写，不含任何原始代码

- 提取 Claude Code 的 Agent Harness 架构

- 现在与 OmX (oh-my-codex) 合作

- 正在 Rust 重写，性能优化中

---

### 仓库C：sanbuphy/claude-code-source-code

**定位：** 泄露源码存档

{

"GitHub": "github.com/sanbuphy/claude-code-source-code",

"Forks": "41,500+",

"语言": "TypeScript（原始泄露）",

"定位": "Claude Code 原始泄露源码存档"

}

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

团队用 Linear 管任务

↓

OpenSwarm 自动分配给多个 Claude Code Agent

↓

Worker 写代码 → Reviewer 审查 → Tester 测试

↓

Discord 实时汇报进度

↓

代码自动合并

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

学习 Agent 架构

↓

基于 claw-code 构建自定义 Agent

↓

接入自己的 LLM（OpenAI/Anthropic/本地）

↓

扩展工具集和工作流

**不适用的场景：**

- ❌ 想要开箱即用的完整产品

- ❌ 只需要简单调用 Claude Code

- ❌ 法律敏感项目（虽然 clean-room 但仍有争议）

---

### 2.3 claude-code-source-code (sanbuphy)

**适合谁用：**