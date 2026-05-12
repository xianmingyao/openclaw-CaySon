#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""同步知识库到飞书文档 - 完整版"""
import os
import json
import requests
import time

FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"

# 读取配置
config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
feishu_config = config.get('channels', {}).get('feishu', {})

# 获取token
resp = requests.post(
    f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal",
    json={"app_id": feishu_config.get('appId'), "app_secret": feishu_config.get('appSecret')},
    timeout=30
)
token = resp.json().get('tenant_access_token')
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# 读取markdown文件
md_file = 'E:/workspace/knowledge-base/wiki/概念/企业AI本体Ontology-从工具到Agent的关键.md'
with open(md_file, 'r', encoding='utf-8') as f:
    content = f.read()
print(f"Markdown: {len(content)} chars")

# 创建新文档
create_url = f"{FEISHU_BASE_URL}/docx/v1/documents"
resp = requests.post(create_url, headers=headers, json={"title": "企业AI本体Ontology - 从工具到Agent的关键"}, timeout=30)
doc_id = resp.json()['data']['document']['document_id']
print(f"Doc created: {doc_id}")

# 写入块
def write_block(doc_id, text, block_type=2, style=None):
    """写入单个块"""
    url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{doc_id}/children"
    
    # 处理文本内容（分段）
    paragraphs = []
    for para in text.split('\n'):
        para = para.strip()
        if not para:
            paragraphs.append("")
        else:
            paragraphs.append(para)
    
    results = []
    for p in paragraphs:
        if not p:
            # 空行
            block = {
                "block_type": 2,
                "text": {
                    "elements": [{"type": "text_run", "text_run": {"content": " "}}],
                    "style": {}
                }
            }
        elif p.startswith('# '):
            block = {
                "block_type": 3,
                "heading1": {
                    "elements": [{"type": "text_run", "text_run": {"content": p[2:]}}],
                    "style": {}
                }
            }
        elif p.startswith('## '):
            block = {
                "block_type": 4,
                "heading2": {
                    "elements": [{"type": "text_run", "text_run": {"content": p[3:]}}],
                    "style": {}
                }
            }
        elif p.startswith('### '):
            block = {
                "block_type": 5,
                "heading3": {
                    "elements": [{"type": "text_run", "text_run": {"content": p[4:]}}],
                    "style": {}
                }
            }
        elif p.startswith('- '):
            block = {
                "block_type": 12,
                "bullet": {
                    "elements": [{"type": "text_run", "text_run": {"content": p[2:]}}],
                    "style": {}
                }
            }
        elif p.startswith('|'):
            block = {
                "block_type": 2,
                "text": {
                    "elements": [{"type": "text_run", "text_run": {"content": p, "text_element_style": {"code": True}}}],
                    "style": {}
                }
            }
        elif p.startswith('```'):
            block = {
                "block_type": 2,
                "text": {
                    "elements": [{"type": "text_run", "text_run": {"content": p, "text_element_style": {"code": True}}}],
                    "style": {}
                }
            }
        else:
            # 普通文本，分段处理避免超长
            if len(p) > 500:
                # 分多段
                for j in range(0, len(p), 500):
                    sub_p = p[j:j+500]
                    block = {
                        "block_type": 2,
                        "text": {
                            "elements": [{"type": "text_run", "text_run": {"content": sub_p}}],
                            "style": {}
                        }
                    }
                    try:
                        resp = requests.post(url, headers=headers, json={"children": [block]}, timeout=15)
                        time.sleep(0.2)
                    except:
                        pass
                continue
            else:
                block = {
                    "block_type": 2,
                    "text": {
                        "elements": [{"type": "text_run", "text_run": {"content": p}}],
                        "style": {}
                    }
                }
        
        try:
            resp = requests.post(url, headers=headers, json={"children": [block]}, timeout=15)
            results.append(resp.json().get('code') == 0)
        except:
            results.append(False)
        time.sleep(0.15)  # 避免限流
    
    return results

# 分割内容为块
blocks = []
current = []
for line in content.split('\n'):
    if line.strip() == '':
        if current:
            blocks.append('\n'.join(current))
            current = []
    else:
        current.append(line)
if current:
    blocks.append('\n'.join(current))

print(f"Blocks to write: {len(blocks)}")

# 写入
success = 0
for i, block in enumerate(blocks):
    if len(block) < 2:
        continue
    
    results = write_block(doc_id, block)
    if any(results):
        success += 1
    
    if (i + 1) % 20 == 0:
        print(f"  Progress: {i+1}/{len(blocks)} ({success} written)")

print(f"\n[OK] {success}/{len(blocks)} blocks written")
print(f"URL: https://feishu.cn/docx/{doc_id}")
