#!/usr/bin/env python
import os, json, requests

FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"
config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
feishu_config = config.get('channels', {}).get('feishu', {})
FEISHU_APP_ID = feishu_config.get('appId')
FEISHU_APP_SECRET = feishu_config.get('appSecret')

resp = requests.post(f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal",
    json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}, timeout=30)
token = resp.json().get('tenant_access_token')
print(f"[1] Token: {token[:20]}...")

headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
title = "GitHub热榜新项目（2026-04-13）"
resp = requests.post(f"{FEISHU_BASE_URL}/docx/v1/documents", headers=headers, json={"title": title}, timeout=30)
print(f"[2] Create doc: {resp.status_code}")

if resp.status_code == 200 and resp.json().get('code') == 0:
    doc_id = resp.json().get('data', {}).get('document', {}).get('document_id')
    print(f"[3] Doc ID: {doc_id}")
    print(f"[4] Success! Doc URL: https://feishu.cn/docx/{doc_id}")
else:
    print(f"Create doc failed: {resp.text[:500]}")
