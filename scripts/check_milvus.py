# -*- coding: utf-8 -*-
from pymilvus import MilvusClient
c = MilvusClient(uri='http://8.137.122.11:19530')
c.load_collection('CaySon_db')
r = c.query('CaySon_db', limit=10, output_fields=['id','text','user_id'])
print(f'Milvus 共有 {len(r)} 条记录')
for item in r:
    text = item.get('text', '')[:60]
    print(f'  id={item["id"]} user={item["user_id"]} text=[{text}]')
