#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from pathlib import Path

token = Path("E:/workspace/knowledge-base/.notion_token").read_text(encoding='utf-8').strip()
db_id = Path("E:/workspace/knowledge-base/.notion_database_id").read_text(encoding='utf-8').strip()

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# 只获取一页看看total
url = f"https://api.notion.com/v1/databases/{db_id}/query"
response = requests.post(url, headers=headers, json={"page_size": 1}, timeout=15)
data = response.json()

# Notion API doesn't return total count directly, need to iterate
# Let's just count iterations with a cap
print(f"Response keys: {list(data.keys())}")
print(f"Has more: {data.get('has_more')}")
print(f"Next cursor: {data.get('next_cursor')}")
print(f"Results count: {len(data.get('results', []))}")

# Count total with a cap
cursor = None
total = 0
cap = 5  # Only test 5 iterations to estimate

while total < cap * 100:
    payload = {"page_size": 100}
    if cursor:
        payload["start_cursor"] = cursor
    
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    result = response.json()
    
    count = len(result.get('results', []))
    total += count
    has_more = result.get('has_more')
    cursor = result.get('next_cursor')
    
    print(f"Iteration {total//100}: got {count} pages, has_more={has_more}, cursor={bool(cursor)}")
    
    if not has_more:
        print(f"DONE! Total pages: {total}")
        break
    if not cursor:
        print(f"ERROR: has_more=True but no cursor!")
        break

if total >= cap * 100:
    print(f"Reached cap of {cap} iterations (est. {total}+ pages)")
