#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""同步 Hermes Agent 184专家团队 到 Milvus"""
import os
import hashlib
from pymilvus import MilvusClient

md_file = 'E:/workspace/knowledge-base/Hermes-Agent-184专家团队-2026-01-18.md'
with open(md_file, 'r', encoding='utf-8') as f:
    text = f.read()

client = MilvusClient(uri='http://8.137.122.11:19530')

try:
    stats = client.get_collection_stats('CaySon_db')
    print(f"Current count: {stats.get('row_count', 0)}")
except Exception as e:
    print(f"Stats error: {e}")

vec = [float(int(hashlib.md5(str(i).encode()).hexdigest()[:8], 16) % 100) / 100 for i in range(768)]

result = client.insert(
    collection_name='CaySon_db',
    data=[{
        'id': 17792399000005,
        'vector': vec,
        'text': text[:1500],
        'user_id': 'cayson'
    }]
)
print(f"Milvus insert result: {result}")
print("Done!")
