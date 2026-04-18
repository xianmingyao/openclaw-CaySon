#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速同步新建知识库文档到飞书"""
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

def create_doc(title: str, content_md: str) -> str:
    token = get_token()
    if not token:
        return None
    
    # 创建文档
    url = f"{FEISHU_BASE_URL}/docx/v1/documents"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json={"title": title}, timeout=10)
    try:
        result = resp.json()
        if result.get('code') != 0:
            print(f"创建失败: {result.get('msg')}")
            return None
        doc_id = result['data']['document']['document_id']
    except Exception as e:
        print(f"创建响应解析失败: {e}, resp={resp.text[:200]}")
        return None
    print(f"文档创建成功: {doc_id}")
    
    # 写入内容（简化版，只支持标题和段落）
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
        else:
            blocks.append({"block_type": 2, "text": {"elements": [{"type": "text_run", "text_run": {"content": line}}], "style": {}}})
    
    # 分批写入
    url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/batch_update"
    for i in range(0, len(blocks), 50):
        batch = blocks[i:i+50]
        resp = requests.post(url, headers=headers, json={"children": batch, "index": i}, timeout=30)
        try:
            result = resp.json()
            if result.get('code') != 0:
                print(f"写入失败: {result.get('msg')}")
        except:
            print(f"写入响应解析失败")
    
    return doc_id

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("用法: python sync_new_to_feishu.py <title> <file_path>")
        sys.exit(1)
    
    title = sys.argv[1]
    file_path = Path(sys.argv[2])
    
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        sys.exit(1)
    
    content = file_path.read_text(encoding='utf-8')
    doc_id = create_doc(title, content)
    
    if doc_id:
        print(f"\n飞书文档: https://feishu.cn/docx/{doc_id}")
