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
    print("[1] 初始化Mem0...")
    memory = Memory.from_config(config)
    print("[OK] Mem0初始化成功！")
    
    user_id = "ningcaison"
    
    # 获取所有记忆
    print("\n[2] 获取所有记忆...")
    all_memories = memory.get_all(user_id=user_id)
    if all_memories:
        print(f"共 {len(all_memories)} 条记忆:")
        for m in all_memories:
            if isinstance(m, dict):
                print(f"  - {m}")
            else:
                print(f"  - {m}")
    else:
        print("  没有记忆")
    
    # 搜索测试
    print("\n[3] 搜索测试...")
    results = memory.search("用户背景", user_id=user_id)
    print(f"搜索结果: {results}")
    
    print("\n[DONE]")

if __name__ == "__main__":
    main()
