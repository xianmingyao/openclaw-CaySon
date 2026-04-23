# Mem0 云端配置指南（Milvus + 双重写入）

## 🎯 架构概述

```
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
```

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

```python
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
```

---

## 🔄 双重写入脚本

### 1. 搜索脚本（优先 Milvus）

```python
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
        search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}
        results = collection.search(
            data=[query_vector],
            anns_field="vector",
            param=search_params,
            limit=5,
            output_fields=["text", "user_id"]
        )
        
        print("=== Milvus 搜索结果 ===")
        for hits in results:
            for hit in hits:
                print(f"- {hit.entity.get('text', 'N/A')}")
        
        connections.disconnect("default")
        return
        
    except Exception as e:
        print(f"Milvus 连接失败: {e}")
        print("降级到本地 ChromaDB...")
        
        # 降级到 ChromaDB
        try:
            import chromadb
            from chromadb.config import Settings
            
            client = chromadb.Client(Settings(
                persist_directory=os.path.expanduser("~/.mem0/chroma")
            ))
            collection = client.get_collection("clawdbot_memories")
            
            results = collection.query(
                query_texts=[query],
                n_results=5
            )
            
            print("=== ChromaDB 搜索结果 ===")
            for i, doc in enumerate(results['documents'][0]):
                print(f"- {doc}")
                
        except Exception as e2:
            print(f"ChromaDB 也失败: {e2}")

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "用户背景"
    search_memory(query)
```

### 2. 写入脚本（双写）

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双重记忆写入脚本
同时写入 Milvus 云端 + ChromaDB 本地
"""
import os
from datetime import datetime

# 配置
MILVUS_HOST = "8.137.122.11"
MILVUS_PORT = "19530"
CHROMA_PATH = os.path.expanduser("~/.mem0/chroma")

def dual_write(text, user_id="cayson", metadata=None):
    """
    双重写入记忆
    """
    success_count = 0
    
    # 1. 写入 Milvus
    try:
        from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
        
        connections.connect(host=MILVUS_HOST, port=MILVUS_PORT, alias="default")
        
        # 创建或获取集合
        if utility.has_collection("CaySon_db"):
            collection = Collection("CaySon_db")
        else:
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=768),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2000),
                FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=100),
                FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=50),
            ]
            schema = CollectionSchema(fields=fields, description="CaySon Memory")
            collection = Collection("CaySon_db", schema)
            
            # 创建索引
            index_params = {"metric_type": "COSINE", "index_type": "IVF_FLAT"}
            collection.create_index(field_name="vector", index_params=index_params)
        
        # 获取 embedding
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        vector = model.encode([text])[0].tolist()
        
        # 插入
        import time
        collection.insert([[{
            "vector": vector,
            "text": text,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
        }]])
        
        collection.flush()
        connections.disconnect("default")
        print(f"[Milvus] 写入成功")
        success_count += 1
        
    except Exception as e:
        print(f"[Milvus] 写入失败: {e}")
    
    # 2. 写入 ChromaDB
    try:
        import chromadb
        from chromadb.config import Settings
        
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_or_create_collection(user_id)
        
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
        vector = model.encode([text])[0].tolist()
        
        collection.add(
            documents=[text],
            embeddings=[vector],
            metadatas=[{"source": "dual_write", "timestamp": datetime.now().isoformat()}],
            ids=[f"{user_id}_{int(time.time())}"]
        )
        
        print(f"[ChromaDB] 写入成功")
        success_count += 1
        
    except Exception as e:
        print(f"[ChromaDB] 写入失败: {e}")
    
    print(f"写入完成: {success_count}/2 个存储成功")
    return success_count > 0

if __name__ == "__main__":
    import sys
    text = sys.argv[1] if len(sys.argv) > 1 else "测试记忆"
    dual_write(text)
```

---

## 📝 检索命令汇总

### 优先 Milvus 检索

```bash
# 主检索脚本（优先 Milvus）
python E:\workspace\scripts\mem0_dual_write.py search "查询内容"

# 仅本地检索
python E:\workspace\scripts\show_memories.py
```

### 同步脚本

```bash
# 同步本地到云端
python E:\workspace\scripts\sync_memories_to_milvus.py
```

---

## 📊 存储层对比

| 存储 | 位置 | 优势 | 劣势 |
|------|------|------|------|
| **Milvus** | 云端 8.137.122.11 | 快速、跨设备 | 需要网络 |
| **ChromaDB** | 本地 ~/.mem0/ | 离线可用 | 单设备 |
| **文件** | memory/YYYY-MM-DD.md | 永久、可追溯 | 不支持语义搜索 |

---

## 🔧 维护命令

### 检查连接状态

```bash
# 测试 Milvus 连接
python -c "
from pymilvus import connections
connections.connect(host='8.137.122.11', port='19530', alias='default')
print('Milvus 连接成功!')
connections.disconnect('default')
"

# 测试 ChromaDB
python -c "
import chromadb
client = chromadb.Client()
print('ChromaDB 连接成功!')
"
```

### 清理过期数据

```bash
# 清理 30 天前的 ChromaDB 数据
python -c "
import chromadb
from datetime import datetime, timedelta

client = chromadb.PersistentClient(path='~/.mem0/chroma')
# 查看所有集合
print(client.list_collections())
"
```

---

## 📋 配置文件路径

| 配置文件 | 路径 |
|---------|------|
| 双写脚本 | `E:\workspace\scripts\mem0_dual_write.py` |
| 同步脚本 | `E:\workspace\scripts\sync_memories_to_milvus.py` |
| Milvus 数据 | 8.137.122.11:19530 (云端) |
| ChromaDB 数据 | `~/.mem0/chroma/` |
| 记忆日志 | `E:\workspace\memory\` |

---

## ✅ 验证步骤

1. **测试 Milvus 连接**
   ```bash
   python -c "from pymilvus import connections; connections.connect(host='8.137.122.11', port='19530'); print('OK')"
   ```

2. **测试双重写入**
   ```bash
   python E:\workspace\scripts\mem0_dual_write.py write "测试记忆"
   ```

3. **测试双重检索**
   ```bash
   python E:\workspace\scripts\mem0_dual_write.py search "测试"
   ```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pymilvus chromadb sentence-transformers mem0ai
```

### 2. 配置环境变量

```bash
export MILVUS_HOST="8.137.122.11"
export MILVUS_PORT="19530"
```

### 3. 开始使用

```python
from mem0 import Memory

memory = Memory.from_config({
    "vector_store": {
        "provider": "milvus",
        "config": {
            "host": "8.137.122.11",
            "port": "19530",
            "collection_name": "CaySon_db",
            "embedding_model_dims": 768,
        }
    }
})

# 添加记忆
memory.add("用户宁采臣是CTO，24年经验", user_id="cayson")

# 搜索记忆
results = memory.search("用户的背景是什么", user_id="cayson")
```

