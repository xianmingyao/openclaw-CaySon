#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 Milvus Collection Schema
"""
from pymilvus import MilvusClient

MILVUS_HOST = "8.137.122.11"
MILVUS_PORT = 19530
MILVUS_COLLECTION = "CaySon_db"

def check_collection():
    client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}")
    
    try:
        schema = client.describe_collection(MILVUS_COLLECTION)
        print(f"Collection: {MILVUS_COLLECTION}")
        print(f"Schema: {schema}")
    except Exception as e:
        print(f"Error: {e}")
    
    try:
        stats = client.get_collection_stats(MILVUS_COLLECTION)
        print(f"\nStats: {stats}")
    except Exception as e:
        print(f"Stats error: {e}")

if __name__ == "__main__":
    check_collection()
