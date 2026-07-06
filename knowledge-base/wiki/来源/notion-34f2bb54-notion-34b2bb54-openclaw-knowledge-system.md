# OpenClaw + Claude Code 个人技术知识库部署

> 2026-04-03 | 来源：抖音@杨大哥 + 实战整合

---

## 一句话

**Atomic Chat做知识库问答 + Claude Code写代码 = 本地AI开发终极组合**

---

## 架构图

个人技术知识库

┌─────────────────────────────────────────┐

│                                         │

│  ┌─────────────┐    ┌────────────────┐ │

│  │ Atomic Chat │    │  Claude Code  │ │

│  │ (TurboQuant)│    │ (代码开发)    │ │

│  │             │    │               │ │

│  │ 本地RAG     │    │ Skills调用    │ │

│  │ 5万上下文   │    │ MCP工具      │ │

│  └──────┬──────┘    └───────┬────────┘ │

│         │                    │          │

│         ↓                    ↓          │

│  ┌─────────────────────────────────────┐ │

│  │       OpenClaw 统一调度            │ │

│  │   (微信/Telegram/终端多渠道)        │ │

│  └─────────────────────────────────────┘ │

│                    ↓                     │

│         ┌──────────────────┐            │

│         │  个人知识库      │            │

│         │  (Markdown笔记)  │            │

│         └──────────────────┘            │

└─────────────────────────────────────────┘

---

## 第一部分：Atomic Chat 本地知识库

### 1.1 安装 Atomic Chat

# 1. 下载地址

https://atomic.chat

# 2. Mac安装

# - 下载 atomic-chat-macos.dmg

# - 双击打开

# - 拖拽到 Applications

# 3. Windows安装

# - 下载 atomic-chat-windows.exe

# - 双击安装即可

### 1.2 配置本地知识库

# 1. 打开 Atomic Chat

# 2. 选择模型

# - Qwen3.5-9B (推荐)

# - 开启 TurboQuant 加速

# 3. 准备知识库文件

# - 路径: ~/knowledge/

# - 格式: Markdown / PDF / TXT / 代码文件

# - 推荐: 技术文档、笔记、项目README

# 4. 导入知识库

# - 把 knowledge/ 文件夹拖入 Atomic Chat

# - 或用 /load 命令加载文件夹

### 1.3 知识库问答示例

**Prompt:**

请基于我的知识库回答：

OpenClaw的Skills系统是如何工作的？

参考路径：~/knowledge/openclaw/

**输出:**

根据你的知识库文档，OpenClaw的Skills系统：

1. 每个Skill是一个目录，包含SKILL.md

2. SKILL.md定义了技能的使用方法和触发条件

3. Agent启动时自动扫描skills目录

...

---

## 第二部分：Claude Code 项目开发

### 2.1 Claude Code 安装

# 方式1: 官方安装 (如有)

npm install -g @anthropic-ai/claude-code

# 方式2: 使用OpenClaw内置

# OpenClaw已集成Claude Code能力

### 2.2 配置项目AGENTS.md

在项目根目录创建 `AGENTS.md`:

# AGENTS.md - 项目配置

## 知识库路径

- 技术文档: `~/knowledge/`

- 项目文档: `./docs/`

- 代码规范: `./STANDARDS.md`

## 可用工具

- Atomic Chat: 本地知识库问答

- Claude Code: 代码生成/重构

- Skills: OpenClaw技能系统

## 代码规范

- 遵循项目STYLE.md

- 使用TypeScript

- 组件放在components/

### 2.3 项目开发流程

# 1. 启动OpenClaw

openclaw start

# 2. Claude Code生成代码

# prompt: "帮我创建一个用户登录组件"

# 3. 知识库验证

# prompt: "请参考知识库中的组件规范，审查这段代码"

# 4. 自动优化

# prompt: "根据项目规范优化这段代码"

---

## 第三部分：OpenClaw 集成

### 3.1 OpenClaw Skills 配置

创建知识库Skill:

# SKILL.md - knowledge-base