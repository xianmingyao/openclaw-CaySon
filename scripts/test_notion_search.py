#!/usr/bin/env python
import requests

with open('E:/workspace/knowledge-base/.notion_token') as f:
    token = f.read().strip()

headers = {
    'Authorization': f'Bearer {token}',
    'Notion-Version': '2022-06-28'
}

# Try to search databases
url = 'https://api.notion.com/v1/search'
data = {'query': 'Karpathy', 'filter': {'property': 'object', 'value': 'database'}}
resp = requests.post(url, headers=headers, json=data, timeout=10)
print(f'Search status: {resp.status_code}')
if resp.status_code == 200:
    results = resp.json().get('results', [])
    print(f'Found {len(results)} databases')
    for r in results[:5]:
        title = r.get('title', [{}])[0].get('plain_text', 'Untitled')
        db_id = r.get('id')
        print(f'  - {title} : {db_id}')
else:
    print(f'Error: {resp.text[:200]}')
