#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速同步新建知识库文档到飞书 v2"""
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
        url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
        resp = requests.post(url, headers={"Content-Type": "application/json"},
            json={"app_id": feishu.get('appId'), "app_secret": feishu.get('appSecret')}, timeout=10)
        return resp.json().get('tenant_access_token')
    except Exception as e:
        print(f"获取token失败: {e}")
        return None

def create_and_fill_doc(title: str, content_md: str) -> str:
    token = get_token()
    if not token:
        return None
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 1. 创建文档
    url = f"{FEISHU_BASE_URL}/docx/v1/documents"
    resp = requests.post(url, headers=headers, json={"title": title}, timeout=10)
    try:
        result = resp.json()
        if result.get('code') != 0:
            print(f"创建失败: {result.get('msg')}")
            return None
        doc_id = result['data']['document']['document_id']
    except Exception as e:
        print(f"创建响应解析失败: {e}")
        return None
    
    print(f"文档创建成功: {doc_id}")
    
    # 2. 转换markdown为blocks
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
        elif line.startswith('>'):
            blocks.append({"block_type": 12, "bullet": {"elements": [{"type": "text_run", "text_run": {"content": line[1:].strip()}}], "style": {}}})
        elif line.startswith('```'):
            blocks.append({"block_type": 12, "bullet": {"elements": [{"type": "text_run", "text_run": {"content": "[代码块]"}}], "style": {}}})
        elif line.startswith('|'):
            blocks.append({"block_type": 12, "bullet": {"elements": [{"type": "text_run", "text_run": {"content": line}}], "style": {}}})
        else:
            blocks.append({"block_type": 2, "text": {"elements": [{"type": "text_run", "text_run": {"content": line[:500]}}], "style": {}}})
    
    # 3. 批量写入blocks (每批50个)
    url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/batch_update"
    for i in range(0, len(blocks), 50):
        batch = blocks[i:i+50]
        payload = {"children": batch, "index": i}
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        try:
            result = resp.json()
            if result.get('code') != 0:
                print(f"  写入批次{i//50+1}失败: {result.get('msg')[:50]}")
        except Exception as e:
            print(f"  写入批次{i//50+1}响应解析失败")
    
    return doc_id

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("用法: python sync_new_to_feishu_v2.py <title> <file_path>")
        sys.exit(1)
    
    title = sys.argv[1]
    file_path = Path(sys.argv[2])
    
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        sys.exit(1)
    
    content = file_path.read_text(encoding='utf-8')
    doc_id = create_and_fill_doc(title, content)
    
    if doc_id:
        print(f"\n✅ 飞书文档创建成功!")
        print(f"📎 链接: https://feishu.cn/docx/{doc_id}")
