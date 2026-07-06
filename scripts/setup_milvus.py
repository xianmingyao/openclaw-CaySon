from pymilvus import MilvusClient
from pymilvus import FieldSchema, CollectionSchema, DataType, Index

client = MilvusClient(uri='http://8.137.122.11:19530')

# 删除旧集合
try:
    client.drop_collection('CaySon_db')
    print('已删除旧集合')
except:
    pass

# 定义Schema
fields = [
    FieldSchema(name='id', dtype=DataType.INT64, is_primary=True, auto_id=True),
    FieldSchema(name='vector', dtype=DataType.FLOAT_VECTOR, dim=768),
    FieldSchema(name='text', dtype=DataType.VARCHAR, max_length=10000),
    FieldSchema(name='user_id', dtype=DataType.VARCHAR, max_length=100)
]

schema = CollectionSchema(fields=fields, description='CaySon知识库', enable_dynamic_field=True)

# 创建集合
client.create_collection(collection_name='CaySon_db', schema=schema)
print('✅ 集合创建成功')

# 创建索引
client.create_index(
    collection_name='CaySon_db',
    field_name='vector',
    index_type='AUTOINDEX',
    metric_type='COSINE'
)
print('✅ 索引创建成功')

# 加载集合
client.load_collection('CaySon_db')
print('✅ 集合已加载')

# 测试写入
import random
vector = [random.random() for _ in range(768)]
result = client.insert(
    collection_name='CaySon_db',
    data=[{'vector': vector, 'text': '测试记忆', 'user_id': 'system'}]
)
print('✅ 测试写入成功，ID:', result['ids'])

print()
print('=' * 50)
print('CaySon_db 集合已就绪！')
print('=' * 50)
