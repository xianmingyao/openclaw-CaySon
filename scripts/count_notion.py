# -*- coding: utf-8 -*-
import requests
from pathlib import Path

token_file = Path('E:/workspace/knowledge-base/.notion_token')
token = token_file.read_text(encoding='utf-8').strip()

headers = {
    'Authorization': f'Bearer {token}',
    'Notion-Version': '2022-06-28'
}

db_id = '33d2bb5417c380f6baaff3467dea91c8'

total = 0
has_more = True
start_cursor = None

while has_more:
    url = f'https://api.notion.com/v1/databases/{db_id}/query'
    data = {'page_size': 100}
    if start_cursor:
        data['start_cursor'] = start_cursor
    
    resp = requests.post(url, headers=headers, json=data, timeout=30)
    result = resp.json()
    
    if 'results' in result:
        count = len(result['results'])
        total += count
        has_more = result.get('has_more', False)
        start_cursor = result.get('next_cursor')
        print(f'Got {count} pages, total: {total}, has_more: {has_more}')
    else:
        print('Error:', result.get('message', 'Unknown'))
        break

print(f'\n===== TOTAL PAGES: {total} =====')
