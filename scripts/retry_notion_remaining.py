# -*- coding: utf-8 -*-
"""重试Notion同步失败的文件"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

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

# 失败的文件和未处理的文件
failed_files = [
    "Alchemy",  # 实际文件名可能包含特殊字符
    "清华大学",  # 相关文件
]

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

def create_page(title: str, blocks: list, retry: int = 5) -> dict:
    url = f"{NOTION_API_URL}/pages"
    data = {
        'parent': {'database_id': NOTION_DATABASE_ID},
        'properties': {
            '标题': {'title': [{'type': 'text', 'text': {'content': title[:100]}}]}
        },
        'children': blocks[:100]
    }
    for attempt in range(retry):
        try:
            resp = requests.post(url, headers=get_headers(), json=data, timeout=30)
            result = resp.json()
            if resp.status_code == 200:
                return {'success': True, 'page_id': result.get('id'), 'url': f"https://notion.so/{result.get('id', '').replace('-', '')}"}
            elif resp.status_code == 429:
                print(f"    Rate limited, waiting {5*(attempt+1)}s...")
                time.sleep(5 * (attempt + 1))
                continue
            else:
                return {'success': False, 'error': result.get('message', 'Unknown')}
        except Exception as e:
            print(f"    Error: {str(e)[:50]}, retry {attempt+1}/{retry}")
            time.sleep(3)
    return {'success': False, 'error': 'Max retries exceeded'}

def main():
    print("=" * 50)
    print("NOTION RETRY SYNC")
    print("=" * 50)
    
    # 查找所有wiki文件
    wiki_files = list(WIKI_DIR.rglob("*.md"))
    total_wiki = len(wiki_files)
    print(f"Total wiki files: {total_wiki}")
    
    # 找出未处理和失败的文件
    # 读取之前的结果
    result_file = Path('E:/workspace/scripts/notion_sync_results.json')
    if result_file.exists():
        content = result_file.read_text(encoding='utf-8', errors='ignore')
        try:
            prev_data = json.loads(content)
            processed_titles = set(r['title'] for r in prev_data['results'])
            print(f"Previously processed: {len(processed_titles)}")
        except:
            processed_titles = set()
    else:
        processed_titles = set()
    
    # 找出未处理的文件
    unprocessed = []
    for wf in wiki_files:
        title = wf.stem
        if title not in processed_titles:
            unprocessed.append(wf)
    
    print(f"Unprocessed files: {len(unprocessed)}")
    
    success = 0
    failed = 0
    
    # 处理未处理的文件
    for wf in unprocessed:
        title = wf.stem
        content = wf.read_text(encoding='utf-8', errors='ignore')
        blocks = notion_blocks_from_markdown(content)
        
        print(f"[NEW] {title[:40]}...")
        result = create_page(title, blocks)
        
        if result.get('success'):
            print(f"    [OK]")
            success += 1
        else:
            print(f"    [FAIL] {result.get('error', 'Unknown')[:40]}")
            failed += 1
        
        time.sleep(2)
    
    print()
    print("=" * 50)
    print(f"RETRY DONE: OK={success} FAIL={failed}")
    print("=" * 50)

if __name__ == "__main__":
    main()
