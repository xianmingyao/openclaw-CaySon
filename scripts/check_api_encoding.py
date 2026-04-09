#!/usr/bin/env python
import requests
import json

with open('E:/workspace/knowledge-base/.notion_token') as f:
    token = f.read().strip()

headers = {
    'Authorization': f'Bearer {token}',
    'Notion-Version': '2022-06-28'
}

# Get blocks
page_id = '33d2bb5417c381688738ec100fc4b322'
url = f'https://api.notion.com/v1/blocks/{page_id}/children'
resp = requests.get(url, headers=headers, timeout=10)

# Get raw text
blocks = resp.json()
first_block = blocks['results'][0]
print('First block type:', first_block.get('type'))
print('First block raw:', json.dumps(first_block, ensure_ascii=False)[:300])
