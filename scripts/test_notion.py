# -*- coding: utf-8 -*-
"""Test Notion API connection - Check actual column names"""
import requests
from pathlib import Path
import unicodedata

# Read token
token_file = Path('E:/workspace/knowledge-base/.notion_token')
token = token_file.read_text(encoding='utf-8').strip()

# Test Notion API
headers = {
    'Authorization': f'Bearer {token}',
    'Notion-Version': '2022-06-28'
}

# Get Database info
db_id = '33d2bb5417c380f6baaff3467dea91c8'
url = f'https://api.notion.com/v1/databases/{db_id}'
resp = requests.get(url, headers=headers, timeout=30)

result = resp.json()
if 'properties' in result:
    # Get title column name
    title_col = None
    for prop_name, prop_data in result['properties'].items():
        if prop_data.get('type') == 'title':
            title_col = prop_name
            break
    
    print('Title column name:', title_col)
    print('Title column bytes:', title_col.encode('utf-8') if title_col else None)
    
    # Count pages
    url2 = f'https://api.notion.com/v1/databases/{db_id}/query'
    resp2 = requests.post(url2, headers=headers, json={'page_size': 100}, timeout=30)
    result2 = resp2.json()
    total = len(result2.get('results', []))
    print('Total pages:', total)
    
    # Try to show a sample page properties
    if result2.get('results'):
        page = result2['results'][0]
        print('\nSample page properties:')
        if 'properties' in page:
            for k, v in page['properties'].items():
                print(f'  {k}: {v.get("type")}')
