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

print(f'App ID: {app_id[:10]}...')

# 获取token
resp = requests.post(f'{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal', 
    json={'app_id': app_id, 'app_secret': app_secret}, timeout=10)
result = resp.json()
print(f'Token response: code={result.get("code")}, msg={result.get("msg")}')

if result.get('tenant_access_token'):
    token = result['tenant_access_token']
    # 测试获取文档
    doc_id = 'NMOrdM7f4oZp'
    resp = requests.get(f'{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}', 
        headers={'Authorization': f'Bearer {token}'}, timeout=10)
    doc_result = resp.json()
    print(f'Doc response: code={doc_result.get("code")}, msg={doc_result.get("msg")}')
    
    if doc_result.get('code') == 0:
        print(f'Document title: {doc_result.get("data", {}).get("document", {}).get("title")}')
        
        # 获取块
        resp = requests.get(f'{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks', 
            headers={'Authorization': f'Bearer {token}'}, timeout=10)
        blocks_result = resp.json()
        print(f'Blocks response: code={blocks_result.get("code")}, msg={blocks_result.get("msg")}')
        if blocks_result.get('code') == 0:
            items = blocks_result.get('data', {}).get('items', [])
            print(f'Found {len(items)} blocks')
