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

# Try POST to blocks/children
url = f"{FEISHU_BASE_URL}/docx/v1/documents/{DOC_ID}/blocks/children"

# Get current blocks first to find the root block
get_url = f"{FEISHU_BASE_URL}/docx/v1/documents/{DOC_ID}/blocks"
resp = requests.get(get_url, headers=headers, timeout=15)
blocks = resp.json().get('data', {}).get('items', [])
print(f"Current blocks: {len(blocks)}")
if blocks:
    print(f"First block: {blocks[0].get('block_id')}, type={blocks[0].get('block_type')}")

# Try inserting with index=0
block = {
    "children": [{
        "block_type": 2,
        "text": {
            "elements": [{"type": "text_run", "text_run": {"content": "Test from API"}}],
            "style": {}
        }
    }],
    "index": 1
}

resp = requests.post(url, headers=headers, json=block, timeout=15)
print(f"\nPOST {url}")
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:500]}")
