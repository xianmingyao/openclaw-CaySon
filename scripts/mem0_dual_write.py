#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mem0 双写配置：本地ChromaDB + 云端Milvus
每次添加记忆时同时写入两个数据库
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

from mem0 import Memory
from pymilvus import MilvusClient
import hashlib

# ============ 配置 ============

# Milvus 云端配置
MILVUS_HOST = "8.137.122.11"
MILVUS_PORT = 19530
MILVUS_COLLECTION = "CaySon_db"

# Ollama 本地配置
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.2"

# 本地 ChromaDB 配置
LOCAL_CHROMA_PATH = os.path.expanduser("~/.mem0/chroma")

# 用户ID
USER_ID = "ningcaison"

# ============ 初始化 ============

def init_mem0():
    """初始化Mem0（用于记忆提取）"""
    # 强制禁用 OpenAI API Key（防止 mem0  fallback 到 OpenAI）
    import os
    os.environ.pop("OPENAI_API_KEY", None)
    os.environ.pop("OPENAI_API_KEY", None)  # 确保从当前进程删除
    
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
                "model": LLM_MODEL,
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
    return MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}")

def ensure_collection_loaded(milvus_client):
    """确保 collection 已加载，必要时自动加载"""
    try:
        milvus_client.load_collection(MILVUS_COLLECTION)
    except Exception:
        pass  # 已加载或无权限，忽略

def get_embedding(text):
    """使用Ollama获取文本嵌入"""
    import requests
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={"model": EMBEDDING_MODEL, "prompt": text}
    )
    return response.json()["embedding"]

# ============ 操作函数 ============

def add_memory(memory_client, milvus_client, text, metadata=None):
    """添加记忆到两个数据库"""
    
    print(f"\n[1] 添加记忆: {text}")
    
    # 1. 写入本地ChromaDB（通过Mem0）
    print("[2] 写入本地ChromaDB...")
    try:
        result = memory_client.add(text, user_id=USER_ID)
        print(f"    [OK] 本地写入成功")
        local_id = result.get('id', '')
    except Exception as e:
        print(f"    [ERROR] 本地写入失败: {e}")
        local_id = None
    
    # 2. 获取嵌入向量
    print("[3] 生成嵌入向量...")
    try:
        embedding = get_embedding(text)
        print(f"    [OK] 嵌入维度: {len(embedding)}")
    except Exception as e:
        print(f"    [ERROR] 嵌入生成失败: {e}")
        return None
    
    # 3. 写入云端Milvus
    print("[4] 写入云端Milvus...")
    ensure_collection_loaded(milvus_client)
    try:
        import time
        milvus_id = int(str(int(time.time() * 1000)) + str(local_id if local_id else '0')[-4:])
        data = [
            {
                "id": milvus_id,
                "vector": embedding,
                "text": text,
                "user_id": USER_ID,
            }
        ]
        result = milvus_client.insert(
            collection_name=MILVUS_COLLECTION,
            data=data
        )
        print(f"    [OK] 云端写入成功 (ID: {milvus_id})")
    except Exception as e:
        print(f"    [ERROR] 云端写入失败: {e}")
    
    print("\n[OK] 双写完成!")
    return local_id

def search_memories(memory_client, milvus_client, query, limit=10):
    """从两个数据库搜索记忆并合并"""
    
    print(f"\n[搜索] 查询: {query}")
    
    # 1. 从本地搜索
    print("[1] 本地ChromaDB搜索...")
    try:
        local_results_raw = memory_client.search(query, user_id=USER_ID, limit=limit)
        # search 返回 dict{'results': [...]}，需要取 ['results']
        local_results = local_results_raw.get('results', []) if isinstance(local_results_raw, dict) else local_results_raw
        print(f"    [OK] 找到 {len(local_results)} 条")
    except Exception as e:
        print(f"    [ERROR] 本地搜索失败: {e}")
        local_results = []
    
    # 2. 从云端搜索
    print("[2] 云端Milvus搜索...")
    ensure_collection_loaded(milvus_client)
    try:
        query_embedding = get_embedding(query)
        milvus_results = milvus_client.search(
            collection_name=MILVUS_COLLECTION,
            data=[query_embedding],
            filter=f'u200b user_id == "{USER_ID}"' if False else None,
            limit=limit
        )
        print(f"    [OK] 找到 {len(milvus_results)} 条")
    except Exception as e:
        print(f"    [ERROR] 云端搜索失败: {e}")
        milvus_results = []
    
    # 3. 合并结果
    print("\n[合并结果]")
    all_results = []
    
    # 添加本地结果
    for r in local_results:
        if isinstance(r, dict):
            all_results.append({
                "source": "local",
                "text": r.get("memory", ""),
                "score": r.get("score", 0)
            })
    
    # 添加云端结果
    for r in milvus_results:
        if isinstance(r, list) and len(r) > 0:
            for item in r:
                all_results.append({
                    "source": "milvus",
                    "text": item.get("entity", {}).get("text", ""),
                    "score": item.get("distance", 0)
                })
    
    # 去重（根据文本内容）
    seen = set()
    unique_results = []
    for r in all_results:
        text = r["text"]
        if text and text not in seen:
            seen.add(text)
            unique_results.append(r)
    
    print(f"\n[OK] 共 {len(unique_results)} 条不重复结果:\n")
    for i, r in enumerate(unique_results, 1):
        print(f"  {i}. [{r['source']}] {r['text'][:60]}...")
    
    return unique_results

def get_all_memories(memory_client, milvus_client):
    """获取所有记忆"""
    
    print("\n[获取所有记忆]")
    
    # 从本地获取
    print("[1] 本地ChromaDB...")
    try:
        local_all = memory_client.get_all(user_id=USER_ID)
        # get_all 返回 dict{'results': [...]} 或 list
        local_results = local_all.get("results", []) if isinstance(local_all, dict) else (local_all if isinstance(local_all, list) else [])
        print(f"    [OK] {len(local_results)} 条")
    except Exception as e:
        print(f"    [ERROR] {e}")
        local_results = []
    
    # 从云端获取
    print("[2] 云端Milvus...")
    ensure_collection_loaded(milvus_client)
    try:
        milvus_all = milvus_client.query(
            collection_name=MILVUS_COLLECTION,
            filter=f'u200b user_id == "{USER_ID}"' if False else None,
            limit=100
        )
        print(f"    [OK] {len(milvus_all)} 条")
    except Exception as e:
        print(f"    [ERROR] {e}")
        milvus_all = []
    
    return local_results, milvus_all

# ============ 主函数 ============

def main():
    print("=" * 60)
    print("Mem0 双写配置：本地ChromaDB + 云端Milvus")
    print("=" * 60)
    print(f"\nMilvus: {MILVUS_HOST}:{MILVUS_PORT}/{MILVUS_COLLECTION}")
    print(f"Ollama: {OLLAMA_URL}")
    print(f"用户ID: {USER_ID}")
    
    try:
        # 初始化
        print("\n[初始化中...]")
        memory_client = init_mem0()
        milvus_client = init_milvus()
        print("[OK] 初始化成功!")
        
        # 根据参数执行不同操作
        if len(sys.argv) > 1:
            action = sys.argv[1]
            
            if action == "add":
                # 添加记忆
                if len(sys.argv) > 2:
                    text = " ".join(sys.argv[2:])
                    add_memory(memory_client, milvus_client, text)
                else:
                    print("\n用法: python mem0_dual_write.py add <记忆内容>")
            
            elif action == "search":
                # 搜索记忆
                if len(sys.argv) > 2:
                    query = " ".join(sys.argv[2:])
                    search_memories(memory_client, milvus_client, query)
                else:
                    print("\n用法: python mem0_dual_write.py search <查询内容>")
            
            elif action == "list":
                # 列出所有记忆
                local, milvus = get_all_memories(memory_client, milvus_client)
                print(f"\n[总计] 本地 {len(local)} + 云端 {len(milvus)} = {len(local) + len(milvus)} 条")
            
            else:
                print(f"\n未知操作: {action}")
                print("用法: python mem0_dual_write.py [add|search|list]")
        else:
            # 默认：显示帮助
            print("\n用法:")
            print("  python mem0_dual_write.py add <记忆内容>   # 添加记忆")
            print("  python mem0_dual_write.py search <查询>    # 搜索记忆")
            print("  python mem0_dual_write.py list            # 列出所有记忆")
        
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
