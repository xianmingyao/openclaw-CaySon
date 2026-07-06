import random
from pymilvus import MilvusClient

client = MilvusClient(uri='http://8.137.122.11:19530')

# 测试写入（需要提供id，因为auto_id=False）
vector = [random.random() for _ in range(768)]
result = client.insert(
    collection_name='CaySon_db',
    data=[{'id': 1, 'vector': vector, 'text': '测试记忆-CaySon', 'user_id': 'system'}]
)
print('✅ 写入成功! ID:', result['ids'])

# 查询
query_result = client.query(
    collection_name='CaySon_db',
    filter='text == "测试记忆-CaySon"',
    limit=1
)
print('✅ 查询成功! 结果:', query_result)

# 搜索
search_result = client.search(
    collection_name='CaySon_db',
    data=[vector],
    limit=1
)
print('✅ 向量搜索成功! 结果数:', len(search_result[0]))

print()
print('=' * 50)
print('🎉 CaySon_db 云端Milvus记忆库已就绪！')
print('=' * 50)
