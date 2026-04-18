#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
飞书文档同步脚本 v6 - 修复版
- 使用正确的API端点
- 添加限流重试机制
- 支持增量同步
"""
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

WIKI_DIR = Path(__file__).parent / "wiki"
STATE_FILE = Path(__file__).parent / ".sync_state.json"
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
    """将 markdown 转换为飞书文档块"""
    blocks = []
    lines = markdown.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].rstrip()
        
        if not line.strip():
            i += 1
            continue
        
        # 标题
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
        # 引用行
        elif line.startswith('>'):
            blocks.append({
                "block_type": 12,
                "bullet": {
                    "elements": [{"type": "text_run", "text_run": {"content": "  " + line[1:].strip()}}],
                    "style": {}
                }
            })
        # 代码块
        elif line.startswith('```'):
            blocks.append({
                "block_type": 12,
                "bullet": {
                    "elements": [{"type": "text_run", "text_run": {"content": "[代码块]"}}],
                    "style": {}
                }
            })
        # 水平线
        elif line.startswith('---') or line.startswith('***'):
            i += 1
            continue
        # 普通段落
        else:
            clean = line.strip()
            if clean and len(clean) < 500:
                blocks.append({
                    "block_type": 2,
                    "text": {
                        "elements": [{"type": "text_run", "text_run": {"content": clean}}],
                        "style": {}
                    }
                })
        
        i += 1
    
    return blocks


def write_blocks_with_retry(doc_id: str, blocks: list) -> dict:
    """写入 blocks 到文档，带重试机制"""
    token = get_tenant_access_token()
    if not token:
        return {'success': False, 'error': 'No token'}
    
    # 获取 page block id
    resp = requests.get(
        f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks",
        headers={"Authorization": f"Bearer {token}"}, timeout=10)
    try:
        result = resp.json()
        items = result.get('data', {}).get('items', [])
        page_block_id = items[0].get('block_id', doc_id) if items else doc_id
    except:
        page_block_id = doc_id
    
    # 分批写入（每次5个，带重试）
    batch_size = 5
    success_count = 0
    fail_count = 0
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{page_block_id}/children"
    
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i+batch_size]
        payload = {"children": batch, "index": -1}
        
        # 重试3次
        for retry in range(3):
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            try:
                result = resp.json()
                if result.get('code') == 0:
                    success_count += len(batch)
                    break
                elif "frequency limit" in result.get('msg', '').lower():
                    time.sleep(2)
                    continue
                else:
                    fail_count += len(batch)
                    break
            except:
                fail_count += len(batch)
                break
        
        # 批次间延迟
        time.sleep(0.5)
    
    return {'success': fail_count == 0, 'success_count': success_count, 'fail_count': fail_count}


def load_sync_state():
    """加载同步状态"""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding='utf-8'))
    return {'synced': {}, 'last_sync': None}


def save_sync_state(state):
    """保存同步状态"""
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    import argparse
    parser = argparse.ArgumentParser(description='飞书文档同步 v6')
    parser.add_argument('--force', action='store_true', help='强制全量同步')
    parser.add_argument('--file', type=str, help='同步指定文件')
    args = parser.parse_args()
    
    print("=" * 50)
    print("FEISHU DOC SYNC v6 - 修复版")
    print("=" * 50)
    
    token = get_tenant_access_token()
    if not token:
        print("[ERROR] Cannot get token")
        return
    print("[OK] Token acquired")
    
    # 加载同步状态
    state = load_sync_state()
    wiki_files = list(WIKI_DIR.rglob("*.md"))
    print(f"[LOAD] Found {len(wiki_files)} wiki files")
    
    # 确定要同步的文件
    if args.file:
        files_to_sync = [f for f in wiki_files if str(f) == args.file]
    elif args.force:
        files_to_sync = wiki_files
        state['synced'] = {}  # 清空状态，强制全量
    else:
        # 增量：只同步有变化的文件
        files_to_sync = []
        for f in wiki_files:
            rel_path = str(f.relative_to(WIKI_DIR))
            mtime = f.stat().st_mtime
            if rel_path not in state.get('synced', {}) or state['synced'][rel_path] != mtime:
                files_to_sync.append(f)
        if files_to_sync:
            print(f"[INCREMENT] {len(files_to_sync)} files changed since last sync")
        else:
            print("[INCREMENT] No changes since last sync")
    
    if not files_to_sync:
        print("[DONE] Nothing to sync")
        return
    
    print(f"\n[SYNC] Syncing {len(files_to_sync)} files...")
    results = []
    
    for wiki_file in files_to_sync:
        rel_path = str(wiki_file.relative_to(WIKI_DIR))
        title = wiki_file.stem
        content = wiki_file.read_text(encoding='utf-8')
        
        print(f"\n   [{len(results)+1}/{len(files_to_sync)}] {title}")
        
        # 创建文档
        create_result = create_doc(title)
        if not create_result.get('success'):
            print(f"   [FAIL] Create: {create_result.get('error')}")
            results.append({'title': title, 'path': rel_path, 'success': False})
            continue
        
        doc_id = create_result.get('doc_id')
        print(f"   [OK] Doc: {doc_id}")
        
        # 转换并写入 blocks
        blocks = markdown_to_blocks(content)
        write_result = write_blocks_with_retry(doc_id, blocks)
        
        if write_result.get('success'):
            print(f"   [OK] Written {write_result.get('success_count')} blocks")
            # 更新状态
            state['synced'][rel_path] = wiki_file.stat().st_mtime
        else:
            print(f"   [WARN] {write_result.get('fail_count')} blocks failed")
        
        results.append({
            'title': title,
            'doc_id': doc_id,
            'url': f"https://feishu.cn/docx/{doc_id}",
            'path': rel_path,
            'success': write_result.get('success', False)
        })
        
        # 文档间延迟
        time.sleep(1)
    
    # 保存状态
    state['last_sync'] = datetime.now().isoformat()
    save_sync_state(state)
    
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
