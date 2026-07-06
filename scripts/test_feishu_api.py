#!/usr/bin/env python
import os
import json
import requests

# Config
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
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:500]}")

token = resp.json().get('tenant_access_token')

# Try to get document info
headers = {"Authorization": f"Bearer {token}"}
url = f"{FEISHU_BASE_URL}/docx/v1/documents/{DOC_ID}"
resp = requests.get(url, headers=headers, timeout=30)
print(f"\nDoc Info Status: {resp.status_code}")
print(f"Doc Info Response: {resp.text[:500]}")
