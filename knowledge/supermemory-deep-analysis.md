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

```
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
```

---

## 📝 关键功能点

### 1. 记忆系统 (Memory)

**核心能力：**
- 从对话中提取事实
- 处理时间变化和矛盾
- 自动遗忘过期信息
- 正确的时间提供正确的上下文

**技术实现：**
```typescript
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
```

**记忆关系图谱：**
```
记忆A (v1) ──[updates]──> 记忆A (v2) ──[extends]──> 记忆B
                    │
                    └──[derives]──> 记忆C
```

### 2. 用户画像 (User Profiles)

**核心能力：**
- 静态记忆 = 稳定事实（永久）
- 动态记忆 = 最近活动（临时）
- ~50ms 响应时间

**数据结构：**
```typescript
// packages/tools/src/tools-shared.ts
interface ProfileWithMemories {
    static?: Array<MemoryItem | string>    // 静态记忆
    dynamic?: Array<MemoryItem | string>  // 动态记忆
    searchResults?: Array<MemoryItem | string>  // 搜索结果
}
```

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

```typescript
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
```

### 2. 记忆工具

```typescript
// 搜索记忆
const searchResult = await tools.searchMemories.execute({
    informationToGet: 'user preferences about coffee'
})

// 添加记忆
const addResult = await tools.addMemory.execute({
    memory: 'User prefers dark roast coffee in the morning'
})
```

### 3. 无限上下文聊天

```typescript
const supermemoryOpenai = createOpenAI({
    baseUrl: 'https://api.supermemory.ai/v3/...',
    headers: {
        'x-supermemory-api-key': 'your-key',
        'x-sm-conversation-id': 'conversation-id'
    }
})

const result = await generateText({
    model: supermemoryOpenai('gpt-5'),
    messages: [{ role: 'user', content: 'Hello!' }]
    // 无限上下文自动管理
})
```

---

## ✅ 优点

1. **基准测试第一** - LongMemEval/LoCoMo/ConvoMem 三冠王
2. **完整的记忆系统** - 提取、版本、遗忘全链路
3. **图结构记忆** - 支持记忆关系（updates/extends/derives）
4. **多模态支持** - PDF/图片/视频/代码全支持
5. **连接器生态** - Google/GitHub/Notion 全家桶
6. **SDK 友好** - Vercel AI SDK 一键集成
7. **开源** - MIT 许可证

---

## ❌ 缺点

1. **云端依赖** - 完整功能需要 API Key
2. **自托管复杂** - 完整部署需要数据库 + 向量存储
3. **文档不够详细** - 某些高级功能缺少示例

---

## 🎬 使用场景

| 场景 | 方案 |
|------|------|
| **个人 AI 助手** | Web App + 浏览器扩展 |
| **产品集成** | AI SDK（npm 包） |
| **企业知识库** | 自托管 + 连接器 |
| **代码记忆** | Claude Code / OpenCode 插件 |

---

## 🔧 项目架构

```
supermemory/
├── apps/
│   ├── web/              # Web 应用（消费者版）
│   ├── browser-extension/ # 浏览器扩展
│   ├── mcp/              # MCP 服务器
│   ├── docs/             # 文档站
│   └── memory-graph-playground/  # 图谱可视化
├── packages/
│   ├── lib/              # 核心库（类型/工具）
│   ├── memory-graph/      # 记忆图谱可视化
│   ├── ai-sdk/           # Vercel AI SDK 集成
│   ├── tools/            # 记忆工具（多平台）
│   │   ├── src/
│   │   │   ├── openai/   # OpenAI 中间件
│   │   │   ├── vercel/   # Vercel AI SDK
│   │   │   ├── mastra/   # Mastra 框架
│   │   │   └── shared/   # 共享代码
│   │   └── README.md
│   ├── hooks/            # React Hooks
│   ├── ui/               # UI 组件库
│   └── validation/       # 数据验证
└── skills/               # OpenClaw/Claude Code 插件
```

---

## 🕳️ 避坑指南

| 坑 | 问题 | 解决 |
|-----|------|------|
| **API Key 申请** | 需要注册获取 | https://supermemory.ai 注册 |
| **自托管复杂** | 需要 PostgreSQL + 向量数据库 | 使用云端版本快速验证 |
| **容器标签** | projectId 和 containerTags 二选一 | 不能同时使用 |
| **搜索阈值** | 默认 chunkThreshold=0.6 | 调整阈值控制精度 |
| **遗忘机制** | 遗忘后不删除 | 定期清理 isForgotten=true 的记录 |

---

## 📊 总结

**学习价值：⭐⭐⭐⭐⭐（5星）**

| 维度 | 评分 | 说明 |
|------|------|------|
| 功能完整性 | ⭐⭐⭐⭐⭐ | 记忆/画像/搜索/连接器全覆盖 |
| 架构设计 | ⭐⭐⭐⭐⭐ | 清晰的包结构和类型定义 |
| 工程质量 | ⭐⭐⭐⭐⭐ | 20k stars 验证，代码质量高 |
| 可扩展性 | ⭐⭐⭐⭐⭐ | 多平台 SDK + 连接器生态 |
| 学习价值 | ⭐⭐⭐⭐⭐ | 图谱结构 + 遗忘机制值得研究 |

**推荐指数：⭐⭐⭐⭐⭐（5星，强烈推荐研究）**

---

## 🔗 与现有 Skills 的关系

```
┌─────────────────────────────────────────────────────────────┐
│                    记忆系统生态对比                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Supermemory (20k) ──► 最完整，RAG+Memory+Profile         │
│        │                                                      │
│        ├──► AI SDK ──► Vercel AI SDK 集成                   │
│        ├──► Memory Graph ──► 图谱可视化                      │
│        └──► Connectors ──► Google/GitHub/Notion           │
│                                                             │
│   Mem0 (已安装) ──► 语义搜索 + Milvus/ChromaDB            │
│        │                                                      │
│        └──► 对比：Supermemory 更完整，Mem0 更轻量           │
│                                                             │
│   Self-Improving ──► 自我反思 + 纠正记录                    │
│        │                                                      │
│        └──► 补充：Supermemory 侧重记忆，Self-Improving 侧重反思│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 下一步行动

1. **申请 API Key** - https://supermemory.ai 注册
2. **安装 npm 包** - `npm install @supermemory/ai-sdk`
3. **测试记忆功能** - 集成到现有 Agent
4. **研究图谱可视化** - memory-graph 包
5. **对比 Mem0** - 选择更适合的方案

---

## 📚 参考资料

- GitHub：https://github.com/supermemoryai/supermemory
- 文档：https://supermemory.ai/docs
- 仪表盘：https://console.supermemory.ai
- Discord：https://supermemory.link/discord
