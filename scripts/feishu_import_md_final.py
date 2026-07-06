#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""飞书导入API导入Markdown文件"""
import os
import json
import requests

FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"
config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
fc = config['channels']['feishu']

# Get token
resp = requests.post(f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal",
    json={"app_id": fc['appId'], "app_secret": fc['appSecret']}, timeout=30)
token = resp.json().get('tenant_access_token')
print(f"Token: {token[:20]}...")

headers = {
    "Authorization": f"Bearer {token}"
}

source = r"D:\xwechat_files\XIANMINGYAO_f7ae\msg\file\2026-05\企业AI本体Ontology-从工具到Agent的关键.md"

# 方法1：尝试使用导入任务API
# POST /open-apis/drive/v1/import_tasks
print("\n[1] Testing import tasks API...")
import_url = f"{FEISHU_BASE_URL}/drive/v1/import_tasks"

# 首先尝试直接创建文档
print("\n[2] Creating document directly...")
create_url = f"{FEISHU_BASE_URL}/docx/v1/documents"
resp = requests.post(create_url, headers=headers, json={"title": "企业AI本体Ontology-从工具到Agent的关键"}, timeout=30)
print(f"Create status: {resp.status_code}")

if resp.status_code == 200:
    result = resp.json()
    if result.get('code') == 0:
        doc_id = result['data']['document']['document_id']
        print(f"Doc ID: {doc_id}")
        print(f"URL: https://feishu.cn/docx/{doc_id}")
        
        # 读取文件内容并写入
        with open(source, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"\n[3] Writing {len(lines)} lines to document...")
        blocks_url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{doc_id}/children"
        
        written = 0
        for i, line in enumerate(lines):
            line = line.rstrip()
            if not line.strip():
                continue
            
            if line.startswith('# '):
                bt = 3; text = line[2:]
            elif line.startswith('## '):
                bt = 4; text = line[3:]
            elif line.startswith('### '):
                bt = 5; text = line[4:]
            elif line.startswith('- '):
                bt = 12; text = line[2:]
            else:
                bt = 2; text = line
            
            if len(text) > 500:
                text = text[:500]
            
            block = {"children": [{"block_type": bt, "text": {"elements": [{"type": "text_run", "text_run": {"content": text}}], "style": {}}}]}
            
            try:
                r = requests.post(blocks_url, headers=headers, json=block, timeout=10)
                if r.json().get('code') == 0:
                    written += 1
            except:
                pass
        
        print(f"[OK] Written: {written}")
        print(f"URL: https://feishu.cn/docx/{doc_id}")
    else:
        print(f"Error: {result.get('msg')}")
else:
    print(f"Create failed: {resp.text}")
