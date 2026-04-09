#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
飞书文档同步脚本 v5
使用可用的 block 格式：heading1, heading2, heading3, bullet, code
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

WIKI_DIR = Path(__file__).parent / "wiki"
FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"

FEISHU_APP_ID = None
FEISHU_APP_SECRET = None
TENANT_ACCESS_TOKEN = None


def get_feishu_config():
    global FEISHU_APP_ID, FEISHU_APP_SECRET
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding='utf-8'))
        feishu_config = config.get('channels', {}).get('feishu', {})
        FEISHU_APP_ID = feishu_config.get('appId')
        FEISHU_APP_SECRET = feishu_config.get('appSecret')


def get_tenant_access_token() -> str:
    global TENANT_ACCESS_TOKEN
    if TENANT_ACCESS_TOKEN:
        return TENANT_ACCESS_TOKEN
    get_feishu_config()
    if not FEISHU_APP_ID or not FEISHU_APP_SECRET:
        return None
    url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, headers={"Content-Type": "application/json"},
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}, timeout=10)
    result = resp.json()
    if result.get('code') == 0:
        TENANT_ACCESS_TOKEN = result.get('tenant_access_token')
        return TENANT_ACCESS_TOKEN
    return None


def create_doc(title: str) -> dict:
    token = get_tenant_access_token()
    if not token:
        return {'success': False, 'error': 'No token'}
    url = f"{FEISHU_BASE_URL}/docx/v1/documents"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json={"title": title}, timeout=10)
    result = resp.json()
    if result.get('code') == 0:
        doc_id = result.get('data', {}).get('document', {}).get('document_id')
        return {'success': True, 'doc_id': doc_id, 'title': title}
    return {'success': False, 'error': result.get('msg')}


def markdown_to_blocks(markdown: str) -> list:
    """将 markdown 转换为飞书文档块（仅使用支持的格式）"""
    blocks = []
    lines = markdown.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].rstrip()
        
        if not line.strip():
            i += 1
            continue
        
        # 标题 - 全部转为 heading1
        if line.startswith('# '):
            blocks.append({
                "block_type": 3,
                "heading1": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[2:]}}],
                    "style": {}
                }
            })
        elif line.startswith('## '):
            blocks.append({
                "block_type": 4,
                "heading2": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[3:]}}],
                    "style": {}
                }
            })
        elif line.startswith('### '):
            blocks.append({
                "block_type": 5,
                "heading3": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[4:]}}],
                    "style": {}
                }
            })
        # 无序列表
        elif line.startswith('- '):
            blocks.append({
                "block_type": 12,
                "bullet": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[2:]}}],
                    "style": {}
                }
            })
        # 引用行 - 转为 bullet
        elif line.startswith('>'):
            blocks.append({
                "block_type": 12,
                "bullet": {
                    "elements": [{"type": "text_run", "text_run": {"content": "  " + line[1:].strip()}}],
                    "style": {}
                }
            })
        # 代码块 - 转为 bullet（跳过内容）
        elif line.startswith('```'):
            blocks.append({
                "block_type": 12,
                "bullet": {
                    "elements": [{"type": "text_run", "text_run": {"content": "[代码块] " + line[3:].strip() if len(line) > 3 else "[代码块]"}}],
                    "style": {}
                }
            })
        # 水平线 - 跳过
        elif line.startswith('---') or line.startswith('***'):
            pass
        # 普通段落 - 转为 bullet
        else:
            # 跳过表格行和特殊字符过多的行
            clean = line.strip()
            if clean and len(clean) < 500:
                blocks.append({
                    "block_type": 12,
                    "bullet": {
                        "elements": [{"type": "text_run", "text_run": {"content": clean}}],
                        "style": {}
                    }
                })
        
        i += 1
    
    return blocks


def write_blocks(doc_id: str, blocks: list) -> dict:
    """写入 blocks 到文档"""
    token = get_tenant_access_token()
    if not token:
        return {'success': False, 'error': 'No token'}
    
    # 获取 page block id
    resp = requests.get(
        f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks",
        headers={"Authorization": f"Bearer {token}"}, timeout=10)
    items = resp.json().get('data', {}).get('items', [])
    page_block_id = items[0].get('block_id', doc_id) if items else doc_id
    
    # 分批写入（每次最多10个block）
    batch_size = 10
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i+batch_size]
        url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{page_block_id}/children"
        resp = requests.post(url,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"children": batch, "index": -1}, timeout=30)
        result = resp.json()
        if result.get('code') != 0:
            return {'success': False, 'error': result.get('msg'), 'code': result.get('code')}
    
    return {'success': True}


def load_wiki_files():
    return list(WIKI_DIR.rglob("*.md"))


def read_wiki_content(file_path: Path) -> dict:
    return {
        'title': file_path.stem,
        'content': file_path.read_text(encoding='utf-8'),
        'path': str(file_path.relative_to(WIKI_DIR))
    }


def main():
    print("=" * 50)
    print("FEISHU DOC SYNC v5")
    print("=" * 50)
    
    token = get_tenant_access_token()
    if not token:
        print("[ERROR] Cannot get token")
        return
    print("[OK] Token acquired")
    
    wiki_files = load_wiki_files()
    print(f"[LOAD] Found {len(wiki_files)} files")
    
    if not wiki_files:
        print("[WARN] No wiki files")
        return
    
    print("\n[SYNC] Syncing to Feishu...")
    results = []
    
    for wiki_file in wiki_files:
        doc_data = read_wiki_content(wiki_file)
        print(f"\n   [{len(results)+1}/{len(wiki_files)}] {doc_data['title']}")
        
        # 创建文档
        create_result = create_doc(doc_data['title'])
        if not create_result.get('success'):
            print(f"   [FAIL] Create: {create_result.get('error')}")
            results.append({'title': doc_data['title'], 'success': False, 'error': create_result.get('error')})
            continue
        
        doc_id = create_result.get('doc_id')
        print(f"   [OK] Doc: {doc_id}")
        
        # 转换并写入 blocks
        blocks = markdown_to_blocks(doc_data['content'])
        write_result = write_blocks(doc_id, blocks)
        
        if write_result.get('success'):
            print(f"   [OK] Content written ({len(blocks)} blocks)")
        else:
            print(f"   [WARN] Write: {write_result.get('error')}")
        
        results.append({
            'title': doc_data['title'],
            'doc_id': doc_id,
            'url': f"https://feishu.cn/docx/{doc_id}",
            'success': write_result.get('success', False)
        })
    
    print("\n" + "=" * 50)
    success_count = sum(1 for r in results if r.get('success'))
    print(f"[DONE] Success: {success_count}/{len(results)}")
    
    for r in results:
        status = "[OK]" if r.get('success') else "[WARN]"
        print(f"   {status} {r['title']}")
        if r.get('url'):
            print(f"      {r['url']}")


if __name__ == '__main__':
    main()
