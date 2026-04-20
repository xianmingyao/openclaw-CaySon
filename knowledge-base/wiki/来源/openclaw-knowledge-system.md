# OpenClaw + Claude Code 个人技术知识库部署

> 2026-04-03 | 来源：抖音@杨大哥 + 实战整合

---

## 一句话

**Atomic Chat做知识库问答 + Claude Code写代码 = 本地AI开发终极组合**

---

## 架构图

```
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
```

---

## 第一部分：Atomic Chat 本地知识库

### 1.1 安装 Atomic Chat

```bash
# 1. 下载地址
https://atomic.chat

# 2. Mac安装
# - 下载 atomic-chat-macos.dmg
# - 双击打开
# - 拖拽到 Applications

# 3. Windows安装
# - 下载 atomic-chat-windows.exe
# - 双击安装即可
```

### 1.2 配置本地知识库

```bash
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
```

### 1.3 知识库问答示例

**Prompt:**
```
请基于我的知识库回答：
OpenClaw的Skills系统是如何工作的？
参考路径：~/knowledge/openclaw/
```

**输出:**
```
根据你的知识库文档，OpenClaw的Skills系统：
1. 每个Skill是一个目录，包含SKILL.md
2. SKILL.md定义了技能的使用方法和触发条件
3. Agent启动时自动扫描skills目录
...
```

---

## 第二部分：Claude Code 项目开发

### 2.1 Claude Code 安装

```bash
# 方式1: 官方安装 (如有)
npm install -g @anthropic-ai/claude-code

# 方式2: 使用OpenClaw内置
# OpenClaw已集成Claude Code能力
```

### 2.2 配置项目AGENTS.md

在项目根目录创建 `AGENTS.md`:

```markdown
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
```

### 2.3 项目开发流程

```bash
# 1. 启动OpenClaw
openclaw start

# 2. Claude Code生成代码
# prompt: "帮我创建一个用户登录组件"

# 3. 知识库验证
# prompt: "请参考知识库中的组件规范，审查这段代码"

# 4. 自动优化
# prompt: "根据项目规范优化这段代码"
```

---

## 第三部分：OpenClaw 集成

### 3.1 OpenClaw Skills 配置

创建知识库Skill:

```markdown
# SKILL.md - knowledge-base

## 描述
访问本地技术知识库，回答问题

## 触发条件
用户问："查一下..."、"知识库..."、"基于我的笔记..."

## 实现
1. 调用Atomic Chat API
2. 传入知识库路径
3. 返回答案

## 示例
用户: "查一下OpenClaw的Skills怎么写"
Agent: 调用knowledge-skill返回结果
```

### 3.2 OpenClaw 多渠道配置

```bash
# 配置微信渠道
openclaw channels enable weixin

# 配置Telegram渠道
openclaw channels enable telegram

# 配置终端渠道
openclaw channels enable terminal
```

---

## 第四部分：演示案例

### 场景: 开发一个RAG系统

```bash
# Step 1: 知识库准备
# 创建 ~/knowledge/rag/ 目录
# 放入:
#   - RAG原理.md
#   - 向量数据库对比.md
#   - LangChain使用教程.md

# Step 2: Atomic Chat知识库问答
prompt:
"""
我需要开发一个RAG系统，请基于我的知识库：
1. 推荐合适的向量数据库
2. 给出LangChain的关键代码
3. 列出常见的坑
"""

# Step 3: Claude Code生成代码
prompt:
"""
根据知识库中的RAG最佳实践，
帮我生成一个基于Milvus的RAG示例代码，
要求:
- 使用LangChain
- 支持PDF文档导入
- 返回带引用的答案
"""

# Step 4: OpenClaw Skills自动化
# 创建rag-builder skill，自动执行完整流程
```

### 代码示例: RAG + OpenClaw

```python
# rag_with_openclaw.py
import os
from pathlib import Path
from langchain.document_loaders import PDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Milvus

# 1. 加载知识库文档
knowledge_path = Path("~/knowledge/rag")
docs = []
for pdf in knowledge_path.glob("*.pdf"):
    loader = PDFLoader(str(pdf))
    docs.extend(loader.load())

# 2. 分割文档
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# 3. 向量化
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = Milvus.from_documents(chunks, embeddings, connection_args={"host": "8.137.122.11", "port": "19530"})

# 4. OpenClaw Skill调用
def rag_query(question: str) -> str:
    docs = vectorstore.similarity_search(question, k=3)
    context = "\n".join([doc.page_content for doc in docs])
    # 调用LLM生成答案（可用Claude/ChatGPT）
    return f"基于知识库的回答:\n{context}\n\n参考文档: {[doc.metadata['source'] for doc in docs]}"
```

---

## 第五部分：避坑指南

| 坑 | 问题 | 解决 |
|----|------|------|
| 内存不足 | MacBook Air跑不动 | 关闭其他应用，或用9B模型 |
| 知识库乱 | 文档格式不统一 | 统一用Markdown格式 |
| 索引慢 | PDF太多 | 先用Atomic Chat处理 |
| Claude Code超时 | 代码生成太久 | 分步骤执行 |
| 向量检索不准 | Embedding模型差 | 用BGE-large-zh |

---

## 工具选择总结

| 场景 | 工具 | 原因 |
|------|------|------|
| 本地知识库问答 | Atomic Chat | TurboQuant加速，5万上下文 |
| 代码生成/重构 | Claude Code | 最强代码LLM |
| 统一调度 | OpenClaw | 多渠道、多Agent |
| 向量存储 | Milvus | 云端，高可用 |
| 文档处理 | LangChain | 成熟生态 |

---

## 记住这个工作流

```
1. Atomic Chat → 知识库问答（规划）
2. Claude Code → 生成代码（执行）
3. OpenClaw → 统一调度（集成）
4. Milvus → 向量存储（检索）
```

---

## 文档

- `knowledge/atomic-chat.md` - Atomic Chat使用指南
- `knowledge/openclaw-knowledge-system.md` - 本文档
