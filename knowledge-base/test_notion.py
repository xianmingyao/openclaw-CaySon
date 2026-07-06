#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import requests
from pathlib import Path

print("Python version:", sys.version)
print("Script starting...")

# Check token
token_file = Path(__file__).parent / ".notion_token"
if token_file.exists():
    token = token_file.read_text(encoding='utf-8').strip()
    print(f"Token loaded: {token[:20]}...")
else:
    print("ERROR: Token file not found")
    sys.exit(1)

# Check database_id
db_file = Path(__file__).parent / ".notion_database_id"
if db_file.exists():
    db_id = db_file.read_text(encoding='utf-8').strip()
    print(f"Database ID loaded: {db_id}")
else:
    print("ERROR: Database ID file not found")
    sys.exit(1)

# Test API call
print("Testing API call...")
url = "https://api.notion.com/v1/databases/" + db_id
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    print(f"Response status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"ERROR: {e}")

print("Script done.")
