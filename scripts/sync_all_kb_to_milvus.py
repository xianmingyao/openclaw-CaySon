#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""完整同步知识库到Milvus"""
import os
import sys
import time
import requests
sys.stdout.reconfigure(encoding='utf-8')

USER_ID = "ningcaison"
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"
MILVUS_HOST = "8.137.122.11"
MILVUS_PORT = 19530
MILVUS_COLLECTION = "CaySon_db"

from pymilvus import MilvusClient

print("=" * 60)
print("知识库 → Milvus 完整同步")
print("=" * 60)

# 连接Milvus
print("\n[1] 连接Milvus...")
milvus_client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}")
try:
    milvus_client.load_collection(MILVUS_COLLECTION)
    print("    [OK] Milvus已连接")
except Exception as e:
    print(f"    [WARN] {e}")

def get_emb(text):
    resp = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBEDDING_MODEL, "prompt": text[:8000]},
        timeout=60
    )
    return resp.json()["embedding"]

# 遍历知识库所有md文件
KB_DIRS = [
    'E:/workspace/knowledge-base/wiki/概念',
    'E:/workspace/knowledge-base/wiki/来源',
    'E:/workspace/knowledge-base/wiki/实体',
]

print("\n[2] 扫描知识库文件...")
all_files = []
for kb_dir in KB_DIRS:
    if os.path.exists(kb_dir):
        for root, dirs, files in os.walk(kb_dir):
            for f in files:
                if f.endswith('.md'):
                    all_files.append(os.path.join(root, f))

print(f"    找到 {len(all_files)} 个Markdown文件")

total_synced = 0
total_errors = 0

print("\n[3] 开始同步...")
for i, filepath in enumerate(all_files, 1):
    filename = os.path.basename(filepath)
    print(f"\n[{i}/{len(all_files)}] {filename}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 按##分段
        sections = content.split('\n## ')
        print(f"    {len(sections)} 个章节")
        
        for j, section in enumerate(sections):
            if j == 0:
                text = section.strip()
            else:
                text = "## " + section.strip()
            
            if not text or len(text) < 30:
                continue
            
            try:
                emb = get_emb(text)
                mid = int(str(int(time.time() * 1000000)) + str(j)[-4:])
                milvus_client.insert(
                    collection_name=MILVUS_COLLECTION,
                    data=[{
                        "id": mid,
                        "vector": emb,
                        "text": text[:4000],
                        "user_id": USER_ID
                    }]
                )
                total_synced += 1
                if total_synced % 50 == 0:
                    print(f"    ...已同步 {total_synced} 条")
            except Exception as e:
                total_errors += 1
                if total_errors <= 5:
                    print(f"    [ERR] {str(e)[:60]}")
        
    except Exception as e:
        print(f"    [SKIP] {str(e)[:60]}")

print(f"\n{'='*60}")
print(f"同步完成！")
print(f"成功: {total_synced} 条")
print(f"失败: {total_errors} 条")
print("=" * 60)
