#!/usr/bin/env python
"""
测试飞书文档写入 - 使用不同格式
"""
import requests, json

config = json.load(open('C:/Users/Administrator/.openclaw/openclaw.json'))
feishu = config['channels']['feishu']

# Get fresh token
resp = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': feishu['appId'], 'app_secret': feishu['appSecret']},
    timeout=10)
token = resp.json().get('tenant_access_token')
print(f'Token: {token[:30]}...')

# Create a new doc
resp = requests.post('https://open.feishu.cn/open-apis/docx/v1/documents',
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    json={'title': 'Wiki Sync Test'},
    timeout=10)
result = resp.json()
print(f'Create doc: code={result.get("code")}, doc_id={result.get("data", {}).get("document", {}).get("document_id")}')

doc_id = result.get('data', {}).get('document', {}).get('document_id')
if not doc_id:
    print('Failed to create doc')
    exit(1)

# Get blocks to find page block id
resp2 = requests.get(f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks',
    headers={'Authorization': f'Bearer {token}'}, timeout=10)
items = resp2.json().get('data', {}).get('items', [])
print(f'Blocks: {len(items)} found')

page_block = items[0] if items else None
if page_block:
    print(f'Page block: id={page_block.get("block_id")}, type={page_block.get("block_type")}')
    page_block_id = page_block.get('block_id')
    
    # Try various block formats
    formats = [
        {
            'name': 'Simple paragraph',
            'data': {
                'children': [{
                    'block_type': 2,
                    'paragraph': {
                        'elements': [{'type': 'text_run', 'text_run': {'content': 'Test paragraph'}}]
                    }
                }],
                'index': 0
            }
        },
        {
            'name': 'With style',
            'data': {
                'children': [{
                    'block_type': 2,
                    'paragraph': {
                        'elements': [{'type': 'text_run', 'text_run': {'content': 'Test with style'}}],
                        'style': {}
                    }
                }],
                'index': 0
            }
        },
        {
            'name': 'Heading1',
            'data': {
                'children': [{
                    'block_type': 3,
                    'heading1': {
                        'elements': [{'type': 'text_run', 'text_run': {'content': 'Heading 1'}}],
                        'style': {}
                    }
                }],
                'index': 0
            }
        }
    ]
    
    for fmt in formats:
        url = f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{page_block_id}/children'
        resp3 = requests.post(url, 
            headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, 
            json=fmt['data'], timeout=10)
        result3 = resp3.json()
        status = 'OK' if result3.get('code') == 0 else f'FAIL(code={result3.get("code")})'
        print(f'{fmt["name"]}: {status}')
        if result3.get('code') == 0:
            print('SUCCESS! Block written!')
            print(f'Doc URL: https://feishu.cn/docx/{doc_id}')
            break
