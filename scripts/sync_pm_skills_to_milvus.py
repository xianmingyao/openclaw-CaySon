#!/usr/bin/env python3
"""同步产品经理Skills到Milvus云端"""
import warnings
warnings.filterwarnings('ignore')

from pymilvus import MilvusClient
import requests
import time

MILVUS_HOST = '8.137.122.11'
MILVUS_PORT = 19530
COLLECTION = 'CaySon_db'

print('[1] 连接Milvus...')
client = MilvusClient(uri=f'http://{MILVUS_HOST}:{MILVUS_PORT}')
print('[OK] 已连接')

print('[2] 加载Collection...')
try:
    client.load_collection(COLLECTION)
    print('[OK] Collection已加载')
except Exception as e:
    print(f'[WARN] {e}')

# Read the doc
content = open(r'E:\workspace\knowledge-base\wiki\来源\产品经理Skills完整指南.md', 'r', encoding='utf-8').read()

# Split into chunks for embedding
lines = content.split('\n')
chunks = []
current_chunk = ""
for line in lines:
    if len(current_chunk) + len(line) < 500:
        current_chunk += line + "\n"
    else:
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        current_chunk = line + "\n"
if current_chunk.strip():
    chunks.append(current_chunk.strip())

print(f'[3] 开始同步记忆到云端 ({len(chunks)}个块)...')
success = 0
for i, m in enumerate(chunks):
    print(f'  块{i+1}: {m[:40]}...')
    try:
        resp = requests.post(
            'http://localhost:11434/api/embeddings',
            json={'model': 'nomic-embed-text', 'prompt': m},
            timeout=60
        )
        emb = resp.json()['embedding']
        mid = int(str(int(time.time()*1000)) + str(abs(hash(m)))[-4:])
        client.insert(COLLECTION, [{
            'id': mid,
            'vector': emb,
            'text': m,
            'user_id': 'ningcaison'
        }])
        print(f'    [OK] ID={mid}')
        success += 1
    except Exception as e:
        print(f'    [FAIL] {str(e)[:60]}')

print(f'\n[OK] 云端Milvus同步完成! 成功: {success}/{len(chunks)}')
