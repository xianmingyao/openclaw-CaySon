#!/usr/bin/env python
from pymilvus import MilvusClient
client = MilvusClient(uri='http://8.137.122.11:19530')
stats = client.get_collection_stats('CaySon_db')
print(f"Count: {stats.get('row_count', 0)}")
