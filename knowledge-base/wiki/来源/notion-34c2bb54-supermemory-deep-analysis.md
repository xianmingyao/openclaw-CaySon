# Supermemory 深度分析报告

> 项目：supermemoryai/supermemory

> Stars：20,307

> 克隆时间：2026-03-30

> 来源：GitHub + 源码分析

---

## 🎯 这是什么

**Supermemory = AI 时代的记忆和上下文引擎**

> "State-of-the-art memory and context engine for AI"

> — **#1 on LongMemEval, LoCoMo, and ConvoMem** 三大基准测试

### 核心定位

┌─────────────────────────────────────────────────────────────┐

│                    AI Agent (健忘症患者)                       │

│                    ❌ 每次对话都是新开始                        │

├─────────────────────────────────────────────────────────────┤

│                                                             │

│   ┌─────────────────────────────────────────────────────┐   │

│   │              Supermemory (记忆引擎)                    │   │

│   │  ─────────────────────────────────────────────────  │   │

│   │  🧠 Memory     │  👤 User Profiles  │  🔍 Search   │   │

│   │  事实提取      │  用户画像          │  混合搜索     │   │

│   └─────────────────────────────────────────────────────┘   │

│                                                             │

└─────────────────────────────────────────────────────────────┘

---

## 📝 关键功能点

### 1. 记忆系统 (Memory)

**核心能力：**

- 从对话中提取事实

- 处理时间变化和矛盾

- 自动遗忘过期信息

- 正确的时间提供正确的上下文

**技术实现：**

// packages/memory-graph/src/types.ts

interface MemoryEntry {

id: string

memory: string

content?: string | null

isStatic: boolean           // 静态记忆（永久事实）

isForgotten: boolean        // 遗忘标记

forgetAfter: string | null  // 何时遗忘

forgetReason: string | null // 遗忘原因

version: number             // 版本号

parentMemoryId: string | null  // 父记忆（版本链）

relation?: MemoryRelation    // 关系类型

}

type MemoryRelation = "updates" | "extends" | "derives"

**记忆关系图谱：**

记忆A (v1) ──[updates]──> 记忆A (v2) ──[extends]──> 记忆B

│

└──[derives]──> 记忆C

### 2. 用户画像 (User Profiles)

**核心能力：**

- 静态记忆 = 稳定事实（永久）

- 动态记忆 = 最近活动（临时）

- ~50ms 响应时间

**数据结构：**

// packages/tools/src/tools-shared.ts

interface ProfileWithMemories {

static?: Array<MemoryItem | string>    // 静态记忆

dynamic?: Array<MemoryItem | string>  // 动态记忆

searchResults?: Array<MemoryItem | string>  // 搜索结果

}

### 3. 混合搜索 (Hybrid Search)

**核心能力：**

- RAG（检索增强生成）

- Memory（记忆检索）

- 一次查询，同时返回知识库和个性化上下文

### 4. 连接器 (Connectors)

**支持平台：**

| 连接器 | 功能 |

|--------|------|

| Google Drive | 文档同步 |

| Gmail | 邮件记忆 |

| Notion | 笔记同步 |

| OneDrive | 文件同步 |

| GitHub | 代码/Issue 记忆 |

### 5. 多模态提取器

| 类型 | 方式 |

|------|------|

| PDF | 文本提取 |

| 图片 | OCR 识别 |

| 视频 | 语音转录 |

| 代码 | AST 感知分块 |

---

## ⚡ 怎么使用

### 1. AI SDK（推荐）

import { supermemoryTools } from '@supermemory/ai-sdk'

import { generateText } from 'ai'

import { openai } from '@ai-sdk/openai'

const result = await generateText({

model: openai('gpt-5'),

messages: [{ role: 'user', content: 'What do you remember about me?' }],

tools: {

...supermemoryTools('your-api-key', {

containerTags: ['user-123']

})

}

})

### 2. 记忆工具