#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""同步企业AI本体Ontology更新到Milvus（第21节-企业AI落地三问）"""
import os
import hashlib
from pymilvus import MilvusClient

# 读取文件内容
md_file = 'E:/workspace/knowledge-base/wiki/概念/企业AI本体Ontology-从工具到Agent的关键.md'
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

# 只取前2500字符（中文utf8约3字节，4096限制）
result = client.insert(
    collection_name='CaySon_db',
    data=[{
        'id': 17792399000003,
        'vector': vec,
        'text': text[:1500],  # 中文utf8约3字节，4096限制
        'user_id': 'cayson'
    }]
)
print(f"Milvus insert result: {result}")
print("Done!")
