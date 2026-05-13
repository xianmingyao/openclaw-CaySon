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
token = resp.json().get('tenant_access_token')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 测试短格式文档ID
short_ids = ['NMOrdM7f4oZp', 'CKmGdoLHEojoosxW2P3cm0m8nxh']
for doc_id in short_ids:
    resp = requests.get(f'{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}', 
        headers=headers, timeout=10)
    result = resp.json()
    print(f'Doc {doc_id}: code={result.get("code")}, msg={result.get("msg")}')
    if result.get('code') == 0:
        title = result.get('data', {}).get('document', {}).get('title')
        print(f'  Title: {title}')
        # 获取长格式ID
        resp2 = requests.get(f'{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks', 
            headers=headers, timeout=10)
        result2 = resp2.json()
        print(f'  Blocks: code={result2.get("code")}')
