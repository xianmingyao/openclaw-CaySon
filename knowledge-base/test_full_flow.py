#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import requests
from pathlib import Path

print("=" * 50)
print("NOTION PULL - 双向同步（Notion → 本地）")
print("=" * 50)

# 配置
NOTION_TOKEN_FILE = Path("E:/workspace/knowledge-base/.notion_token")
NOTION_DB_ID_FILE = Path("E:/workspace/knowledge-base/.notion_database_id")

# API函数
def notion_api(endpoint, token, method="GET", data=None):
    base_url = "https://api.notion.com/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    url = f"{base_url}{endpoint}"
    print(f"  API call: {method} {url}", flush=True)
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        else:
            response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        print(f"  Response status: {response.status_code}", flush=True)
        return result
    except Exception as e:
        print(f"  Exception: {e}", flush=True)
        return {"error": str(e)}

def get_all_pages(token, database_id):
    pages = []
    cursor = None
    iteration = 0
    
    while True:
        iteration += 1
        print(f"  Iteration {iteration}", flush=True)
        endpoint = f"/databases/{database_id}/query"
        data = {"page_size": 100}
        if cursor:
            data["start_cursor"] = cursor
        
        result = notion_api(endpoint, token, method="POST", data=data)
        
        if result.get('error'):
            print(f"[ERROR] {result.get('error')}")
            break
        
        page_count = len(result.get('results', []))
        print(f"  Got {page_count} pages", flush=True)
        
        for page in result.get('results', []):
            page_id = page.get('id', '').replace('-', '')
            properties = page.get('properties', {})
            title = "Untitled"
            for prop_name, prop in properties.items():
                if prop.get('type') == 'title':
                    title = ''.join([t.get('plain_text', '') for t in prop.get('title', [])])
                    break
            last_edited = page.get('last_edited_time', '')
            pages.append({
                'id': page_id,
                'title': title,
                'last_edited': last_edited,
                'url': page.get('url', '')
            })
        
        has_more = result.get('has_more')
        print(f"  has_more: {has_more}", flush=True)
        
        if not has_more:
            break
        
        cursor = result.get('next_cursor')
        if not cursor:
            print(f"  ERROR: has_more=True but no cursor!", flush=True)
            break
    
    return pages

# 主流程
token = NOTION_TOKEN_FILE.read_text(encoding='utf-8').strip()
database_id = NOTION_DB_ID_FILE.read_text(encoding='utf-8').strip()

print(f"\n[1/3] Token: {token[:15]}...", flush=True)
print(f"[1/3] Database ID: {database_id}", flush=True)
print("\n[1/3] 获取 Notion Database 页面列表...", flush=True)
pages = get_all_pages(token, database_id)
print(f"\n      找到 {len(pages)} 个页面", flush=True)

print("\n[DONE]", flush=True)
