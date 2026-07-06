#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""同步到本地Mem0/ChromaDB"""
import os
import sys
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

print("[1] Initializing Mem0...")

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
            "model": "nomic-embed-text",
            "ollama_base_url": OLLAMA_URL
        }
    }
}

memory_client = Memory.from_config(config)
print("[OK] Mem0 initialized")

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
        
        try:
            memory_client.add(text, user_id=USER_ID)
            total += 1
            if total % 20 == 0:
                print(f"  ... {total} synced")
        except Exception as e:
            print(f"  [WARN] {str(e)[:50]}")

print(f"\n[DONE] {total} records synced to Mem0/ChromaDB")
