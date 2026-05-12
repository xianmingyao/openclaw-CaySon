#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""同步知识库到飞书文档 - 简化版"""
import os
import json
import requests
import time

FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"

config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
feishu_config = config.get('channels', {}).get('feishu', {})

resp = requests.post(
    f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal",
    json={"app_id": feishu_config.get('appId'), "app_secret": feishu_config.get('appSecret')},
    timeout=30
)
token = resp.json().get('tenant_access_token')
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 读取文件
with open('E:/workspace/knowledge-base/wiki/概念/企业AI本体Ontology-从工具到Agent的关键.md', 'r', encoding='utf-8') as f:
    content = f.read()
print(f"Content: {len(content)} chars")

# 创建文档
resp = requests.post(f"{FEISHU_BASE_URL}/docx/v1/documents", headers=headers, json={"title": "企业AI本体Ontology"}, timeout=30)
doc_id = resp.json()['data']['document']['document_id']
print(f"Doc: {doc_id}")

url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{doc_id}/children"

# 按行处理
lines = content.split('\n')
batch = []
batch_size = 10

for i, line in enumerate(lines):
    line = line.rstrip()
    
    # 判断类型
    if line.startswith('# '):
        block_type = 3
        text = line[2:]
    elif line.startswith('## '):
        block_type = 4
        text = line[3:]
    elif line.startswith('### '):
        block_type = 5
        text = line[4:]
    elif line.startswith('- '):
        block_type = 12
        text = line[2:]
    else:
        block_type = 2
        text = line
    
    if not text.strip():
        continue
    
    # 截断超长文本
    if len(text) > 500:
        text = text[:500]
    
    block = {
        "children": [{
            "block_type": block_type,
            "text": {
                "elements": [{"type": "text_run", "text_run": {"content": text}}],
                "style": {}
            }
        }]
    }
    batch.append(block)
    
    if len(batch) >= batch_size:
        try:
            resp = requests.post(url, headers=headers, json={"children": batch}, timeout=15)
            if resp.json().get('code') == 0:
                pass
            else:
                print(f"Error: {resp.json().get('msg')}")
        except Exception as e:
            print(f"Exception: {e}")
        batch = []
        time.sleep(0.3)
    
    if (i + 1) % 50 == 0:
        print(f"Progress: {i+1}/{len(lines)}")

# 发送剩余
if batch:
    try:
        requests.post(url, headers=headers, json={"children": batch}, timeout=15)
    except:
        pass

print(f"\n[OK] Done!")
print(f"URL: https://feishu.cn/docx/{doc_id}")
