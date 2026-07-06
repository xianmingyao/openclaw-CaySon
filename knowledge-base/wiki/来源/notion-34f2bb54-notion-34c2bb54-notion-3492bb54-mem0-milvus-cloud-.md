# Mem0 云端配置指南（Milvus + 双重写入）

## 🎯 架构概述

┌─────────────────────────────────────────────────────────────┐

│                      记忆系统双重架构                          │

├─────────────────────────────────────────────────────────────┤

│                                                             │

│   AI Agent ──▶ 写入 ──▶ ┌─────────┐                       │

│                         │ 双写脚本 │                        │

│                         └────┬────┘                        │

│                              │                              │

│              ┌───────────────┼───────────────┐              │

│              ▼               ▼               ▼              │

│        ┌─────────┐   ┌───────────┐   ┌─────────┐          │

│        │ Milvus  │   │ ChromaDB  │   │  文件   │          │

│        │ (云端)  │   │  (本地)   │   │ memory/ │          │

│        │ 8.137. │   │ ~/.mem0/  │   │ MEMORY  │          │

│        └─────────┘   └───────────┘   └─────────┘          │

│                                                             │

└─────────────────────────────────────────────────────────────┘

---

## ☁️ 云端 Milvus 配置

### 服务信息

| 配置项 | 值 |

|--------|-----|

| **地址** | 8.137.122.11:19530 |

| **集合名** | CaySon_db |

| **维度** | 768 |

| **Embedding模型** | nomic-embed-text |

| **协议** | HTTP |

### Python 配置

#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

Mem0 云端 Milvus 配置

"""

import os

# Milvus 云端配置

MILVUS_HOST = "8.137.122.11"

MILVUS_PORT = "19530"

COLLECTION_NAME = "CaySon_db"

EMBEDDING_DIM = 768

EMBEDDING_MODEL = "nomic-embed-text"

# 可选：本地 ChromaDB 备份

CHROMA_PATH = os.path.expanduser("~/.mem0/chroma")

# Mem0 配置

mem0_config = {

"vector_store": {

"provider": "milvus",

"config": {

"host": MILVUS_HOST,

"port": MILVUS_PORT,

"collection_name": COLLECTION_NAME,

"embedding_model_dims": EMBEDDING_DIM,

}

},

"embedder": {

"provider": "huggingface",

"config": {

"model": "sentence-transformers/paraphrase-MiniLM-L6-v2",

"embedding_dims": EMBEDDING_DIM,

}

},

"llm": {

"provider": "openai",

"config": {

"model": "gpt-4o-mini",

"temperature": 0.0,

}

}

}

---

## 🔄 双重写入脚本

### 1. 搜索脚本（优先 Milvus）

#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

双重记忆搜索脚本

优先使用 Milvus 云端，失败时降级到本地 ChromaDB

"""

import os

import sys

def search_memory(query):

"""

搜索记忆，优先 Milvus，降级到 ChromaDB

"""

try:

# 优先尝试 Milvus 云端

from pymilvus import connections, Collection

connections.connect(

host="8.137.122.11",

port="19530",

alias="default"

)

collection = Collection("CaySon_db")

collection.load()

# 获取 embedding

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

query_vector = model.encode([query])[0].tolist()

# 搜索