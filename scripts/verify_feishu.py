#!/usr/bin/env python
import requests, json
config = json.load(open('C:/Users/Administrator/.openclaw/openclaw.json'))
feishu = config['channels']['feishu']
resp = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': feishu['appId'], 'app_secret': feishu['appSecret']}, timeout=10)
token = resp.json().get('tenant_access_token')

# Create doc
resp = requests.post('https://open.feishu.cn/open-apis/docx/v1/documents',
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    json={'title': 'Permission Test Final'}, timeout=10)
doc_id = resp.json().get('data', {}).get('document', {}).get('document_id')
print(f'Doc created: {doc_id}')

# Get page block
resp2 = requests.get(f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks',
    headers={'Authorization': f'Bearer {token}'}, timeout=10)
page_id = resp2.json().get('data', {}).get('items', [{}])[0].get('block_id', doc_id)

# Write heading + bullet
url = f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{page_id}/children'
blocks = [
    {'block_type': 3, 'heading1': {'elements': [{'type': 'text_run', 'text_run': {'content': 'Test Heading'}}], 'style': {}}},
    {'block_type': 12, 'bullet': {'elements': [{'type': 'text_run', 'text_run': {'content': 'Test bullet item'}}], 'style': {}}}
]
resp3 = requests.post(url, headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    json={'children': blocks, 'index': -1}, timeout=10)
result = resp3.json()
code = result.get('code')
msg = result.get('msg')
print(f'Write blocks: code={code}, msg={msg}')
if code == 0:
    print('SUCCESS! Permission fully working!')
    print(f'URL: https://feishu.cn/docx/{doc_id}')
else:
    print('Still has issues...')
