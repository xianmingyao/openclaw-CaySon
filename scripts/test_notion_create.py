# -*- coding: utf-8 -*-
"""Test Notion page creation with fixed title"""
import requests
from pathlib import Path

# Read token
token_file = Path('E:/workspace/knowledge-base/.notion_token')
token = token_file.read_text(encoding='utf-8').strip()

headers = {
    'Authorization': f'Bearer {token}',
    'Notion-Version': '2022-06-28'
}

db_id = '33d2bb5417c380f6baaff3467dea91c8'

# Test creating a page with correct title column name
url = 'https://api.notion.com/v1/pages'
data = {
    'parent': {'database_id': db_id},
    'properties': {
        '标题': {
            'title': [{'type': 'text', 'text': {'content': '测试页面-修复标题'}}]
        }
    },
    'children': [
        {
            'object': 'block',
            'type': 'paragraph',
            'paragraph': {
                'rich_text': [{'type': 'text', 'text': {'content': '这是一次测试'}}]
            }
        }
    ]
}

resp = requests.post(url, headers=headers, json=data, timeout=30)
print('Status:', resp.status_code)
result = resp.json()

if resp.status_code == 200:
    page_id = result.get('id')
    print('Success! Page ID:', page_id)
    print('URL:', f'https://notion.so/{page_id.replace("-", "")}')
else:
    print('Error:', result.get('message', 'Unknown'))
    print('Full response:', result)
