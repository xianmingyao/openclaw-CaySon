#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
飞书文档同步脚本 v3
简化版 - 只创建文档，不写入内容
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

# 配置
WIKI_DIR = Path(__file__).parent / "wiki"
FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"

# 飞书配置
FEISHU_APP_ID = None
FEISHU_APP_SECRET = None
TENANT_ACCESS_TOKEN = None


def get_feishu_config():
    """从配置文件获取飞书配置"""
    global FEISHU_APP_ID, FEISHU_APP_SECRET
    
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding='utf-8'))
        feishu_config = config.get('channels', {}).get('feishu', {})
        FEISHU_APP_ID = feishu_config.get('appId')
        FEISHU_APP_SECRET = feishu_config.get('appSecret')


def get_tenant_access_token() -> str:
    """获取 tenant_access_token"""
    global TENANT_ACCESS_TOKEN
    
    get_feishu_config()
    
    url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=10)
    result = response.json()
    
    if result.get('code') == 0:
        TENANT_ACCESS_TOKEN = result.get('tenant_access_token')
        return TENANT_ACCESS_TOKEN
    return None


def create_doc(title: str) -> dict:
    """创建飞书文档"""
    token = get_tenant_access_token()
    if not token:
        return {'success': False, 'error': 'No token'}
    
    url = f"{FEISHU_BASE_URL}/docx/v1/documents"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {"title": title}
    
    response = requests.post(url, headers=headers, json=data, timeout=10)
    result = response.json()
    
    if result.get('code') == 0:
        doc_id = result.get('data', {}).get('document', {}).get('document_id')
        return {'success': True, 'doc_id': doc_id, 'title': title}
    else:
        return {'success': False, 'error': result.get('msg')}


def update_doc_content(doc_id: str, content: str) -> dict:
    """使用 docx API 更新文档内容"""
    token = get_tenant_access_token()
    if not token:
        return {'success': False, 'error': 'No token'}
    
    # 使用 blocks API
    url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 构建 blocks
    blocks = []
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('# '):
            blocks.append({
                "block_type": 3,
                "heading1": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[2:], "text_style": {}}}],
                    "style": {}
                }
            })
        elif line.startswith('## '):
            blocks.append({
                "block_type": 4,
                "heading2": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[3:], "text_style": {}}}],
                    "style": {}
                }
            })
        elif line.startswith('### '):
            blocks.append({
                "block_type": 5,
                "heading3": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[4:], "text_style": {}}}],
                    "style": {}
                }
            })
        elif line.startswith('- '):
            blocks.append({
                "block_type": 12,
                "bullet": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[2:], "text_style": {}}}],
                    "style": {}
                }
            })
        elif line.startswith('>'):
            blocks.append({
                "block_type": 13,
                "quote": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[1:].strip(), "text_style": {}}}],
                    "style": {}
                }
            })
        elif line.startswith('```'):
            continue  # 跳过代码块标记
        else:
            blocks.append({
                "block_type": 2,
                "paragraph": {
                    "elements": [{"type": "text_run", "text_run": {"content": line, "text_style": {}}}],
                    "style": {}
                }
            })
    
    data = {"children": blocks, "index": -1}
    
    response = requests.post(url, headers=headers, json=data, timeout=30)
    
    if response.status_code == 200:
        try:
            result = response.json()
            if result.get('code') == 0:
                return {'success': True}
        except:
            pass
    
    return {'success': False, 'error': f'Status {response.status_code}'}


def load_wiki_files():
    """加载 wiki 目录下的所有 .md 文件"""
    return list(WIKI_DIR.rglob("*.md"))


def read_wiki_content(file_path: Path) -> dict:
    """读取 wiki 文件内容"""
    return {
        'title': file_path.stem,
        'content': file_path.read_text(encoding='utf-8'),
        'path': str(file_path.relative_to(WIKI_DIR))
    }


def main():
    print("=" * 50)
    print("FEISHU DOC SYNC v3")
    print("=" * 50)
    
    # 加载 wiki 文件
    print("\n[LOAD] Loading wiki files...")
    wiki_files = load_wiki_files()
    print(f"   Found {len(wiki_files)} files")
    
    if not wiki_files:
        print("   WARNING: No wiki files found")
        return
    
    # 创建文档
    print("\n[CREATE] Creating Feishu docs...")
    results = []
    
    for wiki_file in wiki_files:
        doc_data = read_wiki_content(wiki_file)
        print(f"\n   Creating: {doc_data['title']}")
        
        # 创建文档
        result = create_doc(doc_data['title'])
        
        if result.get('success'):
            doc_id = result.get('doc_id')
            print(f"   [OK] Created: https://xxx.feishu.cn/docx/{doc_id}")
            
            # 尝试写入内容
            write_result = update_doc_content(doc_id, doc_data['content'])
            if write_result.get('success'):
                print(f"   [OK] Content written")
            else:
                print(f"   [WARN] Content write failed: {write_result.get('error')}")
                print(f"   [INFO] Please add content manually")
            
            results.append({
                'title': doc_data['title'],
                'doc_id': doc_id,
                'url': f"https://xxx.feishu.cn/docx/{doc_id}",
                'success': True
            })
        else:
            print(f"   [FAIL] {result.get('error')}")
            results.append({
                'title': doc_data['title'],
                'success': False,
                'error': result.get('error')
            })
    
    # 汇总
    print("\n" + "=" * 50)
    success_count = sum(1 for r in results if r.get('success'))
    print(f"[DONE] Created {success_count}/{len(results)} docs")
    
    print("\nCreated Documents:")
    for r in results:
        if r.get('success'):
            print(f"   - {r['title']}")
            print(f"     {r['url']}")


if __name__ == '__main__':
    main()
