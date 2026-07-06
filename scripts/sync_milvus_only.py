#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速同步到Milvus"""
import os
import sys
import time
import requests
sys.stdout.reconfigure(encoding='utf-8')

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

from pymilvus import MilvusClient
milvus_client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}")
try:
    milvus_client.load_collection(MILVUS_COLLECTION)
    print("[OK] Milvus connected")
except Exception as e:
    print(f"[WARN] Milvus: {e}")

def get_embedding(text):
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBEDDING_MODEL, "prompt": text[:8000]},
        timeout=60
    )
    return response.json()["embedding"]

print(f"Syncing {len(FILES_TO_SYNC)} files to Milvus...")

total = 0
for filename in FILES_TO_SYNC:
    filepath = os.path.join(KB_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[SKIP] {filename} not found")
        continue
    
    print(f"\nFile: {filename}")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sections = content.split('\n## ')
    print(f"  {len(sections)} sections")
    
    for i, section in enumerate(sections):
        text = section.strip() if i == 0 else "## " + section.strip()
        if not text or len(text) < 30:
            continue
        
        try:
            emb = get_embedding(text)
            milvus_id = int(str(int(time.time() * 1000)) + str(i)[-4:])
            milvus_client.insert(
                collection_name=MILVUS_COLLECTION,
                data=[{
                    "id": milvus_id,
                    "vector": emb,
                    "text": text[:4000],  # 留点余量
                    "user_id": USER_ID
                }]
            )
            total += 1
            if total % 10 == 0:
                print(f"  ... {total} synced")
        except Exception as e:
            print(f"  [ERROR] {str(e)[:60]}")

print(f"\n[DONE] {total} sections synced to Milvus")
