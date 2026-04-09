#!/usr/bin/env python
import requests

with open('E:/workspace/knowledge-base/.notion_token') as f:
    token = f.read().strip()

headers = {
    'Authorization': f'Bearer {token}',
    'Notion-Version': '2022-06-28'
}

# Get blocks from index page
page_id = '33d2bb5417c381688738ec100fc4b322'
url = f'https://api.notion.com/v1/blocks/{page_id}/children'
resp = requests.get(url, headers=headers, timeout=10)
blocks = resp.json()

print(f'Blocks: {len(blocks.get("results", []))}')
for b in blocks.get('results', [])[:5]:
    btype = b.get('type')
    if btype == 'heading_1':
        texts = b.get('heading_1', {}).get('rich_text', [])
        for t in texts:
            print(f'  H1: {t.get("plain_text", "")}')
    elif btype == 'bulleted_list_item':
        texts = b.get('bulleted_list_item', {}).get('rich_text', [])
        for t in texts:
            print(f'  Bullet: {t.get("plain_text", "")[:80]}')
