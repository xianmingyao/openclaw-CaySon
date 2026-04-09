#!/usr/bin/env python
import requests, json

config = json.load(open('C:/Users/Administrator/.openclaw/openclaw.json'))
feishu = config['channels']['feishu']

# Get token
resp = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': feishu['appId'], 'app_secret': feishu['appSecret']},
    timeout=10)
token = resp.json().get('tenant_access_token')
print('Token OK')

# Create doc
resp = requests.post('https://open.feishu.cn/open-apis/docx/v1/documents',
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    json={'title': 'Perm Test 3'},
    timeout=10)
doc_id = resp.json().get('data', {}).get('document', {}).get('document_id')
print(f'Doc created: {doc_id}')

if doc_id:
    # Get page block id
    resp2 = requests.get(f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks',
        headers={'Authorization': f'Bearer {token}'}, timeout=10)
    items = resp2.json().get('data', {}).get('items', [])
    page_block_id = items[0].get('block_id') if items else doc_id
    
    # Try to add text block
    blocks_url = f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{page_block_id}/children'
    block_data = {
        'children': [{
            'block_type': 2,
            'paragraph': {
                'elements': [{'type': 'text_run', 'text_run': {'content': 'Hello CaySon!'}}],
                'style': {}
            }
        }],
        'index': 0
    }
    resp3 = requests.post(blocks_url, headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, json=block_data, timeout=10)
    result = resp3.json()
    code = result.get('code')
    msg = result.get('msg')
    print(f'Block write code: {code}')
    print(f'Block write msg: {msg}')
    if code == 0:
        print('SUCCESS! Permission granted!')
    else:
        print('Still failing...')
