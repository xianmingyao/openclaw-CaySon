#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""同步知识库到飞书文档 - 最终版"""
import os, sys, json, requests, time
sys.stdout.reconfigure(encoding='utf-8')

FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"
config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
fc = config['channels']['feishu']

# Get token
resp = requests.post(f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal",
    json={"app_id": fc['appId'], "app_secret": fc['appSecret']}, timeout=30)
token = resp.json()['tenant_access_token']
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Read file
with open('E:/workspace/knowledge-base/wiki/概念/企业AI本体Ontology-从工具到Agent的关键 - v2.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Content: {len(lines)} lines", flush=True)

# Create new doc
resp = requests.post(f"{FEISHU_BASE_URL}/docx/v1/documents", headers=headers, 
    json={"title": "企业AI本体Ontology V2.1-从工具到Agent完整指南"}, timeout=30)
doc_id = resp.json()['data']['document']['document_id']
print(f"Doc: {doc_id}", flush=True)
print(f"URL: https://feishu.cn/docx/{doc_id}", flush=True)

url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{doc_id}/children"

written = 0
errors = 0

for i, line in enumerate(lines):
    line = line.rstrip()
    if not line.strip():
        time.sleep(0.3)
        continue
    
    # Determine block type
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
        r = requests.post(url, headers=headers, json=block, timeout=15)
        if r.json().get('code') == 0:
            written += 1
        else:
            errors += 1
    except Exception as e:
        errors += 1
    
    time.sleep(1.2)
    
    if (i+1) % 10 == 0:
        print(f"Progress: {i+1}/{len(lines)} (written:{written}, errors:{errors})", flush=True)

print(f"\n[OK] Written: {written}, Errors: {errors}", flush=True)
print(f"URL: https://feishu.cn/docx/{doc_id}", flush=True)
