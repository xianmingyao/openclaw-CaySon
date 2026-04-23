#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Debug script for sync_pull_notion - step by step"""

import sys
sys.path.insert(0, 'E:/workspace/knowledge-base')

print('Starting debug...')

import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

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

def notion_api(endpoint: str, token: str, method: str = "GET", data: dict = None) -> dict:
    """调用 Notion API"""
    print(f'    [notion_api] Calling {method} {endpoint}')
    base_url = "https://api.notion.com/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    url = f"{base_url}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        else:
            response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f'    [notion_api] Response status: {response.status_code}')
        return response.json()
    except Exception as e:
        print(f'    [notion_api] Exception: {e}')
        return {"error": str(e)}

def get_all_pages(token: str, database_id: str) -> List[Dict]:
    """获取 Database 所有页面"""
    print('[get_all_pages] Starting...')
    pages = []
    cursor = None
    iteration = 0
    
    while True:
        iteration += 1
        print(f'[get_all_pages] Iteration {iteration}, cursor={cursor}')
        endpoint = f"/databases/{database_id}/query"
        if cursor:
            endpoint += f"?start_cursor={cursor}"
        
        print(f'[get_all_pages] Calling notion_api...')
        result = notion_api(endpoint, token, method="POST", data={"page_size": 100})
        print(f'[get_all_pages] Got result, has error: {bool(result.get("error"))}')
        
        if result.get('error'):
            print(f"[ERROR] {result.get('error')}")
            break
        
        for page in result.get('results', []):
            page_id = page.get('id', '').replace('-', '')
            properties = page.get('properties', {})
            
            # 获取标题
            title = "Untitled"
            for prop_name, prop in properties.items():
                if prop.get('type') == 'title':
                    title = ''.join([t.get('plain_text', '') for t in prop.get('title', [])])
                    break
            
            # 获取最后编辑时间
            last_edited = page.get('last_edited_time', '')
            
            pages.append({
                'id': page_id,
                'title': title,
                'last_edited': last_edited,
                'url': page.get('url', '')
            })
        
        print(f'[get_all_pages] Pages so far: {len(pages)}, has_more: {result.get("has_more")}')
        
        if not result.get('has_more'):
            break
        
        cursor = result.get('next_cursor')
        print(f'[get_all_pages] Next cursor: {cursor}')
        
        if iteration >= 5:  # Limit iterations for debugging
            print('[get_all_pages] Reached max iterations (5), breaking')
            break
    
    print(f'[get_all_pages] Done, total pages: {len(pages)}')
    return pages

# Main
token = get_notion_token()
database_id = get_database_id()
print(f'Token: {token[:15]}...')
print(f'DB ID: {database_id}')
print('Calling get_all_pages...')
pages = get_all_pages(token, database_id)
print(f'Got {len(pages)} pages')
