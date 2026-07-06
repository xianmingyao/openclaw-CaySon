#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""使用飞书API写入文档内容"""
import os
import sys
import json
import requests

DOC_ID = "AiY0dtSbyoYOUQxT1iVcGFbrnJe"

# Read content
kb_path = 'E:/workspace/knowledge-base/wiki/概念/Zilliz-Cloud企业知识库完整指南.md'
with open(kb_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Get Feishu config
config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

feishu_config = config.get('channels', {}).get('feishu', {})
FEISHU_APP_ID = feishu_config.get('appId')
FEISHU_APP_SECRET = feishu_config.get('appSecret')

# Get access token
url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
resp = requests.post(url, headers={"Content-Type": "application/json"}, 
                    json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}, timeout=10)
result = resp.json()
token = result.get('tenant_access_token')
print(f"Token: {token[:20]}...")

# 使用更简单的写入方式 - 直接用text类型block
def create_text_block(content_text):
    return {
        "block_type": 2,
        "text": {
            "elements": [{"type": "text_run", "text_run": {"content": content_text}}],
            "style": {}
        }
    }

# Build blocks from content
lines = content.split('\n')
blocks = []
for line in lines:
    if line.strip():
        blocks.append(create_text_block(line))

print(f"Created {len(blocks)} blocks")

# Write blocks in batches
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
blocks_url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{DOC_ID}/blocks/children"

success_count = 0
for i in range(0, len(blocks), 20):
    batch = blocks[i:i+20]
    payload = {"children": batch, "index": i}
    
    try:
        resp = requests.post(blocks_url, headers=headers, json=payload, timeout=30)
        resp_text = resp.text
        print(f"Batch {i}: status={resp.status_code}")
        
        if resp.status_code == 200:
            try:
                result = resp.json()
                if result.get('code') == 0:
                    success_count += len(batch)
                    print(f"  OK: {len(batch)} blocks")
                else:
                    print(f"  Error: {result}")
            except:
                print(f"  Response: {resp_text[:100]}")
    except Exception as e:
        print(f"  Exception: {e}")

print(f"\n✅ 完成! 成功写入 {success_count}/{len(blocks)} blocks")
print(f"📄 文档: https://feishu.cn/docx/{DOC_ID}")
