#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步本地ChromaDB记忆到云端Milvus
"""
import os
import sys
import time
sys.stdout.reconfigure(encoding='utf-8')

from mem0 import Memory
from pymilvus import MilvusClient
import requests

# ============ 配置 ============
MILVUS_HOST = "8.137.122.11"
MILVUS_PORT = 19530
MILVUS_COLLECTION = "CaySon_db"
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"
LOCAL_CHROMA_PATH = os.path.expanduser("~/.mem0/chroma")
USER_ID = "ningcaison"

def get_embedding(text):
    """使用Ollama获取文本嵌入"""
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBEDDING_MODEL, "prompt": text}
    )
    return response.json()["embedding"]

def init_mem0():
    """初始化Mem0"""
    config = {
        "vector_store": {
            "provider": "chroma",
            "config": {
                "collection_name": "clawdbot_memories",
                "path": LOCAL_CHROMA_PATH
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
    return Memory.from_config(config)

def init_milvus():
    """初始化Milvus客户端"""
    client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}")
    
    # 确保集合存在
    if MILVUS_COLLECTION not in client.list_collections():
        client.create_collection(collection_name=MILVUS_COLLECTION, dimension=768)
        print(f"    [OK] 创建集合 {MILVUS_COLLECTION}")
    
    # 加载集合
    client.load_collection(collection_name=MILVUS_COLLECTION)
    
    return client

def main():
    print("=" * 60)
    print("同步本地记忆到云端Milvus")
    print("=" * 60)
    
    # 初始化
    print("\n[1] 初始化连接...")
    memory_client = init_mem0()
    milvus_client = init_milvus()
    print("    [OK] 初始化完成")
    
    # 获取本地所有记忆
    print("\n[2] 获取本地记忆...")
    local_all = memory_client.get_all(user_id=USER_ID)
    local_results = local_all.get("results", []) if local_all else []
    print(f"    [OK] 本地共 {len(local_results)} 条记忆")
    
    if not local_results:
        print("\n没有本地记忆需要同步")
        return
    
    # 同步到云端
    print("\n[3] 同步到云端Milvus...")
    success_count = 0
    
    for i, m in enumerate(local_results, 1):
        memory_text = m.get("memory", "")
        local_id = m.get("id", "")
        
        if not memory_text:
            continue
        
        try:
            # 获取嵌入向量
            embedding = get_embedding(memory_text)
            
            # 写入云端
            data = [{
                "id": int(time.time() * 1000000) + i,  # 微秒时间戳+序号
                "vector": embedding
            }]
            
            result = milvus_client.insert(
                collection_name=MILVUS_COLLECTION,
                data=data
            )
            
            print(f"    [{i}/{len(local_results)}] [OK] {memory_text[:40]}...")
            success_count += 1
            
        except Exception as e:
            print(f"    [{i}/{len(local_results)}] [ERROR] {memory_text[:40]}... - {e}")
    
    print(f"\n[4] 同步完成!")
    print(f"    成功: {success_count}/{len(local_results)}")
    
    # 验证
    print("\n[5] 验证云端数据...")
    milvus_client.load_collection(collection_name=MILVUS_COLLECTION)
    
    # 搜索测试
    print("\n[6] 搜索测试...")
    test_query = "用户背景"
    query_emb = get_embedding(test_query)
    search_results = milvus_client.search(
        collection_name=MILVUS_COLLECTION,
        data=[query_emb],
        limit=3
    )
    print(f"    [OK] 搜索'{test_query}'找到 {len(search_results[0]) if search_results else 0} 条")
    
    for r in (search_results[0] if search_results else []):
        dist = r.get("distance", 0)
        print(f"      - 距离: {dist:.4f}")
    
    print("\n" + "=" * 60)
    print("同步完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
