#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

from mem0 import Memory

os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

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
        }
    },
    "embedder": {
        "provider": "ollama",
        "config": {
            "model": "nomic-embed-text"
        }
    }
}

def main():
    print("=" * 60)
    print("Mem0 记忆查询工具")
    print("=" * 60)
    
    memory = Memory.from_config(config)
    user_id = "ningcaison"
    
    # 获取所有记忆
    print(f"\n[用户ID] {user_id}")
    print("-" * 60)
    
    all_memories = memory.get_all(user_id=user_id)
    
    if all_memories and len(all_memories) > 0:
        results = all_memories.get("results", [])
        print(f"\n[共 {len(results)} 条记忆]\n")
        
        for i, m in enumerate(results, 1):
            memory_text = m.get("memory", "")
            memory_id = m.get("id", "")
            created_at = m.get("created_at", "")
            
            print(f"{i}. {memory_text}")
            print(f"   ID: {memory_id}")
            print(f"   时间: {created_at}")
            print()
    else:
        print("\n没有找到任何记忆")
    
    print("=" * 60)
    print("存储位置: C:\\Users\\Administrator\\.mem0\\chroma\\")
    print("=" * 60)

if __name__ == "__main__":
    main()
