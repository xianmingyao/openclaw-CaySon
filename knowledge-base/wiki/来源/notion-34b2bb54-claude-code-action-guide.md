# claude-code-action 使用指南

> 来源：程序员Sunday 第57集

> 整理时间：2026-03-28

---

## 🎯 这是什么

✅ **claude-code-action** 是将 Claude Code 集成到 GitHub Actions CI/CD 工作流的官方 Action

**核心数据：**

- Star：6.5k

- Fork：1.6k

- Releases：140个版本

- Deployments：600+次部署

- 最新版本：Claude Code 2.1.81 / Agent SDK 0.2.81

---

## 📝 关键功能点

### 1. 核心能力

• 将 Claude AI 编码能力集成到 GitHub 工作流

• 自动分析 Pull Request

• 代码审查与 Bug 修复

• 根据指令重构代码

• 利用 Agent SDK 以代理身份执行复杂开发任务

### 2. 源码结构

┌─ 项目结构 ─────────────────────────────────┐

│ .claude          - Claude 配置文件          │

│ .github          - GitHub 工作流定义         │

│ base-action      - 核心逻辑代码              │

│ docs             - 文档                     │

│ examples         - 使用示例                  │

│ scripts          - 脚本工具                  │

│ src              - 源代码                   │

│ test             - 测试套件                  │

│ CLAUDE.md        - Claude 指令规范          │

└────────────────────────────────────────────┘

### 3. 工作流集成方式

# .github/workflows/claude.yml

name: Claude Code Review

on: [pull_request]

jobs:

review:

runs-on: ubuntu-latest

steps:

- uses: actions/checkout@v4

- uses: anthropic/claude-code-action@v1

with:

# 你的 Claude API Key

---

## ⚡ 怎么使用

### 第一步：安装配置

1. 在 GitHub 仓库中创建 .github/workflows/ 目录

2. 创建 yml 配置文件

3. 在仓库 Settings > Secrets 中添加 ANTHROPIC_API_KEY

4. 提交代码触发 workflow

### 第二步：编写工作流

• 指定触发条件（pull_request / push / issue）

• 配置 Claude 指令（CLAUDE.md 或 inline）

• 设置输出格式（comment / review）

### 第三步：运行验证

• 查看 Actions 日志

• 检查 Claude 的 PR 评论

• 根据反馈调整指令

---

## ✅ 优点

• 官方出品，稳定性高（140个版本迭代）

• 深度集成 GitHub 生态

• 支持 PR 自动审查

• Agent SDK 支持复杂任务执行

• 部署规模大（600+生产环境验证）

• 持续更新（2天前刚更新到 Claude Code 2.1.81）

---

## ❌ 缺点

• 需要配置 Claude API Key，有成本

• 国内访问 GitHub Actions 可能受限

• 配置有一定学习成本

• 需要编写 CLAUDE.md 提示词

• Agent SDK 版本需要同步更新

---

## 🎬 使用场景

• PR 代码审查自动化

• Bug 自动修复

• 代码重构建议

• 文档自动生成

• 测试用例编写

• CI/CD 质量门禁

---

## 🔧 运行依赖环境

┌─ 环境要求 ─────────────────────────────────┐

│ 运行时                                 │

│   • GitHub Actions 运行器               │

│   • Ubuntu / Windows / macOS           │

│                                         │

│ 依赖项                                 │

│   • Claude Code 2.1.81+               │

│   • Agent SDK 0.2.81+                  │

│   • Git                                 │

│                                         │

│ 网络要求                                 │

│   • 能访问 Anthropic API               │

│   • GitHub Actions 网络                 │

│                                         │

│ 认证要求                                 │

│   • ANTHROPIC_API_KEY (Secrets)       │