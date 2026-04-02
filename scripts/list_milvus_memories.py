#!/usr/bin/env python3
import warnings
import sys
warnings.filterwarnings('ignore')
sys.stdout.reconfigure(encoding='utf-8')
from pymilvus import MilvusClient

client = MilvusClient(uri='http://8.137.122.11:19530')

results = client.query(
    collection_name='CaySon_db',
    filter='user_id == "ningcaison"',
    output_fields=['text'],
    limit=100
)

print(f'云端 Milvus 记忆总数: {len(results)}')
print('='*50)
for i, r in enumerate(results, 1):
    text = r.get('text', 'N/A')
    print(f'{i}. {text[:70]}...' if len(text) > 70 else f'{i}. {text}')
