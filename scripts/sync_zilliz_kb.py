#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
同步Zilliz知识库到Mem0(ChromaDB) + Milvus
修复版：使用正确的字段名和维度
"""
import os
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

# Read the knowledge base content
kb_path = 'E:/workspace/knowledge-base/wiki/概念/Zilliz-Cloud企业知识库完整指南.md'
with open(kb_path, 'r', encoding='utf-8') as f:
    kb_content = f.read()

print(f"读取文件: {kb_path}")
print(f"文件长度: {len(kb_content)} 字符")

# Split content into meaningful chunks for memory
# Each section starting with ## is a good chunk
sections = kb_content.split('\n## ')

print(f"Found {len(sections)} sections to sync")

# Initialize clients
from mem0 import Memory
from pymilvus import MilvusClient

# Milvus config
MILVUS_HOST = "8.137.122.11"
MILVUS_PORT = 19530
MILVUS_COLLECTION = "CaySon_db"

# Ollama config
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"
USER_ID = "ningcaison"

# Init Mem0
config = {
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "clawdbot_memories",
            "path": os.path.expanduser("~/.mem0/chroma")
        }
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.2",
            "temperature": 0.0,
            "ollama_base_url": OLLAMA_URL
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": EMBEDDING_MODEL,
            "ollama_base_url": OLLAMA_URL
        }
    }
}

memory_client = Memory.from_config(config)
milvus_client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}")

# Ensure collection is loaded
try:
    milvus_client.load_collection(MILVUS_COLLECTION)
    print("Milvus collection loaded")
except Exception as e:
    print(f"Collection load: {e}")

# Get embedding - using nomic-embed-text which outputs 768 dimensions
def get_embedding(text):
    import requests
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBEDDING_MODEL, "prompt": text[:8000]}
    )
    return response.json()["embedding"]

# Sync each section
success_count = 0
error_count = 0

for i, section in enumerate(sections):
    if i == 0:
        # First section (before first ##)
        text = section.strip()
    else:
        text = "## " + section.strip()
    
    if not text or len(text) < 50:
        continue
    
    print(f"\n[Section {i+1}] Syncing: {text[:60]}...")
    
    # 1. Add to Mem0 (ChromaDB)
    try:
        result = memory_client.add(text, user_id=USER_ID)
        print(f"  [OK] Mem0/ChromaDB synced")
    except Exception as e:
        print(f"  [WARN] Mem0: {e}")
    
    # 2. Add to Milvus - 使用正确的字段名
    try:
        emb = get_embedding(text)
        # 生成唯一ID
        milvus_id = int(str(int(time.time() * 1000)) + str(i)[-4:])
        
        milvus_client.insert(
            collection_name=MILVUS_COLLECTION,
            data=[{
                "id": milvus_id,
                "vector": emb,  # 注意：是vector不是embedding
                "text": text[:4096],  # 限制长度
                "user_id": USER_ID
            }]
        )
        print(f"  [OK] Milvus synced (ID: {milvus_id})")
        success_count += 1
    except Exception as e:
        print(f"  [ERROR] Milvus: {e}")
        error_count += 1

print(f"\n\n[Done] Synced {success_count} sections successfully, {error_count} errors")
