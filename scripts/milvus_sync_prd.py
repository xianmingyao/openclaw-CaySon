#!/usr/bin/env python
import os, hashlib
from pymilvus import MilvusClient

md_file = 'E:/workspace/knowledge-base/PRD-Writer产品经理技能-2025-11-25.md'
with open(md_file, 'r', encoding='utf-8') as f:
    text = f.read()[:1200]  # 缩短到1200字符

client = MilvusClient(uri='http://8.137.122.11:19530')
stats = client.get_collection_stats('CaySon_db')
print(f"Current count: {stats.get('row_count', 0)}")

vec = [float(int(hashlib.md5(str(i).encode()).hexdigest()[:8], 16) % 100) / 100 for i in range(768)]
result = client.insert(collection_name='CaySon_db', data=[{
    'id': 17792399000006,
    'vector': vec,
    'text': text,
    'user_id': 'cayson'
}])
print(f"Milvus: {result}")
print("Done!")
