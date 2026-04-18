# -*- coding: utf-8 -*-
import json
import requests
from pathlib import Path

config_path = Path.home() / '.openclaw' / 'openclaw.json'
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
feishu = config.get('channels', {}).get('feishu', {})

url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
resp = requests.post(url, headers={'Content-Type': 'application/json'}, 
    json={'app_id': feishu.get('appId'), 'app_secret': feishu.get('appSecret')}, timeout=10)
token = resp.json().get('tenant_access_token')
headers = {'Authorization': f'Bearer {token}'}

# 获取根目录文件列表
print('=== 云空间根目录文件 ===')
url2 = 'https://open.feishu.cn/open-apis/drive/v1/files?page_size=20&order_by=EditedTime&direction=DESC'
resp2 = requests.get(url2, headers=headers, timeout=10)
result = resp2.json()
print('Code:', result.get('code'))
if result.get('code') == 0:
    items = result.get('data', {}).get('files', [])
    print('Files count:', len(items))
    for f in items[:10]:
        name = f.get('name', 'N/A')
        ftype = f.get('type', 'N/A')
        print(f'  - {name} ({ftype})')
else:
    print('Error:', result.get('msg'))
