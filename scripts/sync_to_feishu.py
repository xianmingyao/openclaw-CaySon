#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""同步知识库到飞书文档"""
import os
import sys
import json
import requests
sys.stdout.reconfigure(encoding='utf-8')

# ============ 配置 ============
DOC_ID = "HjOVdDudOoYGycxIHKZcrMoonxe"
FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"

# 读取配置文件
config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

feishu_config = config.get('channels', {}).get('feishu', {})
FEISHU_APP_ID = feishu_config.get('appId')
FEISHU_APP_SECRET = feishu_config.get('appSecret')

# 知识库文件
KB_FILE = 'E:/workspace/knowledge-base/wiki/概念/企业AI本体Ontology-从工具到Agent的关键.md'

# ============ 获取token ============
def get_token():
    url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, headers={"Content-Type": "application/json"}, 
                        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}, timeout=30)
    return resp.json().get('tenant_access_token')

# ============ 读取知识库内容 ============
print(f"[1] Reading: {KB_FILE}")
with open(KB_FILE, 'r', encoding='utf-8') as f:
    content = f.read()
print(f"    Content length: {len(content)} chars")

# ============ 获取token ============
token = get_token()
print(f"[2] Token: {token[:20]}...")

# ============ 获取现有文档块 ============
def get_blocks(doc_id, token):
    url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=30)
    return resp.json()

# ============ 写入块 ============
def write_blocks(doc_id, blocks, token, index=0):
    url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/children"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"children": blocks, "index": index}
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    return resp.json()

# ============ 构建块 ============
def build_blocks(content):
    """将markdown内容转换为飞书文档块"""
    lines = content.split('\n')
    blocks = []
    
    for line in lines:
        line = line.rstrip()
        
        if not line:
            # 空行 - 创建空文本块
            blocks.append({
                "block_type": 2,
                "text": {
                    "elements": [{"type": "text_run", "text_run": {"content": ""}}],
                    "style": {}
                }
            })
            continue
        
        # 判断行类型
        if line.startswith('# '):
            # 一级标题
            blocks.append({
                "block_type": 3,
                "heading1": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[2:]}}],
                    "style": {}
                }
            })
        elif line.startswith('## '):
            # 二级标题
            blocks.append({
                "block_type": 4,
                "heading2": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[3:]}}],
                    "style": {}
                }
            })
        elif line.startswith('### '):
            # 三级标题
            blocks.append({
                "block_type": 5,
                "heading3": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[4:]}}],
                    "style": {}
                }
            })
        elif line.startswith('```'):
            # 代码块开始/结束
            blocks.append({
                "block_type": 2,
                "text": {
                    "elements": [{"type": "text_run", "text_run": {"content": line}}],
                    "style": {}
                }
            })
        elif line.startswith('- '):
            # 列表
            blocks.append({
                "block_type": 12,
                "bullet": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[2:]}}],
                    "style": {}
                }
            })
        elif line.startswith('|'):
            # 表格行 - 简化处理为文本
            blocks.append({
                "block_type": 2,
                "text": {
                    "elements": [{"type": "text_run", "text_run": {"content": line}}],
                    "style": {}
                }
            })
        else:
            # 普通文本
            blocks.append({
                "block_type": 2,
                "text": {
                    "elements": [{"type": "text_run", "text_run": {"content": line}}],
                    "style": {}
                }
            })
    
    return blocks

# ============ 主流程 ============
print(f"[3] Building blocks...")
blocks = build_blocks(content)
print(f"    Total blocks: {len(blocks)}")

# 获取现有块数量
print(f"[4] Getting existing blocks...")
try:
    result = get_blocks(DOC_ID, token)
    if result.get('code') == 0:
        existing_blocks = result.get('data', {}).get('items', [])
        print(f"    Existing blocks: {len(existing_blocks)}")
    else:
        print(f"    Error: {result}")
        existing_blocks = []
except Exception as e:
    print(f"    Error getting blocks: {e}")
    existing_blocks = []

# 清空现有内容（如果需要）
if existing_blocks:
    print(f"[5] Clearing existing content...")
    # 删除现有块
    try:
        delete_url = f"{FEISHU_BASE_URL}/docx/v1/documents/{DOC_ID}/blocks/batch_delete"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        # 获取块ID列表
        block_ids = [b.get('block_id') for b in existing_blocks if b.get('block_id')]
        
        if block_ids:
            payload = {"start_index": 0, "end_index": len(block_ids)}
            resp = requests.delete(delete_url, headers=headers, json=payload, timeout=30)
            print(f"    Delete result: {resp.json()}")
    except Exception as e:
        print(f"    Delete error (will try append): {e}")

# 分批写入新内容
print(f"[6] Writing new content...")
batch_size = 30
total_written = 0

for i in range(0, len(blocks), batch_size):
    batch = blocks[i:i+batch_size]
    try:
        result = write_blocks(DOC_ID, batch, token, index=i)
        if result.get('code') == 0:
            written = len(result.get('data', {}).get('children', []))
            total_written += written
            print(f"    Batch {i//batch_size + 1}: OK ({written} blocks)")
        else:
            print(f"    Batch {i//batch_size + 1}: code={result.get('code')}, msg={result.get('msg')}")
    except Exception as e:
        print(f"    Batch {i//batch_size + 1}: Exception {e}")

print(f"\n[DONE] Total written: {total_written} blocks")
print(f"Doc URL: https://feishu.cn/docx/{DOC_ID}")
