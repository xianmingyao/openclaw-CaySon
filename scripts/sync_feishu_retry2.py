#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""飞书同步失败重试脚本 v2"""
import json
import time
import requests
from pathlib import Path
import sys

# 配置
FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"
STATE_FILE = Path(__file__).parent / "sync_state_retry.json"
WIKI_DIR = Path(__file__).parent.parent / "knowledge-base" / "wiki"

def log(msg):
    print(msg, flush=True)

def get_token():
    try:
        config_path = Path.home() / ".openclaw" / "openclaw.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        feishu = config.get('channels', {}).get('feishu', {})
        url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
        resp = requests.post(url, headers={"Content-Type": "application/json"},
            json={"app_id": feishu.get('appId'), "app_secret": feishu.get('appSecret')}, timeout=10)
        return resp.json().get('tenant_access_token')
    except Exception as e:
        log(f"获取token失败: {e}")
        return None

def create_doc(title):
    token = get_token()
    if not token:
        return None
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{FEISHU_BASE_URL}/docx/v1/documents"
    resp = requests.post(url, headers=headers, json={"title": title}, timeout=10)
    try:
        result = resp.json()
        if result.get('code') == 0:
            return result['data']['document']['document_id']
        log(f"  创建失败: {result.get('msg')[:50]}")
        return None
    except Exception as e:
        log(f"  创建异常: {e}")
        return None

def get_page_block_id(doc_id):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks", headers=headers, timeout=10)
    try:
        result = resp.json()
        items = result.get('data', {}).get('items', [])
        return items[0].get('block_id', doc_id) if items else doc_id
    except:
        return doc_id

def content_to_blocks(content):
    blocks = []
    for line in content.split('\n'):
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
            blocks.append({"block_type": 2, "text": {"elements": [{"type": "text_run", "text_run": {"content": line[:500]}}], "style": {}}})
    return blocks

def write_blocks(doc_id, blocks):
    token = get_token()
    if not token:
        return 0
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    page_block_id = get_page_block_id(doc_id)
    url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{page_block_id}/children"
    
    success_count = 0
    for i in range(0, len(blocks), 5):
        batch = blocks[i:i+5]
        payload = {"children": batch, "index": -1}
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
            except:
                pass
        time.sleep(0.5)
    return success_count

def main():
    log("=== 飞书同步重试脚本 v2 ===")
    log(f"WIKI_DIR: {WIKI_DIR}")
    log(f"STATE_FILE: {STATE_FILE}")
    
    # 加载失败列表
    state_file = Path(__file__).parent.parent / "knowledge-base" / ".sync_state.json"
    if not state_file.exists():
        log("找不到同步状态文件")
        return
    
    with open(state_file, 'r', encoding='utf-8') as f:
        state = json.load(f)
    
    failed = state.get('failed', {})
    log(f"发现 {len(failed)} 个失败的文件需要重试\n")
    
    results = []
    for i, (filename, info) in enumerate(failed.items(), 1):
        log(f"[{i}/{len(failed)}] 重试: {filename}")
        
        # 查找文件
        wiki_file = None
        for md_file in WIKI_DIR.rglob("*.md"):
            if md_file.stem == filename or filename in str(md_file):
                wiki_file = md_file
                break
        
        if not wiki_file:
            for md_file in WIKI_DIR.rglob(f"*{filename}*"):
                wiki_file = md_file
                break
        
        if not wiki_file:
            log(f"  找不到文件，跳过")
            results.append({'filename': filename, 'success': False, 'reason': 'file not found'})
            continue
        
        try:
            content = wiki_file.read_text(encoding='utf-8')
            doc_id = create_doc(filename)
            
            if doc_id:
                blocks = content_to_blocks(content)
                success_count = write_blocks(doc_id, blocks)
                log(f"  成功: https://feishu.cn/docx/{doc_id} ({success_count} blocks)")
                results.append({'filename': filename, 'success': True, 'doc_id': doc_id})
            else:
                results.append({'filename': filename, 'success': False, 'reason': 'create failed'})
        except Exception as e:
            log(f"  异常: {e}")
            results.append({'filename': filename, 'success': False, 'reason': str(e)})
        
        # 动态间隔
        time.sleep(3)
    
    # 统计
    success = sum(1 for r in results if r['success'])
    log(f"\n=== 重试完成 ===")
    log(f"成功: {success}/{len(results)}")
    
    # 保存结果
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    log(f"结果已保存到: {STATE_FILE}")

if __name__ == '__main__':
    main()
