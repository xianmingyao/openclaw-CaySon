#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import requests
from pathlib import Path

print("1. Import done", flush=True)

token_file = Path("E:/workspace/knowledge-base/.notion_token")
db_file = Path("E:/workspace/knowledge-base/.notion_database_id")

token = token_file.read_text(encoding='utf-8').strip()
db_id = db_file.read_text(encoding='utf-8').strip()
print(f"2. Token: {token[:15]}..., DB: {db_id}", flush=True)

url = "https://api.notion.com/v1/databases/" + db_id + "/query"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
print(f"3. Sending POST request to {url}", flush=True)

try:
    response = requests.post(url, headers=headers, json={"page_size": 100}, timeout=30)
    print(f"4. Response: {response.status_code}", flush=True)
    data = response.json()
    print(f"5. Got {len(data.get('results', []))} results", flush=True)
except Exception as e:
    print(f"ERROR: {e}", flush=True)

print("Done", flush=True)
