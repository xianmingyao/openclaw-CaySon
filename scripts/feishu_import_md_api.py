#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""使用飞书导入API导入Markdown文件"""
import os
import json
import requests

FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"

# 读取配置
config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
fc = config['channels']['feishu']

# 获取token
resp = requests.post(
    f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal",
    json={"app_id": fc['appId'], "app_secret": fc['appSecret']},
    timeout=30
)
token = resp.json().get('tenant_access_token')
print(f"Token: {token[:20]}...")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 飞书导入API - 目前支持以下格式：
# docx, doc, xlsx, csv, pptx, pdf, txt, markdown
# 需要先上传文件到云空间

# 方法1：使用导入任务API
# POST /open-apis/drive/v1/import_tasks
# 这个API需要先上传文件

# 先检查文件
source_path = r"D:\xwechat_files\XIANMINGYAO_f7ae\msg\file\2026-05\企业AI本体Ontology-从工具到Agent的关键.md"
print(f"Source: {source_path}")
print(f"Exists: {os.path.exists(source_path)}")

# 由于飞书导入API需要先上传文件到云空间，我们用另一种方式：
# 直接用drive upload API上传md文件

# 上传文件
# POST /open-apis/drive/v1/files
upload_url = f"{FEISHU_BASE_URL}/drive/v1/files"

with open(source_path, 'rb') as f:
    files = {'file': (f'企业AI本体Ontology.md', f, 'text/markdown')}
    data = {'file_name': '企业AI本体Ontology.md', 'parent_type': 'explorer', 'parent_node': 'root'}
    
    resp = requests.post(
        upload_url, 
        headers={"Authorization": f"Bearer {token}"},
        files=files,
        data=data,
        timeout=60
    )

print(f"\nUpload status: {resp.status_code}")
print(f"Response: {resp.text[:500]}")
