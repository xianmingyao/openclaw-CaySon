# -*- coding: utf-8 -*-
from pymilvus import MilvusClient
c = MilvusClient(uri='http://8.137.122.11:19530')
r = c.query(collection_name='CaySon_db', output_fields=['text','user_id'], limit=3)
with open('E:\\workspace\\scripts\\test_result.txt', 'w', encoding='utf-8') as f:
    for x in r:
        text = x.get('text', '')[:60]
        f.write(f"text: {text}\n")
    stats = c.get_collection_stats('CaySon_db')
    f.write(f"CaySon_db row_count: {stats['row_count']}\n")
