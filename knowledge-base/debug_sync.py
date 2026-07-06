#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug script for sync_pull_notion"""

import sys
sys.path.insert(0, 'E:/workspace/knowledge-base')

print('1. importing modules...')
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

print('2. defining functions...')

NOTION_TOKEN_FILE = Path('E:/workspace/knowledge-base/.notion_token')
NOTION_DB_ID_FILE = Path('E:/workspace/knowledge-base/.notion_database_id')
WIKI_DIR = Path('E:/workspace/knowledge-base/wiki')

def get_notion_token():
    if NOTION_TOKEN_FILE.exists():
        return NOTION_TOKEN_FILE.read_text(encoding='utf-8').strip()
    return ''

def get_database_id():
    if NOTION_DB_ID_FILE.exists():
        return NOTION_DB_ID_FILE.read_text(encoding='utf-8').strip()
    return ''

print('3. getting config...')
token = get_notion_token()
database_id = get_database_id()
print('Token:', token[:15] + '...')
print('DB ID:', database_id)

print('4. testing API...')
base_url = 'https://api.notion.com/v1'
headers = {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}
url = base_url + '/databases/' + database_id + '/query'
response = requests.post(url, headers=headers, json={'page_size': 10}, timeout=30)
print('API response status:', response.status_code)
result = response.json()
print('Error in result:', result.get('error'))
print('Results count:', len(result.get('results', [])))
print('Has more:', result.get('has_more'))
print('Next cursor:', result.get('next_cursor'))

if result.get('has_more') and result.get('next_cursor'):
    print('5. testing pagination...')
    cursor = result.get('next_cursor')
    url2 = base_url + '/databases/' + database_id + '/query'
    response2 = requests.post(url2, headers=headers, json={'page_size': 10, 'start_cursor': cursor}, timeout=30)
    result2 = response2.json()
    print('Page 2 count:', len(result2.get('results', [])))
    print('Has more:', result2.get('has_more'))

print('Done!')
