# -*- coding: utf-8 -*-
from pymilvus import MilvusClient
from pymilvus.client import types

client = MilvusClient(uri='http://8.137.122.11:19530')

schema = client.create_schema(
    auto_id=False,
    description='CaySon 记忆库',
    enable_dynamic_field=True
)
schema.add_field(field_name='id', datatype=types.DataType.INT64, is_primary=True)
schema.add_field(field_name='vector', datatype=types.DataType.FLOAT_VECTOR, params={'dim': 768})
schema.add_field(field_name='text', datatype=types.DataType.VARCHAR, max_length=4096)
schema.add_field(field_name='user_id', datatype=types.DataType.VARCHAR, max_length=256)

# 检查 schema 的 fields
print('Schema fields:')
for f in schema.fields:
    print(f'  name={f.name}, dtype={f.dtype}, params={f.params}')

# 试试直接用 FieldSchema 构建
from pymilvus.orm.schema import FieldSchema
vec_field = FieldSchema(field_name='vector', dtype=types.DataType.FLOAT_VECTOR, params={'dim': 768})
print(f'\nManual vec_field: name={vec_field.name}, dtype={vec_field.dtype}, params={vec_field.params}')
print(f'  to_dict: {vec_field.to_dict()}')
