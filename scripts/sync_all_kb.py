#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""完整同步知识库到所有平台"""
import os
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

# ============ 配置 ============
KB_DIR = 'E:/workspace/knowledge-base/wiki/概念'
FILES_TO_SYNC = [
    'Zilliz-Cloud企业知识库完整指南.md',
    '企业AI本体Ontology-从工具到Agent的关键.md',
    'Agent评测方法论-老傅1024.md',
    'Hermes-Agent-7个等级-一蛙AI.md',
    'SenseNova-U1-8B开源信息图模型-赛脖古.md',
]

USER_ID = "ningcaison"
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"
MILVUS_HOST = "8.137.122.11"
MILVUS_PORT = 19530
MILVUS_COLLECTION = "CaySon_db"

# ============ 初始化 ============
print("=" * 60)
print("完整同步知识库到所有平台")
print("=" * 60)

# Init Milvus
from pymilvus import MilvusClient
milvus_client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}")
try:
    milvus_client.load_collection(MILVUS_COLLECTION)
    print("[OK] Milvus connected")
except Exception as e:
    print(f"[WARN] Milvus load: {e}")

# Get embedding function
def get_embedding(text):
    import requests
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBEDDING_MODEL, "prompt": text[:8000]},
        timeout=60
    )
    return response.json()["embedding"]

# Init Mem0
try:
    from mem0 import Memory
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
    print("[OK] Mem0 connected")
    mem0_available = True
except Exception as e:
    print(f"[WARN] Mem0 init failed: {e}")
    mem0_available = False

# ============ 同步函数 ============
def sync_file(filepath):
    """同步单个文件"""
    filename = os.path.basename(filepath)
    print(f"\n{'='*60}")
    print(f"Syncing: {filename}")
    print("=" * 60)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 按##分段
    sections = content.split('\n## ')
    print(f"Found {len(sections)} sections")
    
    total_success = 0
    total_errors = 0
    
    for i, section in enumerate(sections):
        if i == 0:
            text = section.strip()
        else:
            text = "## " + section.strip()
        
        if not text or len(text) < 30:
            continue
        
        preview = text[:50].replace('\n', ' ')
        print(f"\n[{i+1}] {preview}...")
        
        # 1. Sync to Mem0 (ChromaDB)
        if mem0_available:
            try:
                memory_client.add(text, user_id=USER_ID)
                print(f"    [OK] Mem0/ChromaDB")
            except Exception as e:
                print(f"    [WARN] Mem0: {str(e)[:50]}")
        
        # 2. Sync to Milvus
        try:
            emb = get_embedding(text)
            milvus_id = int(str(int(time.time() * 1000)) + str(i)[-4:])
            milvus_client.insert(
                collection_name=MILVUS_COLLECTION,
                data=[{
                    "id": milvus_id,
                    "vector": emb,
                    "text": text[:4096],
                    "user_id": USER_ID
                }]
            )
            print(f"    [OK] Milvus (ID: {milvus_id})")
            total_success += 1
        except Exception as e:
            print(f"    [ERROR] Milvus: {str(e)[:50]}")
            total_errors += 1
    
    return total_success, total_errors

# ============ 执行同步 ============
print(f"\nFiles to sync: {len(FILES_TO_SYNC)}")
for f in FILES_TO_SYNC:
    print(f"  - {f}")

total_success = 0
total_errors = 0

for filename in FILES_TO_SYNC:
    filepath = os.path.join(KB_DIR, filename)
    if os.path.exists(filepath):
        s, e = sync_file(filepath)
        total_success += s
        total_errors += e
    else:
        print(f"\n[WARN] File not found: {filepath}")

print(f"\n{'='*60}")
print(f"SYNC COMPLETE")
print(f"Success: {total_success}, Errors: {total_errors}")
print("=" * 60)
