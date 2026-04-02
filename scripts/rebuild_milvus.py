# -*- coding: utf-8 -*-
from pymilvus import MilvusClient
from pymilvus.client import types
from pymilvus.milvus_client.index import IndexParams

client = MilvusClient(uri='http://8.137.122.11:19530')
COLLECTION = 'CaySon_db'

# 1. 删除旧 collection
print('[1] 删除旧 collection...')
try:
    client.drop_collection(COLLECTION)
    print('    [OK] 已删除')
except Exception as e:
    print(f'    [SKIP] {e}')

# 2. 创建新 collection
print('[2] 创建新 collection...')
schema = client.create_schema(
    auto_id=False,
    description='CaySon 记忆库',
    enable_dynamic_field=True
)
schema.add_field(field_name='id', datatype=types.DataType.INT64, is_primary=True)
schema.add_field(field_name='vector', datatype=types.DataType.FLOAT_VECTOR, dim=768)
schema.add_field(field_name='text', datatype=types.DataType.VARCHAR, max_length=4096)
schema.add_field(field_name='user_id', datatype=types.DataType.VARCHAR, max_length=256)

client.create_collection(
    collection_name=COLLECTION,
    schema=schema,
    consistency_level=2
)
print('    [OK] 新 collection 创建成功')

# 3. 创建索引
print('[3] 创建向量索引...')
idx = IndexParams()
idx.add_index(field_name='vector', index_type='AUTOINDEX', metric_type='COSINE')
client.create_index(COLLECTION, idx)
print('    [OK] 索引创建成功')

# 4. 加载 collection
print('[4] 加载 collection...')
client.load_collection(COLLECTION)
print('    [OK] 加载成功')

# 5. 验证
desc = client.describe_collection(COLLECTION)
print('\n[5] Schema 验证:')
for f in desc.get('fields', []):
    print(f'    - {f.get("name")}: {f.get("type")}')

print(f'\n[完成] Collection {COLLECTION} 已重建（包含索引+已加载）')
