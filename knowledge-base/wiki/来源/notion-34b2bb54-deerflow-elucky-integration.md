# DeerFlow 2.0 × ELUCKY 架构融合深度研究报告

## 1. 🎯 DeerFlow 2.0 是什么

**DeerFlow 2.0** 是字节跳动开源的 **SuperAgent Harness**，基于 LangGraph 构建，专门处理长周期、复杂任务的 AI Agent 运行时基础设施。

| 项目 | 信息 |

|------|------|

| **出品方** | 字节跳动（ByteDance） |

| **类型** | SuperAgent Harness |

| **Stars** | 47.3k+ |

| **基于** | LangGraph 1.0 |

| **定位** | 让Agent完成复杂长周期任务 |

## 2. 📝 核心架构

### DeerFlow 2.0 组件

| 组件 | 说明 |

|------|------|

| 🧠 **memory** | 多层次记忆系统 |

| 🔧 **tools** | 扩展工具集 |

| 👥 **subagents** | 子Agent编排 |

| 📦 **sandboxes** | 沙箱隔离执行 |

| 🛠️ **skills** | 可扩展技能系统 |

| 📨 **message gateway** | 消息网关 |

### DeerFlow vs OpenHarness 对比

| 维度 | DeerFlow 2.0 | OpenHarness |

|------|---------------|--------------|

| **出品方** | 字节跳动 | 港大HKUDS |

| **Stars** | 47.3k | 4000+ |

| **基于** | LangGraph | 自研 |

| **定位** | SuperAgent运行时 | 轻量基础设施 |

| **记忆** | 多层次memory | 基础memory |

| **子Agent** | 原生支持 | 需扩展 |

| **沙箱** | 原生sandbox | 需扩展 |

## 3. 🔗 ELUCKY 现状分析

### 当前ELUCKY Agent架构

LangGraph Agent Orchestrator

├── 主控Agent

├── 脚本Agent

├── 视频Agent

├── 质检Agent

├── BrowserAgent

├── NurtureAgent

├── PublishAgent

├── OutreachAgent

├── 风控Agent

└── 调度Agent

**现状痛点：**

- ❌ 子Agent协作靠硬编码

- ❌ 缺少沙箱隔离

- ❌ 记忆系统分散

- ❌ 长周期任务支持弱

## 4. 🏗️ DeerFlow × ELUCKY 融合方案

### 融合后的ELUCKY v2架构

┌─────────────────────────────────────────────────────────────┐

│                    ELUCKY v2.0 架构                        │

├─────────────────────────────────────────────────────────────┤

│                                                             │

│  ┌─────────────────────────────────────────────────────┐  │

│  │              DeerFlow Harness Core                   │  │

│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐            │  │

│  │  │ Memory  │  │ Sandbox │  │ Gateway │            │  │

│  │  │ System  │  │ Manager │  │          │            │  │

│  │  └─────────┘  └─────────┘  └─────────┘            │  │

│  └─────────────────────────────────────────────────────┘  │

│                           │                                │

│                           ▼                                │

│  ┌─────────────────────────────────────────────────────┐  │

│  │              LangGraph Orchestrator                  │  │

│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐            │  │

│  │  │Research │  │  Code   │  │  Create │            │  │

│  │  │ Agent   │  │ Agent   │  │ Agent   │            │  │

│  │  └─────────┘  └─────────┘  └─────────┘            │  │

│  └─────────────────────────────────────────────────────┘  │

│                           │                                │

│                           ▼                                │

│  ┌─────────────────────────────────────────────────────┐  │

│  │              Platform Sub-Agents                       │  │

│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐│  │

│  │  │ TikTok │  │   FB   │  │   IG   │  │   X    ││  │

│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘│  │

│  └─────────────────────────────────────────────────────┘  │

│                                                             │

└─────────────────────────────────────────────────────────────┘

### 具体融合点

#### 4.1 记忆系统融合

**当前问题：** ELUCKY的记忆分散在各个Agent

**DeerFlow方案：**

# 统一记忆层

class ELUCKYMemory:

"""多层次记忆：短期→长期→向量"""

# 1. 短期记忆：当前任务上下文

short_term: ConversationBufferMemory

# 2. 长期记忆：账号配置、历史操作

long_term: PostgreSQL + Redis

# 3. 向量记忆：知识库检索

vector_memory: ChromaDB/Milvus

# 4. 技能记忆：OpenSpace进化沉淀

skill_memory: OpenSpace Skill Store

#### 4.2 子Agent协作融合

**当前问题：** Agent间协作靠主控Agent硬编排

**DeerFlow方案：**

# DeerFlow风格的子Agent定义

sub_agents = {