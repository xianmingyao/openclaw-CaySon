#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
记忆上传脚本 v3
使用正确的 schema 上传到 Milvus
"""

import sys
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# Milvus 配置
MILVUS_HOST = "8.137.122.11"
MILVUS_PORT = 19530
COLLECTION_NAME = "CaySon_db"
OLLAMA_URL = "http://localhost:11434"
EMBEDDING_MODEL = "nomic-embed-text"
USER_ID = "knowledge-base"

# 知识库路径
WIKI_DIR = Path(__file__).parent / "wiki"
MEMORY_FILE = Path(__file__).parent / "memory" / "knowledge-base.json"


def load_wiki_entries():
    """加载 wiki 条目"""
    entries = []
    for f in WIKI_DIR.rglob("*.md"):
        content = f.read_text(encoding='utf-8')
        entries.append({
            'title': f.stem,
            'content': content,
            'path': str(f.relative_to(WIKI_DIR)),
            'created': datetime.now().isoformat()
        })
    return entries


def get_embedding(text: str) -> list:
    """获取文本 embedding"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text[:2000]},
            timeout=30
        )
        return response.json()["embedding"]
    except Exception as e:
        print(f"   ERROR getting embedding: {e}")
        return None


def upload_to_milvus(entries: list) -> dict:
    """上传到 Milvus"""
    try:
        from pymilvus import MilvusClient
        
        client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}")
        
        print(f"   Loading collection {COLLECTION_NAME}...")
        try:
            client.load_collection(COLLECTION_NAME)
        except:
            pass
        
        print(f"   Generating embeddings and uploading {len(entries)} entries...")
        
        for i, e in enumerate(entries):
            print(f"   - {e['title']}...")
            
            # 获取 embedding
            embedding = get_embedding(e['content'])
            if not embedding:
                embedding = [0.0] * 768
            
            # 生成 ID
            milvus_id = int(str(int(time.time() * 1000)) + str(i)[-4:])
            
            # 插入数据
            data = [
                {
                    "id": milvus_id,
                    "vector": embedding,
                    "text": e['content'][:1000],
                    "user_id": USER_ID,
                }
            ]
            
            try:
                result = client.insert(
                    collection_name=COLLECTION_NAME,
                    data=data
                )
                print(f"     [OK] ID: {milvus_id}")
            except Exception as ex:
                print(f"     [FAIL] {ex}")
        
        return {'success': True, 'count': len(entries)}
        
    except ImportError:
        print("   ERROR: pymilvus not installed")
        return {'success': False, 'error': 'pymilvus not installed'}
    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def main():
    print("=" * 50)
    print("MEMORY UPLOAD TO MILVUS v3")
    print("=" * 50)
    
    # 加载条目
    print("\n[LOAD] Loading wiki entries...")
    entries = load_wiki_entries()
    print(f"   Found {len(entries)} entries")
    
    for e in entries:
        print(f"   - {e['title']}: {len(e['content'])} chars")
    
    # 保存本地副本
    print("\n[SAVE] Saving local copy...")
    MEMORY_FILE.parent.mkdir(exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"   Saved to {MEMORY_FILE}")
    
    # 上传到 Milvus
    print("\n[UPLOAD] Uploading to Milvus...")
    result = upload_to_milvus(entries)
    
    if result.get('success'):
        print(f"\n[DONE] Successfully uploaded {result['count']} entries to Milvus")
    else:
        print(f"\n[FAIL] Upload failed: {result.get('error')}")


if __name__ == '__main__':
    main()
