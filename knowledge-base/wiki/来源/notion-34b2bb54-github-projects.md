# fireworks-tech-graph 项目研究报告

## 📌 一句话定位

> **用中文描述系统架构，几秒钟生成 SVG + PNG 技术图** —— Claude Code Skill，专门解决程序员画架构图的痛点

## 📦 核心功能

| 功能 | 说明 |

|------|------|

| **输入** | 中文自然语言描述 |

| **输出** | SVG + PNG（1920px 2x视网膜分辨率）|

| **风格** | 7种视觉风格 |

| **图类型** | 14种UML图 + AI/Agent专属图 |

## 🎨 7种视觉风格

| # | 风格 | 背景 | 适用场景 |

|---|------|------|----------|

| 1 | 扁平图标风 | 白色 | 博客、文档、PPT |

| 2 | 暗黑极客风 | #0f0f1a | GitHub README、开发者文章 |

| 3 | 工程蓝图风 | #0a1628 | 架构设计、工程规范 |

| 4 | Notion极简风 | 白色 | Notion、Wiki |

| 5 | 玻璃态卡片风 | 深色渐变 | 产品官网、Keynote |

| 6 | Claude官方风格 | #f8f6f3 | Anthropic风格 |

| 7 | OpenAI官方风格 | 白色 | OpenAI风格 |

## 📊 支持的图类型

### AI/Agent专属

- RAG Pipeline

- Agentic Search

- Mem0记忆架构

- Multi-Agent协作

- Tool Call流程

- Agent记忆类型（5种）

### UML 14种

类图、组件图、部署图、包图、复合结构图、对象图、用例图、活动图、状态机图、序列图、通信图、时序图、交互概览图、ER图

## 🔧 安装方式

# Claude Code用户

npx skills add yizhiyanhua-ai/fireworks-tech-graph

# 或直接克隆

git clone https://github.com/yizhiyanhua-ai/fireworks-tech-graph.git ~/.claude/skills/

## 📝 触发词

画图 / 帮我画 / 生成图 / 做个图 / 架构图 / 流程图 / 可视化一下 / 出图

## 💡 核心价值

1. **不用手画图** - 中文描述 → 自动生成

2. **AI/Agent领域专属** - 内置RAG、Mem0、Multi-Agent等Pattern

3. **语义形状词汇** - LLM=双边框、Agent=六边形、VectorStore=圆柱

4. **语义箭头系统** - 颜色+虚线编码含义（写入/读取/异步/循环）

## 📊 项目信息

| 项目 | 内容 |

|------|------|

| GitHub | https://github.com/yizhiyanhua-ai/fireworks-tech-graph |

| NPM | https://www.npmjs.com/package/@yizhiyanhua-ai/fireworks-tech-graph |

| Stars | 2.4k |

| License | MIT |

| 语言 | Python + Shell |

## 🎯 与OpenClaw集成

**可以整合的方式：**

1. 安装为OpenClaw Skill

2. 写一个OpenClaw Skill包装器

3. 直接在对话中调用

**适用场景：**

- 知识库架构图生成

- 技术文档自动配图

- 项目汇报可视化

## 📅 研究时间

2026-04-15