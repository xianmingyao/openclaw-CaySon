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

# 测试获取块 - 使用长格式
doc_id = 'IAp0djGyDoNiPlxshKwc5P1rnEf'
resp = requests.get(f'{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks', 
    headers=headers, timeout=10)
result = resp.json()
print(f'Blocks: code={result.get("code")}, msg={result.get("msg")}')
if result.get('code') == 0:
    items = result.get('data', {}).get('items', [])
    print(f'Found {len(items)} blocks')
    for item in items[:3]:
        print(f'  Block: type={item.get("block_type")}, id={item.get("block_id")}, children={len(item.get("children", []))}')
