#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速同步知识库到Milvus - 简化版"""
import os
import sys
import time
import requests
sys.stdout.reconfigure(encoding='utf-8')

KB_DIR = 'E:/workspace/knowledge-base/wiki/概念'
FILES = [
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

from pymilvus import MilvusClient
print("[1] Connecting to Milvus...")
milvus_client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}")
try:
    milvus_client.load_collection(MILVUS_COLLECTION)
    print("[OK] Milvus connected and loaded")
except Exception as e:
    print(f"[WARN] {e}")

def get_emb(text):
    resp = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBEDDING_MODEL, "prompt": text[:8000]},
        timeout=60
    )
    return resp.json()["embedding"]

print(f"\n[2] Syncing {len(FILES)} files...")
total = 0

for filename in FILES:
    filepath = os.path.join(KB_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[SKIP] {filename}")
        continue
    
    print(f"\nFile: {filename}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by ## headers
    parts = content.split('\n## ')
    print(f"  {len(parts)} parts")
    
    for i, part in enumerate(parts):
        if i == 0:
            text = part.strip()
        else:
            text = "## " + part.strip()
        
        if not text or len(text) < 30:
            continue
        
        # Truncate text to fit 4000 char limit
        text = text[:4000]
        
        try:
            emb = get_emb(text)
            mid = int(str(int(time.time() * 1000))[-6:] + str(i)[-2:])
            milvus_client.insert(
                collection_name=MILVUS_COLLECTION,
                data=[{
                    "id": mid,
                    "vector": emb,
                    "text": text,
                    "user_id": USER_ID
                }]
            )
            total += 1
            if total % 20 == 0:
                print(f"  ... {total} synced")
        except Exception as e:
            err = str(e)[:80]
            print(f"  [ERR] {err}")

print(f"\n[DONE] {total} records synced to Milvus")
