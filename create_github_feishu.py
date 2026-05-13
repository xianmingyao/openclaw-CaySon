#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests
from pathlib import Path

TOKEN_FILE = Path.home() / '.openclaw' / 'openclaw.json'
FEISHU_BASE_URL = 'https://open.feishu.cn/open-apis'

with open(TOKEN_FILE, 'r') as f:
    config = json.load(f)
feishu = config.get('channels', {}).get('feishu', {})
app_id = feishu.get('appId')
app_secret = feishu.get('appSecret')

# 获取token
resp = requests.post(f'{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal', 
    json={'app_id': app_id, 'app_secret': app_secret}, timeout=10)
token = resp.json().get('tenant_access_token')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 读取知识库内容
kb_path = Path('E:/workspace/knowledge-base/wiki/概念/GitHub一周热榜Top20-2026年第19周.md')
content = kb_path.read_text(encoding='utf-8')

# 创建新文档
resp = requests.post(f'{FEISHU_BASE_URL}/docx/v1/documents', 
    headers=headers, json={'title': 'GitHub一周热榜Top20-2026年第19周（完整版）'}, timeout=10)
result = resp.json()
print(f'Create: code={result.get("code")}')
if result.get('code') == 0:
    new_doc_id = result['data']['document']['document_id']
    print(f'New doc ID: {new_doc_id}')
    print(f'URL: https://feishu.cn/docx/{new_doc_id}')
    
    # 写入内容
    def md_to_blocks(md):
        blocks = []
        for line in md.split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.startswith('# '):
                blocks.append({"block_type": 3, "heading1": {"elements": [{"type": "text_run", "text_run": {"content": line[2:]}}], "style": {}}})
            elif line.startswith('## '):
                blocks.append({"block_type": 4, "heading2": {"elements": [{"type": "text_run", "text_run": {"content": line[3:]}}], "style": {}}})
            elif line.startswith('### '):
                blocks.append({"block_type": 5, "heading3": {"elements": [{"type": "text_run", "text_run": {"content": line[4:]}}], "style": {}}})
            elif line.startswith('- '):
                blocks.append({"block_type": 12, "bullet": {"elements": [{"type": "text_run", "text_run": {"content": line[2:]}}], "style": {}}})
            elif line.startswith('| '):
                blocks.append({"block_type": 2, "text": {"elements": [{"type": "text_run", "text_run": {"content": line}}], "style": {}}})
            else:
                blocks.append({"block_type": 2, "text": {"elements": [{"type": "text_run", "text_run": {"content": line}}], "style": {}}})
        return blocks
    
    blocks = md_to_blocks(content)
    print(f'Writing {len(blocks)} blocks...')
    
    # 获取根block_id
    resp = requests.get(f'{FEISHU_BASE_URL}/docx/v1/documents/{new_doc_id}/blocks', 
        headers=headers, timeout=10)
    root_result = resp.json()
    root_block_id = root_result['data']['items'][0]['block_id']
    
    # 写入
    url = f'{FEISHU_BASE_URL}/docx/v1/documents/{new_doc_id}/blocks/{root_block_id}/children'
    for i in range(0, len(blocks), 50):
        batch = blocks[i:i+50]
        resp = requests.post(url, headers=headers, json={"children": batch, "index": i}, timeout=30)
    
    print('Done!')
