#!/usr/bin/env python
"""测试不同的段落格式"""
import requests, json

config = json.load(open('C:/Users/Administrator/.openclaw/openclaw.json'))
feishu = config['channels']['feishu']

resp = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': feishu['appId'], 'app_secret': feishu['appSecret']},
    timeout=10)
token = resp.json().get('tenant_access_token')

resp = requests.post('https://open.feishu.cn/open-apis/docx/v1/documents',
    headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
    json={'title': 'Format Test'},
    timeout=10)
doc_id = resp.json().get('data', {}).get('document', {}).get('document_id')

resp2 = requests.get(f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks',
    headers={'Authorization': f'Bearer {token}'}, timeout=10)
page_block_id = resp2.json().get('data', {}).get('items', [{}])[0].get('block_id', doc_id)

url = f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{page_block_id}/children'

formats = [
    ('Paragraph v1', {
        'children': [{
            'block_type': 2,
            'paragraph': {
                'elements': [{'type': 'text_run', 'text_run': {'content': 'Hello v1'}}]
            }
        }],
        'index': 0
    }),
    ('Paragraph v2', {
        'children': [{
            'block_type': 2,
            'paragraph': {
                'elements': [{'type': 'text_run', 'text_run': {'content': 'Hello v2', 'text_element_style': {}}}],
                'style': {}
            }
        }],
        'index': 0
    }),
    ('Paragraph v3 text_element_style', {
        'children': [{
            'block_type': 2,
            'paragraph': {
                'elements': [{'type': 'text_run', 'text_run': {'content': 'Hello v3'}}],
                'style': {}
            }
        }],
        'index': 0
    }),
    ('Bullet', {
        'children': [{
            'block_type': 12,
            'bullet': {
                'elements': [{'type': 'text_run', 'text_run': {'content': 'Bullet item'}}],
                'style': {}
            }
        }],
        'index': 0
    }),
    ('Quote', {
        'children': [{
            'block_type': 13,
            'quote': {
                'elements': [{'type': 'text_run', 'text_run': {'content': 'Quote text'}}],
                'style': {}
            }
        }],
        'index': 0
    }),
]

for name, data in formats:
    resp3 = requests.post(url, headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, json=data, timeout=10)
    result = resp3.json()
    status = 'OK' if result.get('code') == 0 else f'FAIL({result.get("code")})'
    print(f'{name}: {status}')

print(f'\nDoc: https://feishu.cn/docx/{doc_id}')
