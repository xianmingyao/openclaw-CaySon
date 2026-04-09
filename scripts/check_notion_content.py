#!/usr/bin/env python
import requests

with open('E:/workspace/knowledge-base/.notion_token') as f:
    token = f.read().strip()

headers = {
    'Authorization': f'Bearer {token}',
    'Notion-Version': '2022-06-28'
}

# Get the first page
page_id = '33d2bb5417c381688738ec100fc4b322'
url = f'https://api.notion.com/v1/pages/{page_id}'
resp = requests.get(url, headers=headers, timeout=10)
print(f'Page Status: {resp.status_code}')

# Get blocks
blocks_url = f'https://api.notion.com/v1/blocks/{page_id}/children'
resp2 = requests.get(blocks_url, headers=headers, timeout=10)
blocks = resp2.json()
print(f'Blocks count: {len(blocks.get("results", []))}')

for b in blocks.get('results', [])[:5]:
    btype = b.get('type')
    print(f'  Type: {btype}')
    if btype == 'paragraph':
        texts = b.get('paragraph', {}).get('rich_text', [])
        for t in texts:
            print(f'    Text: {t.get("plain_text", "")[:100]}')
    elif btype == 'heading_1':
        texts = b.get('heading_1', {}).get('rich_text', [])
        for t in texts:
            print(f'    Heading: {t.get("plain_text", "")[:100]}')
