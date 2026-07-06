#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests
from pathlib import Path

TOKEN_FILE = Path.home() / '.openclaw' / 'openclaw.json'
FEISHU_BASE_URL = 'https://open.feishu.cn/open-apis'

with open(TOKEN_FILE, 'r') as f:
    config = json.load(f)
feishu = config.get('channels', {}).get('feishu', {})
app_id = feishu.get('appId')
app_secret = feishu.get('appSecret')

# 获取token
resp = requests.post(f'{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal', 
    json={'app_id': app_id, 'app_secret': app_secret}, timeout=10)
result = resp.json()
token = result.get('tenant_access_token')

if token:
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # 测试创建文档
    resp = requests.post(f'{FEISHU_BASE_URL}/docx/v1/documents', 
        headers=headers, json={'title': 'Test Update Script'}, timeout=10)
    create_result = resp.json()
    print(f'Create response: code={create_result.get("code")}, msg={create_result.get("msg")}')
    
    if create_result.get('code') == 0:
        new_doc_id = create_result['data']['document']['document_id']
        print(f'New doc ID: {new_doc_id}')
        print(f'URL: https://feishu.cn/docx/{new_doc_id}')
