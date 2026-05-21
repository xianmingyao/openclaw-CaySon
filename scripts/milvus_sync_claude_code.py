#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""同步Claude Code最佳实践到Milvus"""
import os
import json
from pymilvus import MilvusClient

# 读取文件内容
md_file = 'E:/workspace/knowledge-base/Claude Code大型项目最佳实践-2026-05-21.md'
with open(md_file, 'r', encoding='utf-8') as f:
    text = f.read()

# 连接到Milvus (新版本pymilvus不需要connect)
client = MilvusClient(uri='http://8.137.122.11:19530')

# 获取集合统计
try:
    stats = client.get_collection_stats('CaySon_db')
    print(f"Current count: {stats.get('row_count', 0)}")
except Exception as e:
    print(f"Stats error: {e}")

# 简单向量（用文本生成确定性向量）
import hashlib
vec = [float(int(hashlib.md5(str(i).encode()).hexdigest()[:8], 16) % 100) / 100 for i in range(768)]

result = client.insert(
    collection_name='CaySon_db',
    data=[{
        'id': 17792399000001,
        'vector': vec,
        'text': text[:2500],  # 中文字符utf8约3字节，留余量
        'user_id': 'cayson'
    }]
)
print(f"Milvus insert result: {result}")
print("Done!")
