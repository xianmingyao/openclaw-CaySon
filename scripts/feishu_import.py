#!/usr/bin/env python
import os
import json
import requests

FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"

config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
feishu_config = config.get('channels', {}).get('feishu', {})
FEISHU_APP_ID = feishu_config.get('appId')
FEISHU_APP_SECRET = feishu_config.get('appSecret')

# Get token
resp = requests.post(
    f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal",
    json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
    timeout=30
)
token = resp.json().get('tenant_access_token')
print(f"Token: {token[:20]}...")

# Try document import API
# POST /open-apis/drive/v1/import_tasks
# This API imports files (docs, sheets, etc.) into Feishu

# For now, let's try using the wiki API to create a doc
# Wiki API: POST /open-apis/wiki/v2/spaces/{space_id}/nodes

# First, let's check what APIs are available for creating docs
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Try creating a new doc in the root folder
# POST /open-apis/docx/v1/documents
new_doc_payload = {
    "title": "企业AI本体Ontology - 知识库同步测试"
}

url = f"{FEISHU_BASE_URL}/docx/v1/documents"
resp = requests.post(url, headers=headers, json=new_doc_payload, timeout=30)
print(f"\nCreate new doc:")
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:500]}")

if resp.status_code == 200:
    result = resp.json()
    if result.get('code') == 0:
        new_doc_id = result.get('data', {}).get('document', {}).get('document_id')
        print(f"\nNew doc created: {new_doc_id}")
        print(f"URL: https://feishu.cn/docx/{new_doc_id}")
