#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""更新已有飞书文档内容"""
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

def get_doc_blocks(token: str, doc_id: str):
    """获取文档所有块"""
    url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, timeout=30)
    try:
        result = resp.json()
        if result.get('code') != 0:
            print(f"获取块失败: {result.get('msg')}")
            return None
        return result.get('data', {}).get('items', [])
    except Exception as e:
        print(f"获取块响应解析失败: {e}")
        return None

def delete_block(token: str, doc_id: str, block_id: str):
    """删除块"""
    url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{block_id}/children"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.delete(url, headers=headers, json={"start_index": 0, "end_index": 1}, timeout=30)
    try:
        result = resp.json()
        return result.get('code') == 0
    except:
        return False

def batch_delete_blocks(token: str, doc_id: str, block_ids: list):
    """批量删除块"""
    success = True
    for block_id in block_ids:
        if not delete_block(token, doc_id, block_id):
            success = False
    return success

def markdown_to_blocks(content_md: str):
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
            # 表格行，简化处理为段落
            blocks.append({"block_type": 2, "text": {"elements": [{"type": "text_run", "text_run": {"content": line}}], "style": {}}})
        else:
            blocks.append({"block_type": 2, "text": {"elements": [{"type": "text_run", "text_run": {"content": line}}], "style": {}}})
    return blocks

def update_doc(doc_id: str, content_md: str) -> bool:
    """更新文档内容"""
    token = get_token()
    if not token:
        return False
    
    # 获取现有块
    print(f"获取文档 {doc_id} 现有块...")
    blocks = get_doc_blocks(token, doc_id)
    if blocks is None:
        print("获取块失败")
        return False
    
    # 找到根block_id（page类型）
    root_block = None
    for block in blocks:
        if block.get('block_type') == 1:  # page block
            root_block = block
            break
    
    if not root_block:
        print("未找到根块")
        return False
    
    root_block_id = root_block.get('block_id')
    print(f"根块ID: {root_block_id}")
    
    # 获取子块ID列表
    children_ids = root_block.get('children', [])
    print(f"需要删除 {len(children_ids)} 个子块...")
    
    # 批量删除子块
    if children_ids:
        # 飞书API删除需要分批
        for i in range(0, len(children_ids), 10):
            batch = children_ids[i:i+10]
            for block_id in batch:
                delete_block(token, doc_id, block_id)
        print("子块已删除")
    
    # 写入新内容
    blocks = markdown_to_blocks(content_md)
    if not blocks:
        print("无内容可写入")
        return True
    
    print(f"写入 {len(blocks)} 个块...")
    url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{root_block_id}/children"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # 分批写入
    for i in range(0, len(blocks), 50):
        batch = blocks[i:i+50]
        resp = requests.post(url, headers=headers, json={"children": batch, "index": i}, timeout=30)
        try:
            result = resp.json()
            if result.get('code') != 0:
                print(f"写入失败: {result.get('msg')}")
        except Exception as e:
            print(f"写入响应解析失败: {e}")
    
    print("文档更新完成!")
    return True

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("用法: python feishu_update_doc.py <doc_id> <file_path>")
        print("示例: python feishu_update_doc.py NMOrdM7f4oZp E:\\workspace\\knowledge-base\\wiki\\概念\\GitHub一周热榜Top20-2026年第19周.md")
        sys.exit(1)
    
    doc_id = sys.argv[1]
    file_path = Path(sys.argv[2])
    
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        sys.exit(1)
    
    content = file_path.read_text(encoding='utf-8')
    
    if update_doc(doc_id, content):
        print(f"\n飞书文档已更新: https://feishu.cn/docx/{doc_id}")
    else:
        print("\n更新失败!")
        sys.exit(1)
