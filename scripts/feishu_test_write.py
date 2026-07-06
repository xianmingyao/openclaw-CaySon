#!/usr/bin/env python
import os, json, requests

FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"
config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r') as f:
    config = json.load(f)
fc = config['channels']['feishu']

resp = requests.post(f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal",
    json={"app_id": fc['appId'], "app_secret": fc['appSecret']}, timeout=30)
token = resp.json()['tenant_access_token']
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 创建文档
resp = requests.post(f"{FEISHU_BASE_URL}/docx/v1/documents", headers=headers, json={"title": "企业AI本体测试"}, timeout=30)
print(f"Create: {resp.status_code} {resp.json()}")
doc_id = resp.json()['data']['document']['document_id']

# 写入测试块
url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{doc_id}/children"
block = {"children": [{"block_type": 2, "text": {"elements": [{"type": "text_run", "text_run": {"content": "Test from API"}}], "style": {}}}]}
resp = requests.post(url, headers=headers, json=block, timeout=15)
print(f"Write: {resp.status_code} {resp.json()}")

print(f"URL: https://feishu.cn/docx/{doc_id}")
