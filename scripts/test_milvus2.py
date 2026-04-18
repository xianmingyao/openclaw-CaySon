# -*- coding: utf-8 -*-
from pymilvus import MilvusClient
c = MilvusClient(uri='http://8.137.122.11:19530')
collections = c.list_collections()
with open('E:\\workspace\\scripts\\test_result2.txt', 'w', encoding='utf-8') as f:
    f.write(f'Collections: {collections}\n')
    stats = c.get_collection_stats('CaySon_db')
    f.write(f'CaySon_db: {stats["row_count"]} 条\n')
