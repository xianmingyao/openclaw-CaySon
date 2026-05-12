#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查Milvus CaySon_db的Schema"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from pymilvus import MilvusClient

MILVUS_HOST = "8.137.122.11"
MILVUS_PORT = 19530
MILVUS_COLLECTION = "CaySon_db"

client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}")

# 获取Collection信息
print("Collection Info:")
try:
    info = client.describe_collection(MILVUS_COLLECTION)
    print(f"  Schema: {info.get('schema', {})}")
    print(f"  Fields: {info.get('fields', [])}")
except Exception as e:
    print(f"  Error: {e}")

# 获取一条数据看结构
print("\nSample Data:")
try:
    result = client.query(
        collection_name=MILVUS_COLLECTION,
        limit=1
    )
    if result:
        print(f"  Keys: {list(result[0].keys()) if result else 'None'}")
        print(f"  Sample: {result[0]}")
    else:
        print("  No data found")
except Exception as e:
    print(f"  Error: {e}")
