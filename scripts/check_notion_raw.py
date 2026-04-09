#!/usr/bin/env python
import requests

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

blocks = resp.json()
first_block = blocks['results'][0]

# Get heading text
heading = first_block.get('heading_1', {})
rich_text = heading.get('rich_text', [])
if rich_text:
    text_obj = rich_text[0]
    print('Text obj:', text_obj)
    print('Plain text:', text_obj.get('plain_text'))
    print('Raw bytes of plain_text:', text_obj.get('plain_text').encode('utf-8'))
