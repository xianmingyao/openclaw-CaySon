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

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Try correct API path with block_id
# According to Feishu docs: POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children
url = f"{FEISHU_BASE_URL}/docx/v1/documents/{DOC_ID}/blocks/{DOC_ID}/children"

block = {
    "children": [{
        "block_type": 2,
        "text": {
            "elements": [{"type": "text_run", "text_run": {"content": "Test paragraph from API v2"}}],
            "style": {}
        }
    }],
    "index": 1
}

print(f"POST {url}")
resp = requests.post(url, headers=headers, json=block, timeout=15)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:500]}")
