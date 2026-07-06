from pymilvus import MilvusClient
import random

client = MilvusClient(uri='http://8.137.122.11:19530')

# 测试写入
vector = [random.random() for _ in range(768)]

result = client.insert(
    collection_name='CaySon_db',
    data=[{'vector': vector, 'text': '测试记忆', 'user_id': 'system'}]
)
print('✅ 写入成功!')
print('插入结果:', result)

# 查询验证
query_result = client.query(
    collection_name='CaySon_db',
    filter='text == "测试记忆"',
    limit=1
)
print('查询结果:', query_result)
print()
print('✅ CaySon_db 集合已就绪，可以同步记忆了！')
