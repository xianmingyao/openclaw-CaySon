#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""使用飞书导入API创建文档"""
import os
import sys
import json
import requests

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
def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, headers={"Content-Type": "application/json"}, 
                        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}, timeout=10)
    return resp.json().get('tenant_access_token')

token = get_token()
print(f"Token: {token[:20]}...")

# 创建文档
def create_doc(title, token):
    url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json={"title": title}, timeout=10)
    result = resp.json()
    if result.get('code') == 0:
        return result.get('data', {}).get('document', {}).get('document_id')
    print(f"Create error: {result}")
    return None

doc_id = create_doc("Zilliz Cloud 企业知识库完整指南 v1.0", token)
print(f"Doc ID: {doc_id}")

if doc_id:
    # 使用blocks API写入内容
    def write_content(doc_id, content, token):
        url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # 构建block内容
        lines = content.split('\n')
        blocks_to_insert = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 根据行内容判断block类型
            if line.startswith('# '):
                # 一级标题
                block = {
                    "block_type": 3,
                    "heading1": {
                        "elements": [{"type": "text_run", "text_run": {"content": line[2:]}}],
                        "style": {}
                    }
                }
            elif line.startswith('## '):
                # 二级标题
                block = {
                    "block_type": 4,
                    "heading2": {
                        "elements": [{"type": "text_run", "text_run": {"content": line[3:]}}],
                        "style": {}
                    }
                }
            elif line.startswith('### '):
                # 三级标题
                block = {
                    "block_type": 5,
                    "heading3": {
                        "elements": [{"type": "text_run", "text_run": {"content": line[4:]}}],
                        "style": {}
                    }
                }
            elif line.startswith('```'):
                # 代码块（简化处理）
                block = {
                    "block_type": 2,
                    "text": {
                        "elements": [{"type": "text_run", "text_run": {"content": line}}],
                        "style": {}
                    }
                }
            elif line.startswith('- '):
                # 列表
                block = {
                    "block_type": 12,
                    "bullet": {
                        "elements": [{"type": "text_run", "text_run": {"content": line[2:]}}],
                        "style": {}
                    }
                }
            else:
                # 普通文本
                block = {
                    "block_type": 2,
                    "text": {
                        "elements": [{"type": "text_run", "text_run": {"content": line}}],
                        "style": {}
                    }
                }
            
            blocks_to_insert.append(block)
        
        # 分批写入
        batch_size = 50
        for i in range(0, len(blocks_to_insert), batch_size):
            batch = blocks_to_insert[i:i+batch_size]
            payload = {"children": batch, "index": i}
            
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=30)
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get('code') == 0:
                        print(f"Batch {i//batch_size + 1}: OK ({len(batch)} blocks)")
                    else:
                        print(f"Batch {i//batch_size + 1}: code={result.get('code')}, msg={result.get('msg')}")
                else:
                    print(f"Batch {i//batch_size + 1}: HTTP {resp.status_code}")
            except Exception as e:
                print(f"Batch {i//batch_size + 1}: Exception {e}")
        
        return len(blocks_to_insert)
    
    count = write_content(doc_id, content, token)
    print(f"\n[OK] Written {count} blocks")
    print(f"Doc URL: https://feishu.cn/docx/{doc_id}")
