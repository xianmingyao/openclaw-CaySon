#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, json, requests, time
sys.stdout.reconfigure(encoding='utf-8')

FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"
config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
fc = config['channels']['feishu']

resp = requests.post(f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal",
    json={"app_id": fc['appId'], "app_secret": fc['appSecret']}, timeout=30)
token = resp.json()['tenant_access_token']
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

with open('E:/workspace/knowledge-base/wiki/概念/企业AI本体Ontology-从工具到Agent的关键.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

resp = requests.post(f"{FEISHU_BASE_URL}/docx/v1/documents", headers=headers, 
    json={"title": "企业AI本体Ontology-v1"}, timeout=30)
doc_id = resp.json()['data']['document']['document_id']
url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{doc_id}/children"

print(f"Doc: {doc_id}")
written = 0
total = len(lines)

for i, line in enumerate(lines):
    line = line.rstrip()
    if not line.strip():
        time.sleep(0.5)
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
        r = requests.post(url, headers=headers, json=block, timeout=10)
        if r.json().get('code') == 0:
            written += 1
        else:
            print(f"Err[{i}]: {r.json().get('msg')[:30]}")
    except Exception as e:
        print(f"Exc[{i}]: {str(e)[:30]}")
    
    time.sleep(1)  # 1秒间隔避免限流
    
    if (i+1) % 20 == 0:
        print(f"Progress: {i+1}/{total} (written:{written})")

print(f"\n[OK] {written}/{total} written")
print(f"URL: https://feishu.cn/docx/{doc_id}")
