#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证 Milvus 记忆上传
"""
from pymilvus import MilvusClient
import requests

MILVUS_HOST = "8.137.122.11"
MILVUS_PORT = 19530
MILVUS_COLLECTION = "CaySon_db"
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"

def search_memories(query, top_k=3):
    client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}")
    client.load_collection(MILVUS_COLLECTION)
    
    # 获取 embedding
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBEDDING_MODEL, "prompt": query},
        timeout=30
    )
    embedding = response.json()["embedding"]
    
    # 搜索
    results = client.search(
        collection_name=MILVUS_COLLECTION,
        data=[embedding],
        limit=top_k,
        output_fields=["text", "user_id"]
    )
    
    return results

def main():
    print("验证云端 Milvus 记忆...")
    print()
    
    queries = [
        ("Skills安装", "2026-04-08 Skills安装"),
        ("Harness Engineering", "驾驭工程"),
        ("下午研究", "2026-04-08 下午研究")
    ]
    
    for name, query in queries:
        print(f"[{name}] 搜索: {query}")
        try:
            results = search_memories(query)
            print(f"  找到 {len(results[0])} 条记忆:")
            for r in results[0]:
                text = r['entity']['text'][:80]
                print(f"    - {text}...")
            print()
        except Exception as e:
            print(f"  错误: {e}")
            print()

if __name__ == "__main__":
    main()
