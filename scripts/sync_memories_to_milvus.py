# -*- coding: utf-8 -*-
"""同步本地 ChromaDB 记忆到云端 Milvus"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

os.environ.pop('OPENAI_API_KEY', None)

from mem0 import Memory
from pymilvus import MilvusClient
import requests
import time

MILVUS_HOST = '8.137.122.11'
MILVUS_PORT = 19530
MILVUS_COLLECTION = 'CaySon_db'
OLLAMA_URL = 'http://localhost:11434'
EMBEDDING_MODEL = 'nomic-embed-text'
LOCAL_CHROMA_PATH = os.path.expanduser('~/.mem0/chroma')
USER_ID = 'ningcaison'

def get_embedding(text):
    response = requests.post(
        f'{OLLAMA_URL}/api/embeddings',
        json={'model': EMBEDDING_MODEL, 'prompt': text}
    )
    return response.json()['embedding']

def ensure_loaded(client):
    try:
        client.load_collection(MILVUS_COLLECTION)
    except:
        pass

print('=' * 60)
print('ChromaDB → Milvus 记忆同步')
print('=' * 60)

# 初始化
config = {
    'vector_store': {
        'provider': 'chroma',
        'config': {
            'collection_name': 'clawdbot_memories',
            'path': LOCAL_CHROMA_PATH
        }
    },
    'llm': {
        'provider': 'ollama',
        'config': {
            'model': 'llama3.2',
            'temperature': 0.0,
            'ollama_base_url': OLLAMA_URL
        }
    },
    'embedder': {
        'provider': 'ollama',
        'config': {
            'model': EMBEDDING_MODEL,
            'ollama_base_url': OLLAMA_URL
        }
    }
}

print('\n[1] 初始化客户端...')
memory_client = Memory.from_config(config)
milvus_client = MilvusClient(uri=f'http://{MILVUS_HOST}:{MILVUS_PORT}')
ensure_loaded(milvus_client)

# 获取本地所有记忆
print('[2] 获取本地 ChromaDB 所有记忆...')
local_all = memory_client.get_all(user_id=USER_ID)
local_memories = local_all.get('results', []) if isinstance(local_all, dict) else (local_all if isinstance(local_all, list) else [])
print(f'    本地记忆: {len(local_memories)} 条')

# 获取云端已有的记忆（用于去重）
print('[3] 获取云端 Milvus 已有的记忆...')
ensure_loaded(milvus_client)
milvus_all = milvus_client.query(
    collection_name=MILVUS_COLLECTION,
    limit=10000,
    output_fields=['text']
)
milvus_texts = set(item.get('text', '') for item in milvus_all if item.get('text'))
print(f'    云端已有: {len(milvus_texts)} 条')

# 找出需要同步的（本地有但云端没有的）
to_sync = [m for m in local_memories if m.get('memory', '') and m.get('memory', '') not in milvus_texts]
print(f'\n[4] 需要同步: {len(to_sync)} 条')

if len(to_sync) == 0:
    print('\n✅ 已全部同步，无需处理')
else:
    print('\n[5] 开始同步到云端 Milvus...')
    success = 0
    failed = 0
    for i, m in enumerate(to_sync, 1):
        text = m.get('memory', '')
        mem_id = m.get('id', f'mem_{i}')
        
        try:
            # 生成嵌入
            embedding = get_embedding(text)
            
            # 生成唯一ID（只用时间戳+序号，避免UUID字符）
            milvus_id = int(time.time() * 1000000) + i
            
            # 写入 Milvus
            milvus_client.insert(
                collection_name=MILVUS_COLLECTION,
                data=[{
                    'id': milvus_id,
                    'vector': embedding,
                    'text': text,
                    'user_id': USER_ID,
                }]
            )
            success += 1
            print(f'    [{i}/{len(to_sync)}] ✅ {text[:50]}...')
        except Exception as e:
            failed += 1
            print(f'    [{i}/{len(to_sync)}] ❌ {text[:50]}... 错误: {e}')
    
    print(f'\n[完成] 成功: {success} 条，失败: {failed} 条')

# 验证
print('\n[6] 验证同步结果...')
ensure_loaded(milvus_client)
milvus_count = milvus_client.query(
    collection_name=MILVUS_COLLECTION,
    filter='',
    limit=16384,
    output_fields=['id']
)
print(f'    云端 Milvus: {len(milvus_count)} 条')
print(f'    本地 ChromaDB: {len(local_memories)} 条')
print('\n' + '=' * 60)
