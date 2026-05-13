#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
飞书文档更新脚本 - 支持创建和更新已有文档
用法:
    python feishu_upsert.py <doc_id_or_url> <md_file_path>
    python feishu_upsert.py new <title> <md_file_path>
示例:
    python feishu_upsert.py new "我的文档" E:/workspace/test.md
    python feishu_upsert.py https://feishu.cn/docx/xxx test.md
"""
import json
import requests
from pathlib import Path

FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"
TOKEN_FILE = Path.home() / ".openclaw" / "openclaw.json"

def get_token():
    try:
        with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        feishu = config.get('channels', {}).get('feishu', {})
        app_id = feishu.get('appId')
        app_secret = feishu.get('appSecret')
        
        url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
        resp = requests.post(url, headers={"Content-Type": "application/json"},
            json={"app_id": app_id, "app_secret": app_secret}, timeout=10)
        result = resp.json()
        return result.get('tenant_access_token')
    except Exception as e:
        print(f"获取token失败: {e}")
        return None

def md_to_blocks(content_md):
    """将markdown转换为飞书块"""
    blocks = []
    lines = content_md.split('\n')
    for line in lines:
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
            blocks.append({"block_type": 2, "text": {"elements": [{"type": "text_run", "text_run": {"content": line}}}], "style": {}}})
        else:
            blocks.append({"block_type": 2, "text": {"elements": [{"type": "text_run", "text_run": {"content": line}}}], "style": {}}})
    return blocks

def create_doc(title, content):
    """创建新文档"""
    token = get_token()
    if not token:
        return None
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 创建文档
    url = f"{FEISHU_BASE_URL}/docx/v1/documents"
    resp = requests.post(url, headers=headers, json={"title": title}, timeout=10)
    result = resp.json()
    if result.get('code') != 0:
        print(f"创建失败: {result.get('msg')}")
        return None
    
    doc_id = result['data']['document']['document_id']
    print(f"文档创建成功: {doc_id}")
    
    # 获取根block_id
    resp = requests.get(f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks", 
        headers=headers, timeout=10)
    root_result = resp.json()
    root_block_id = root_result['data']['items'][0]['block_id']
    
    # 写入内容
    blocks = md_to_blocks(content)
    url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{root_block_id}/children"
    for i in range(0, len(blocks), 50):
        batch = blocks[i:i+50]
        resp = requests.post(url, headers=headers, json={"children": batch, "index": i}, timeout=30)
    
    return doc_id

def update_doc(doc_id, content):
    """更新已有文档"""
    token = get_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 获取文档块
    resp = requests.get(f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks", 
        headers=headers, timeout=10)
    result = resp.json()
    if result.get('code') != 0:
        print(f"获取块失败: {result.get('msg')}")
        return False
    
    items = result.get('data', {}).get('items', [])
    if not items:
        print("文档为空")
        return False
    
    # 找根块
    root_block = None
    for item in items:
        if item.get('block_type') == 1:
            root_block = item
            break
    
    if not root_block:
        print("未找到根块")
        return False
    
    root_block_id = root_block.get('block_id')
    children_ids = root_block.get('children', [])
    
    # 删除现有子块
    for block_id in children_ids:
        requests.delete(f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{block_id}/children",
            headers=headers, json={"start_index": 0, "end_index": 1}, timeout=10)
    
    # 写入新内容
    blocks = md_to_blocks(content)
    url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{root_block_id}/children"
    for i in range(0, len(blocks), 50):
        batch = blocks[i:i+50]
        requests.post(url, headers=headers, json={"children": batch, "index": i}, timeout=30)
    
    print("文档更新成功!")
    return True

def extract_doc_id(doc_id_or_url):
    """从URL或直接ID中提取文档ID"""
    if doc_id_or_url.startswith('http'):
        # 从URL提取
        parts = doc_id_or_url.split('/')
        return parts[-1]
    return doc_id_or_url

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    doc_id_or_title = sys.argv[1]
    file_path = Path(sys.argv[2])
    
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        sys.exit(1)
    
    content = file_path.read_text(encoding='utf-8')
    
    if doc_id_or_title == 'new' or doc_id_or_title == 'new':
        # 创建新文档
        title = file_path.stem  # 使用文件名作为标题
        doc_id = create_doc(title, content)
        if doc_id:
            print(f"\n飞书文档: https://feishu.cn/docx/{doc_id}")
    else:
        # 更新文档
        doc_id = extract_doc_id(doc_id_or_title)
        if update_doc(doc_id, content):
            print(f"\n飞书文档已更新: https://feishu.cn/docx/{doc_id}")
        else:
            print("\n更新失败!")
