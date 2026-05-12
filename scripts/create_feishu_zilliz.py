#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""使用飞书API创建Zilliz知识库文档"""
import os
import sys
import json
import requests

# Read content
kb_path = 'E:/workspace/knowledge-base/wiki/概念/Zilliz-Cloud企业知识库完整指南.md'
with open(kb_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"读取文件: {kb_path}")
print(f"长度: {len(content)} 字符")

# Get Feishu config
config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

feishu_config = config.get('channels', {}).get('feishu', {})
FEISHU_APP_ID = feishu_config.get('appId')
FEISHU_APP_SECRET = feishu_config.get('appSecret')

print(f"App ID: {FEISHU_APP_ID}")

# Get access token
def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, headers={"Content-Type": "application/json"}, 
                        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}, timeout=10)
    result = resp.json()
    if result.get('code') == 0:
        return result.get('tenant_access_token')
    print(f"Token error: {result}")
    return None

token = get_token()
print(f"Got token: {token[:20]}...")

# Create document
def create_doc(title, token):
    url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, 
                        json={"title": title}, timeout=10)
    result = resp.json()
    print(f"Create response: {result}")
    if result.get('code') == 0:
        return result.get('data', {}).get('document', {}).get('document_id')
    return None

doc_id = create_doc("Zilliz Cloud 企业知识库完整指南 v1.0", token)
print(f"Created doc_id: {doc_id}")

if doc_id:
    # Write content using blocks
    def write_blocks(doc_id, content, token):
        url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # Split content into lines and create simple text blocks
        lines = content.split('\n')
        blocks = []
        for line in lines:
            if line.strip():
                blocks.append({
                    "block_type": 2,  # text block
                    "text": {
                        "elements": [{"type": "text_run", "text_run": {"content": line}}],
                        "style": {}
                    }
                })
        
        # Create blocks in batches
        for i in range(0, len(blocks), 50):
            batch = blocks[i:i+50]
            resp = requests.post(url, headers=headers, 
                              json={"children": batch, "index": i}, timeout=30)
            result = resp.json()
            if result.get('code') != 0:
                print(f"Write error at {i}: {result}")
        
        print(f"Wrote {len(blocks)} blocks")
        return True
    
    write_blocks(doc_id, content, token)
    print(f"\n✅ 飞书文档创建成功!")
    print(f"📄 文档链接: https://feishu.cn/docx/{doc_id}")
