#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick test - just get first 5 pages"""

import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import requests
from pathlib import Path

NOTION_TOKEN_FILE = Path('E:/workspace/knowledge-base/.notion_token')
NOTION_DB_ID_FILE = Path('E:/workspace/knowledge-base/.notion_database_id')

token = NOTION_TOKEN_FILE.read_text(encoding='utf-8').strip()
db_id = NOTION_DB_ID_FILE.read_text(encoding='utf-8').strip()

print(f'Token: {token[:15]}...')
print(f'DB ID: {db_id}')

headers = {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

# Just get first page
print('Querying database (page_size=5)...')
r = requests.post(
    'https://api.notion.com/v1/databases/' + db_id + '/query',
    headers=headers,
    json={'page_size': 5},
    timeout=30
)
print(f'Status: {r.status_code}')
data = r.json()
print(f'Pages returned: {len(data.get("results", []))}')
print(f'Has more: {data.get("has_more")}')
print(f'Next cursor: {data.get("next_cursor")}')

for page in data.get('results', []):
    props = page.get('properties', {})
    title = 'Untitled'
    for name, prop in props.items():
        if prop.get('type') == 'title':
            title = ''.join([t.get('plain_text', '') for t in prop.get('title', [])])
            break
    print(f'  - {title}')

print('Done!')
