#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""同步 Hermes Agent 184专家团队 到飞书"""
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

resp = requests.post(
    f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal",
    json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
    timeout=30
)
token = resp.json().get('tenant_access_token')
print(f"[1] Token: {token[:20]}...")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

title = "Hermes Agent · 184专家团队深度解析（2026-01-18）"
create_url = f"{FEISHU_BASE_URL}/docx/v1/documents"
create_payload = {"title": title}
resp = requests.post(create_url, headers=headers, json=create_payload, timeout=30)
print(f"[2] Create doc: {resp.status_code}")

if resp.status_code == 200 and resp.json().get('code') == 0:
    doc_id = resp.json().get('data', {}).get('document', {}).get('document_id')
    print(f"[3] Doc ID: {doc_id}")
    print(f"[4] Success! Doc URL: https://feishu.cn/docx/{doc_id}")
else:
    print(f"Create doc failed: {resp.text[:500]}")
