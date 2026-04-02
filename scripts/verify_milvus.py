#!/usr/bin/env python3
"""验证云端Milvus记忆 - 查询数据"""
import warnings
warnings.filterwarnings('ignore')

from pymilvus import MilvusClient

MILVUS_HOST = '8.137.122.11'
MILVUS_PORT = 19530
COLLECTION = 'CaySon_db'

print('[1] 连接Milvus...')
client = MilvusClient(uri=f'http://{MILVUS_HOST}:{MILVUS_PORT}')

print('[2] 查询最近记忆...')
try:
    results = client.query(
        collection_name=COLLECTION,
        filter='user_id == "ningcaison"',
        limit=10
    )
    print(f'[OK] 找到 {len(results)} 条记忆')
    for r in results:
        text = r.get('text', 'N/A')
        print(f'  ID={r.get("id")}: {str(text)[:60]}...')
except Exception as e:
    print(f'[FAIL] {e}')
    # 尝试获取collection stats
    try:
        stats = client.get_collection_stats(COLLECTION)
        print(f'Stats: {stats}')
    except:
        pass
