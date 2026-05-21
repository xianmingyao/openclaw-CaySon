#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""将Claude Code大型项目最佳实践写入飞书文档"""
import os
import json
import requests

FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"

# 读取配置
config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
feishu_config = config.get('channels', {}).get('feishu', {})
FEISHU_APP_ID = feishu_config.get('appId')
FEISHU_APP_SECRET = feishu_config.get('appSecret')

# 获取token
resp = requests.post(
    f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal",
    json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
    timeout=30
)
token = resp.json().get('tenant_access_token')
print(f"[1] Token: {token[:20]}...")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 读取markdown内容
md_file = 'E:/workspace/knowledge-base/Claude Code大型项目最佳实践-2026-05-21.md'
with open(md_file, 'r', encoding='utf-8') as f:
    md_content = f.read()
print(f"[2] Markdown: {len(md_content)} chars")

# 创建文档
title = "Claude Code大型项目最佳实践（2026-05-21）"
create_url = f"{FEISHU_BASE_URL}/docx/v1/documents"
create_payload = {"title": title}
resp = requests.post(create_url, headers=headers, json=create_payload, timeout=30)
print(f"[3] Create doc: {resp.status_code}")
print(f"Response: {resp.text[:500]}")

if resp.status_code == 200 and resp.json().get('code') == 0:
    doc_id = resp.json().get('data', {}).get('document', {}).get('document_id')
    print(f"[4] Doc ID: {doc_id}")
    
    # 获取根block
    block_url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks"
    resp = requests.get(block_url, headers=headers, timeout=30)
    if resp.status_code == 200:
        blocks = resp.json().get('data', {}).get('items', [])
        if blocks:
            root_block_id = blocks[0].get('block_id')
            print(f"[5] Root block: {root_block_id}")
            
            # 构建飞书block格式
            # 简化：使用paragraph插入markdown内容
            lines = md_content.split('\n')
            blocks_to_insert = []
            
            for line in lines:
                if line.startswith('# '):
                    blocks_to_insert.append({
                        "block_type": 2,  # heading1
                        "heading1": {
                            "elements": [{"type": "text_run", "text_run": {"content": line[2:], "text_element_style": {}}}],
                            "style": {}
                        }
                    })
                elif line.startswith('## '):
                    blocks_to_insert.append({
                        "block_type": 3,  # heading2
                        "heading2": {
                            "elements": [{"type": "text_run", "text_run": {"content": line[3:], "text_element_style": {}}}],
                            "style": {}
                        }
                    })
                elif line.startswith('### '):
                    blocks_to_insert.append({
                        "block_type": 4,  # heading3
                        "heading3": {
                            "elements": [{"type": "text_run", "text_run": {"content": line[4:], "text_element_style": {}}}],
                            "style": {}
                        }
                    })
                elif line.startswith('> '):
                    blocks_to_insert.append({
                        "block_type": 14,  # quote
                        "quote": {
                            "elements": [{"type": "text_run", "text_run": {"content": line[2:], "text_element_style": {}}}],
                            "style": {}
                        }
                    })
                elif line.startswith('- '):
                    blocks_to_insert.append({
                        "block_type": 12,  # bullet
                        "bullet": {
                            "elements": [{"type": "text_run", "text_run": {"content": line[2:], "text_element_style": {}}}],
                            "style": {}
                        }
                    })
                elif line.startswith('```'):
                    # 代码块开始/结束，跳过
                    continue
                elif line.strip().startswith('|'):
                    # 表格行，简化为paragraph
                    clean_line = line.replace('|', ' ').strip()
                    if clean_line and not clean_line.startswith('-'):
                        blocks_to_insert.append({
                            "block_type": 2,
                            "paragraph": {
                                "elements": [{"type": "text_run", "text_run": {"content": clean_line, "text_element_style": {}}}],
                                "style": {}
                            }
                        })
                elif line.strip().startswith('**') and line.strip().endswith('**'):
                    # 加粗行
                    clean = line.strip()[2:-2]
                    blocks_to_insert.append({
                        "block_type": 2,
                        "paragraph": {
                            "elements": [{"type": "text_run", "text_run": {"content": clean, "text_element_style": {"bold": True}}}],
                            "style": {}
                        }
                    })
                elif line.strip() == '---':
                    blocks_to_insert.append({
                        "block_type": 27,  # divider
                        "divider": {}
                    })
                elif line.strip() == '':
                    # 空行
                    blocks_to_insert.append({
                        "block_type": 2,
                        "paragraph": {
                            "elements": [{"type": "text_run", "text_run": {"content": " ", "text_element_style": {}}}],
                            "style": {}
                        }
                    })
                else:
                    # 普通文本
                    clean_line = line.strip()
                    if clean_line:
                        blocks_to_insert.append({
                            "block_type": 2,
                            "paragraph": {
                                "elements": [{"type": "text_run", "text_run": {"content": clean_line, "text_element_style": {}}}],
                                "style": {}
                            }
                        })
            
            # 批量插入blocks
            insert_url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{root_block_id}/children"
            insert_payload = {
                "children": blocks_to_insert[:50],  # 限制50个
                "index": 0
            }
            resp = requests.post(insert_url, headers=headers, json=insert_payload, timeout=30)
            print(f"[6] Insert blocks: {resp.status_code}")
            if resp.status_code == 200:
                print(f"[7] Success! Doc URL: https://feishu.cn/docx/{doc_id}")
            else:
                print(f"Error: {resp.text[:500]}")
    else:
        print(f"Get blocks error: {resp.text[:300]}")
else:
    print(f"Create doc failed: {resp.text[:500]}")
