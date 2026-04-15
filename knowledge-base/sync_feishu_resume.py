#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
飞书文档同步脚本 v6 - 支持断点续传
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

WIKI_DIR = Path(__file__).parent / "wiki"
FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"
STATE_FILE = Path(__file__).parent / ".sync_state.json"

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


def load_sync_state():
    """加载同步状态"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    return {'synced': {}, 'failed': {}}


def save_sync_state(state):
    """保存同步状态"""
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def is_synced(title, state):
    """检查文档是否已同步"""
    return title in state.get('synced', {})


def mark_synced(title, doc_id, url, state):
    """标记文档已同步"""
    if 'synced' not in state:
        state['synced'] = {}
    state['synced'][title] = {'doc_id': doc_id, 'url': url, 'synced_at': datetime.now().isoformat()}


def mark_failed(title, error, state):
    """标记文档同步失败"""
    if 'failed' not in state:
        state['failed'] = {}
    state['failed'][title] = {'error': error, 'failed_at': datetime.now().isoformat()}


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
    """将 markdown 转换为飞书文档块"""
    blocks = []
    lines = markdown.split('\n')
    
    for line in lines:
        line = line.rstrip()
        
        if not line.strip():
            continue
        
        if line.startswith('# '):
            blocks.append({
                "block_type": 3, "heading1": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[2:]}}], "style": {}
                }
            })
        elif line.startswith('## '):
            blocks.append({
                "block_type": 4, "heading2": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[3:]}}], "style": {}
                }
            })
        elif line.startswith('### '):
            blocks.append({
                "block_type": 5, "heading3": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[4:]}}], "style": {}
                }
            })
        elif line.startswith('- '):
            blocks.append({
                "block_type": 12, "bullet": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[2:]}}], "style": {}
                }
            })
        elif line.startswith('>'):
            blocks.append({
                "block_type": 12, "bullet": {
                    "elements": [{"type": "text_run", "text_run": {"content": "  " + line[1:].strip()}}], "style": {}
                }
            })
        elif line.startswith('```'):
            blocks.append({
                "block_type": 12, "bullet": {
                    "elements": [{"type": "text_run", "text_run": {"content": "[代码块] " + line[3:].strip() if len(line) > 3 else "[代码块]"}}], "style": {}
                }
            })
        elif line.startswith('---') or line.startswith('***'):
            pass
        else:
            clean = line.strip()
            if clean and len(clean) < 500:
                blocks.append({
                    "block_type": 12, "bullet": {
                        "elements": [{"type": "text_run", "text_run": {"content": clean}}], "style": {}
                    }
                })
    
    return blocks


def write_blocks(doc_id: str, blocks: list) -> dict:
    """写入 blocks 到文档"""
    token = get_tenant_access_token()
    if not token:
        return {'success': False, 'error': 'No token'}
    
    resp = requests.get(
        f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks",
        headers={"Authorization": f"Bearer {token}"}, timeout=10)
    items = resp.json().get('data', {}).get('items', [])
    page_block_id = items[0].get('block_id', doc_id) if items else doc_id
    
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


def main(batch_start=0, batch_size=None, resume=True):
    """
    断点续传同步
    
    Args:
        batch_start: 从第几个文件开始（0索引）
        batch_size: 每次同步多少个，None表示全部
        resume: 是否启用断点续传
    """
    print("=" * 50)
    print("FEISHU DOC SYNC v6 (断点续传)")
    print("=" * 50)
    
    state = load_sync_state() if resume else {'synced': {}, 'failed': {}}
    print(f"[LOAD] 已同步: {len(state.get('synced', {}))} 个")
    print(f"[LOAD] 失败: {len(state.get('failed', {}))} 个")
    
    token = get_tenant_access_token()
    if not token:
        print("[ERROR] Cannot get token")
        return
    print("[OK] Token acquired\n")
    
    wiki_files = load_wiki_files()
    print(f"[LOAD] Wiki文件: {len(wiki_files)} 个")
    
    # 断点续传：跳过已同步的
    if resume:
        original_count = len(wiki_files)
        wiki_files = [f for f in wiki_files if not is_synced(f.stem, state)]
        print(f"[RESUME] 跳过已同步: {original_count - len(wiki_files)} 个")
        print(f"[RESUME] 需同步: {len(wiki_files)} 个\n")
    
    if batch_size:
        wiki_files = wiki_files[batch_start:batch_start + batch_size]
        print(f"[BATCH] 本批: {len(wiki_files)} 个 (从{batch_start}开始)\n")
    
    if not wiki_files:
        print("[DONE] 没有需要同步的文件")
        return
    
    print("[SYNC] 开始同步...\n")
    results = []
    success_count = 0
    
    for i, wiki_file in enumerate(wiki_files):
        doc_data = read_wiki_content(wiki_file)
        idx = batch_start + i + 1
        total = batch_start + len(wiki_files)
        
        print(f"[{idx}/{total}] {doc_data['title']}")
        
        # 检查是否已同步（双重检查）
        if resume and is_synced(doc_data['title'], state):
            print(f"   [SKIP] 已同步\n")
            continue
        
        # 创建文档
        create_result = create_doc(doc_data['title'])
        if not create_result.get('success'):
            print(f"   [FAIL] Create: {create_result.get('error')}")
            mark_failed(doc_data['title'], create_result.get('error'), state)
            save_sync_state(state)
            results.append({'title': doc_data['title'], 'success': False})
            continue
        
        doc_id = create_result.get('doc_id')
        url = f"https://feishu.cn/docx/{doc_id}"
        print(f"   [OK] Doc: {doc_id}")
        
        # 写入blocks
        blocks = markdown_to_blocks(doc_data['content'])
        write_result = write_blocks(doc_id, blocks)
        
        if write_result.get('success'):
            print(f"   [OK] Content ({len(blocks)} blocks)")
            mark_synced(doc_data['title'], doc_id, url, state)
            success_count += 1
        else:
            print(f"   [WARN] Write: {write_result.get('error')}")
            mark_failed(doc_data['title'], write_result.get('error'), state)
        
        save_sync_state(state)
        results.append({'title': doc_data['title'], 'doc_id': doc_id, 'success': write_result.get('success', False)})
        print()
    
    print("=" * 50)
    total_synced = len(state.get('synced', {}))
    total_failed = len(state.get('failed', {}))
    print(f"[SUMMARY] 本批成功: {success_count}/{len(wiki_files)}")
    print(f"[SUMMARY] 累计成功: {total_synced}")
    print(f"[SUMMARY] 累计失败: {total_failed}")
    print("=" * 50)


if __name__ == '__main__':
    import sys
    # 支持命令行参数: python sync_feishu_resume.py [batch_start] [batch_size]
    batch_start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else None
    main(batch_start=batch_start, batch_size=batch_size, resume=True)
