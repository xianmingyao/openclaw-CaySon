# OpenClaw Context 层 Skills 设计：基于 LangChain 三层学习框架

> 研究日期：2026-04-08

> 理论支撑：LangChain 三层学习框架（Model / Harness / Context）

---

## 1. 🎯 核心理念

### 为什么 Context 层最重要？

| 层级 | 成本 | 速度 | 效果 | OpenClaw 对应 |

|------|------|------|------|--------------|

| Model | 🔴 高 | 🐢 慢 | 上限最高 | 模型选择 |

| Harness | 🟡 中 | 🟡 中 | 中等 | 执行框架 |

| **Context** | 🟢 低 | 🐇 快 | 见效最快 | **Skills + Memory** |

Context 层 = Skills + Memory

↓

"热更新"能力

不改模型、不改代码

直接加个 Skill 就变强

**这就是 OpenClaw Skills 的价值所在！**

---

## 2. 📊 OpenClaw Skills 定位

### OpenClaw Skills 架构

┌─────────────────────────────────────────────────────────┐

│                    OpenClaw Agent                         │

│                                                         │

│  ┌─────────────────────────────────────────────────┐   │

│  │              Context 层（运行时）                 │   │

│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐       │   │

│  │  │ Skills  │  │ Memory  │  │  Tools  │       │   │

│  │  └─────────┘  └─────────┘  └─────────┘       │   │

│  └─────────────────────────────────────────────────┘   │

│                                                         │

│  ┌─────────────────────────────────────────────────┐   │

│  │              Harness 层（执行框架）              │   │

│  │  Prompt / Tool Calling / Workflow / Safety      │   │

│  └─────────────────────────────────────────────────┘   │

│                                                         │

│  ┌─────────────────────────────────────────────────┐   │

│  │              Model 层（模型选择）                 │   │

│  │  MiniMax / Claude / Gemini / GPT                │   │

│  └─────────────────────────────────────────────────┘   │

│                                                         │

└─────────────────────────────────────────────────────────┘

---

## 3. 🔧 Skills 设计原则

### 3.1 Skill 的本质

Skill = Context 层的一种可复用组件

↓

包含：instructions + tools + memory

### 3.2 Skill 结构

skill-name:

name: "技能名称"

description: "简短描述"

version: "1.0.0"

# Context 层配置

instructions:

- "指令1"

- "指令2"

# 工具定义

tools:

- name: "工具1"

description: "工具描述"

command: "执行命令"

# 记忆配置

memory:

type: "vector|file|structured"

path: "路径"

# 触发条件

triggers:

- "关键词1"

- "关键词2"

---

## 4. 📝 Skill 设计模板

### 4.1 基础 Skill 模板

# Skill 名称

## 描述

简短描述这个 Skill 的功能

## 触发条件

- 关键词1

- 关键词2

- 场景描述

## 指令（Instructions）

你是一个 [角色]。当用户要求 [任务] 时，你应该：

1. [步骤1]

2. [步骤2]

3. [步骤3]

## 工具（Tools）

- tool1: [描述]

- tool2: [描述]

## 输出格式

[期望的输出格式]

## 注意事项

- [注意点1]

- [注意点2]

### 4.2 示例：Wiki 编译 Skill

# wiki-compiler

## 描述

将 raw/ 目录下的资料编译成 wiki 知识库

## 触发条件

- "编译知识库"

- "整理 wiki"

- "构建知识体系"