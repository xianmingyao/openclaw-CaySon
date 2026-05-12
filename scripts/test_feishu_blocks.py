#!/usr/bin/env python
import os
import json
import requests

DOC_ID = "HjOVdDudOoYGycxIHKZcrMoonxe"
FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"

config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
feishu_config = config.get('channels', {}).get('feishu', {})

# Get token
resp = requests.post(
    f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal",
    json={"app_id": feishu_config.get('appId'), "app_secret": feishu_config.get('appSecret')},
    timeout=30
)
token = resp.json().get('tenant_access_token')

headers = {"Authorization": f"Bearer {token}"}

# Try different API paths
urls = [
    f"{FEISHU_BASE_URL}/docx/v1/documents/{DOC_ID}/blocks",
    f"{FEISHU_BASE_URL}/docx/v1/documents/{DOC_ID}",
    f"{FEISHU_BASE_URL}/drive/v1/files/{DOC_ID}",
]

for url in urls:
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"GET {url}")
        print(f"  Status: {resp.status_code}")
        print(f"  Response: {resp.text[:200]}\n")
    except Exception as e:
        print(f"GET {url}: Error - {e}\n")
