#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

from mem0 import Memory

# Milvus 云端配置
os.environ["MILVUS_HOST"] = "8.137.122.11"
os.environ["MILVUS_PORT"] = "19530"

config = {
    "vector_store": {
        "provider": "milvus",
        "config": {
            "collection_name": "CaySon_db",
            "embedding_model": "nomic-embed-text",
            "dimension": 768,
            "index_type": "IVF_FLAT",
            "metric_type": "IP",
            "host": "8.137.122.11",
            "port": 19530
        }
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.2",
            "temperature": 0.0,
            "ollama_base_url": "http://localhost:11434"
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text",
            "ollama_base_url": "http://localhost:11434"
        }
    }
}

def main():
    print("=" * 60)
    print("Mem0 + Milvus 云端向量数据库配置")
    print("=" * 60)
    print(f"\nMilvus 配置:")
    print(f"  HOST: 8.137.122.11")
    print(f"  PORT: 19530")
    print(f"  COLLECTION: CaySon_db")
    print()
    
    try:
        memory = Memory.from_config(config)
        print("[OK] Mem0 初始化成功！")
        
        user_id = "ningcaison"
        
        # 添加记忆
        print("\n[1] 添加记忆...")
        result = memory.add(
            "用户宁采臣是CTO，24年技术老兵，专长AI Agent、RAG、Windows自动化、跨境电商开发",
            user_id=user_id
        )
        print(f"[OK] 记忆添加成功!")
        
        # 获取所有记忆
        print("\n[2] 获取所有记忆...")
        all_memories = memory.get_all(user_id=user_id)
        
        if all_memories:
            results = all_memories.get("results", [])
            print(f"[OK] 共 {len(results)} 条记忆:")
            for i, m in enumerate(results, 1):
                print(f"  {i}. {m.get('memory', '')}")
        else:
            print("[INFO] 没有找到记忆")
        
        print("\n" + "=" * 60)
        print("Milvus 云端存储成功!")
        print("=" * 60)
        
    except Exception as e:
        print(f"[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
