#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""同步Google I/O 2025 Android AI到Milvus"""
import os
import hashlib
from pymilvus import MilvusClient

# 读取文件内容
md_file = 'E:/workspace/knowledge-base/Google-IO-2025-Android-AI系统-2026-05-21.md'
with open(md_file, 'r', encoding='utf-8') as f:
    text = f.read()

# 连接到Milvus
client = MilvusClient(uri='http://8.137.122.11:19530')

# 获取集合统计
try:
    stats = client.get_collection_stats('CaySon_db')
    print(f"Current count: {stats.get('row_count', 0)}")
except Exception as e:
    print(f"Stats error: {e}")

# 简单向量
vec = [float(int(hashlib.md5(str(i).encode()).hexdigest()[:8], 16) % 100) / 100 for i in range(768)]

result = client.insert(
    collection_name='CaySon_db',
    data=[{
        'id': 17792399000002,
        'vector': vec,
        'text': text[:2000],  # 中文utf8约3字节，4096限制
        'user_id': 'cayson'
    }]
)
print(f"Milvus insert result: {result}")
print("Done!")
