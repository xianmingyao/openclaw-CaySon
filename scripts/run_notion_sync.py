# -*- coding: utf-8 -*-
"""Notion同步脚本 - 修复版"""
import sys
import os
sys.path.insert(0, 'E:/workspace/knowledge-base')

from pathlib import Path
import requests
import time
import json

# 配置
WIKI_DIR = Path('E:/workspace/knowledge-base/wiki')
TOKEN_FILE = Path('E:/workspace/knowledge-base/.notion_token')
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
NOTION_DATABASE_ID = "33d2bb5417c380f6baaff3467dea91c8"

def get_headers():
    token = TOKEN_FILE.read_text(encoding='utf-8').strip()
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Notion-Version': NOTION_VERSION
    }

def notion_blocks_from_markdown(markdown: str) -> list:
    blocks = []
    lines = markdown.split('\n')
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        if line_stripped.startswith('# '):
            blocks.append({'object': 'block', 'type': 'heading_1', 'heading_1': {'rich_text': [{'type': 'text', 'text': {'content': line_stripped[2:]}}]}})
        elif line_stripped.startswith('## '):
            blocks.append({'object': 'block', 'type': 'heading_2', 'heading_2': {'rich_text': [{'type': 'text', 'text': {'content': line_stripped[3:]}}]}})
        elif line_stripped.startswith('### '):
            blocks.append({'object': 'block', 'type': 'heading_3', 'heading_3': {'rich_text': [{'type': 'text', 'text': {'content': line_stripped[4:]}}]}})
        elif line_stripped.startswith('- '):
            blocks.append({'object': 'block', 'type': 'bulleted_list_item', 'bulleted_list_item': {'rich_text': [{'type': 'text', 'text': {'content': line_stripped[2:]}}]}})
        elif line_stripped.startswith('>'):
            blocks.append({'object': 'block', 'type': 'quote', 'quote': {'rich_text': [{'type': 'text', 'text': {'content': line_stripped[1:].strip()}}]}})
        elif line_stripped.startswith('```'):
            continue
        else:
            if len(line_stripped) > 2000:
                for i in range(0, len(line_stripped), 2000):
                    blocks.append({'object': 'block', 'type': 'paragraph', 'paragraph': {'rich_text': [{'type': 'text', 'text': {'content': line_stripped[i:i+2000]}}]}})
            else:
                blocks.append({'object': 'block', 'type': 'paragraph', 'paragraph': {'rich_text': [{'type': 'text', 'text': {'content': line_stripped}}]}})
    return blocks

def create_page(title: str, blocks: list) -> dict:
    url = f"{NOTION_API_URL}/pages"
    data = {
        'parent': {'database_id': NOTION_DATABASE_ID},
        'properties': {
            '标题': {'title': [{'type': 'text', 'text': {'content': title[:100]}}]}  # 修复：使用中文列名
        },
        'children': blocks[:100]
    }
    try:
        resp = requests.post(url, headers=get_headers(), json=data, timeout=30)
        result = resp.json()
        if resp.status_code == 200:
            return {'success': True, 'page_id': result.get('id'), 'url': f"https://notion.so/{result.get('id', '').replace('-', '')}"}
        else:
            return {'success': False, 'error': result.get('message', 'Unknown')}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    print("=" * 50)
    print("NOTION SYNC - 修复版")
    print("=" * 50)
    
    # 获取所有wiki文件
    wiki_files = list(WIKI_DIR.rglob("*.md"))
    print(f"找到 {len(wiki_files)} 个wiki文件")
    
    # 限制数量测试
    wiki_files = wiki_files[:10]  # 先同步10个测试
    print(f"本次同步 {len(wiki_files)} 个文件")
    
    success = 0
    failed = 0
    
    for i, wiki_file in enumerate(wiki_files):
        title = wiki_file.stem
        content = wiki_file.read_text(encoding='utf-8')
        blocks = notion_blocks_from_markdown(content)
        
        print(f"[{i+1}/{len(wiki_files)}] Creating: {title[:30]}...")
        result = create_page(title, blocks)
        
        if result.get('success'):
            print(f"  [OK] {result.get('url', '')}")
            success += 1
        else:
            print(f"  [FAIL] {result.get('error', 'Unknown')}")
            failed += 1
        
        time.sleep(1)  # 避免限流
    
    print()
    print("=" * 50)
    print(f"Sync done: OK={success} FAIL={failed}")
    print("=" * 50)

if __name__ == "__main__":
    main()
