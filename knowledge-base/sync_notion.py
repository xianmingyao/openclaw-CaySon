#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Notion 同步脚本 v2
将 wiki/ 知识库同步到 Notion
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime

# 配置
WIKI_DIR = Path(__file__).parent / "wiki"
NOTION_TOKEN_FILE = Path(__file__).parent / ".notion_token"
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Notion Database 配置（需要先创建一个 Database）
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID', '')


def get_notion_token() -> str:
    """获取 Notion API token"""
    if NOTION_TOKEN_FILE.exists():
        return NOTION_TOKEN_FILE.read_text(encoding='utf-8').strip()
    return os.environ.get('NOTION_API_TOKEN', '')


def get_headers():
    """获取 Notion API 请求头"""
    token = get_notion_token()
    if not token:
        return None
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Notion-Version': NOTION_VERSION
    }


def load_wiki_files():
    """加载 wiki 目录下的所有 .md 文件"""
    return list(WIKI_DIR.rglob("*.md"))


def read_wiki_content(file_path: Path) -> dict:
    """读取 wiki 文件内容"""
    content = file_path.read_text(encoding='utf-8')
    relative_path = file_path.relative_to(WIKI_DIR)
    return {
        'title': file_path.stem,
        'content': content,
        'path': str(relative_path)
    }


def notion_blocks_from_markdown(markdown: str) -> list:
    """将 Markdown 转换为 Notion blocks 格式"""
    blocks = []
    lines = markdown.split('\n')
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        if line_stripped.startswith('# '):
            blocks.append({
                'object': 'block',
                'type': 'heading_1',
                'heading_1': {
                    'rich_text': [{'type': 'text', 'text': {'content': line_stripped[2:]}}]
                }
            })
        elif line_stripped.startswith('## '):
            blocks.append({
                'object': 'block',
                'type': 'heading_2',
                'heading_2': {
                    'rich_text': [{'type': 'text', 'text': {'content': line_stripped[3:]}}]
                }
            })
        elif line_stripped.startswith('### '):
            blocks.append({
                'object': 'block',
                'type': 'heading_3',
                'heading_3': {
                    'rich_text': [{'type': 'text', 'text': {'content': line_stripped[4:]}}]
                }
            })
        elif line_stripped.startswith('- '):
            blocks.append({
                'object': 'block',
                'type': 'bulleted_list_item',
                'bulleted_list_item': {
                    'rich_text': [{'type': 'text', 'text': {'content': line_stripped[2:]}}]
                }
            })
        elif line_stripped.startswith('>'):
            blocks.append({
                'object': 'block',
                'type': 'quote',
                'quote': {
                    'rich_text': [{'type': 'text', 'text': {'content': line_stripped[1:].strip()}}]
                }
            })
        elif line_stripped.startswith('```'):
            continue
        else:
            # 分段处理长文本
            if len(line_stripped) > 2000:
                # 分成多个段落
                for i in range(0, len(line_stripped), 2000):
                    blocks.append({
                        'object': 'block',
                        'type': 'paragraph',
                        'paragraph': {
                            'rich_text': [{'type': 'text', 'text': {'content': line_stripped[i:i+2000]}}]
                        }
                    })
            else:
                blocks.append({
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [{'type': 'text', 'text': {'content': line_stripped}}]
                    }
                })
    
    return blocks


def create_notion_page(title: str, blocks: list, parent_id: str = None) -> dict:
    """创建 Notion 页面"""
    headers = get_headers()
    if not headers:
        return {'success': False, 'error': 'No token'}
    
    # 如果没有 parent_id，使用环境变量中的 database_id
    if not parent_id:
        parent_id = NOTION_DATABASE_ID
    
    if not parent_id:
        return {
            'success': False,
            'error': '需要设置 NOTION_DATABASE_ID 环境变量，指向一个 Notion Database'
        }
    
    # 创建页面
    url = f"{NOTION_API_URL}/pages"
    data = {
        'parent': {'database_id': parent_id},
        'properties': {
            '标题': {
                'title': [{'type': 'text', 'text': {'content': title}}]
            }
        },
        'children': blocks[:100]  # Notion API 限制每次最多 100 个 blocks
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        if response.status_code == 200:
            page_id = result.get('id')
            return {
                'success': True,
                'page_id': page_id,
                'url': f"https://notion.so/{page_id.replace('-', '')}"
            }
        else:
            return {
                'success': False,
                'error': result.get('message', 'Unknown error'),
                'code': response.status_code
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def create_notion_database(title: str, parent_page_id: str = None) -> dict:
    """创建 Notion Database（作为知识库的根目录）"""
    headers = get_headers()
    if not headers:
        return {'success': False, 'error': 'No token'}
    
    # 创建 Database（直接以 workspace 为 parent）
    url = f"{NOTION_API_URL}/databases"
    data = {
        'parent': {'type': 'workspace'},
        'title': [{'type': 'text', 'text': {'content': title}}],
        'properties': {
            'title': {
                'type': 'title',
                'title': {}
            }
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()
        
        if response.status_code == 200:
            db_id = result.get('id')
            return {
                'success': True,
                'database_id': db_id,
                'url': f"https://notion.so/{db_id.replace('-', '')}"
            }
        else:
            return {
                'success': False,
                'error': result.get('message', 'Unknown error')
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_or_create_database() -> str:
    """获取或创建知识库 Database"""
    global NOTION_DATABASE_ID
    
    # 如果已经配置了，直接返回
    if NOTION_DATABASE_ID:
        return NOTION_DATABASE_ID
    
    # 尝试从文件读取
    db_id_file = Path(__file__).parent / ".notion_database_id"
    if db_id_file.exists():
        NOTION_DATABASE_ID = db_id_file.read_text().strip()
        return NOTION_DATABASE_ID
    
    # 创建新的 Database
    print("[NOTION] 创建新 Database...")
    result = create_notion_database("Karpathy 知识库")
    
    if result.get('success'):
        NOTION_DATABASE_ID = result['database_id']
        parent_page_id = result.get('parent_page_id', '')
        # 保存到文件
        db_id_file.write_text(NOTION_DATABASE_ID)
        # 也保存 parent_page_id
        parent_file = Path(__file__).parent / ".notion_parent_page_id"
        parent_file.write_text(parent_page_id)
        print(f"[NOTION] Database 创建成功: {result['url']}")
        print(f"[NOTION] Database ID: {NOTION_DATABASE_ID}")
        print(f"[NOTION] Parent Page ID: {parent_page_id}")
        print("[NOTION] IDs 已保存到文件")
        return NOTION_DATABASE_ID
    else:
        print(f"[NOTION] Database 创建失败: {result.get('error')}")
        return None


def sync_to_notion(wiki_files: list, parent_id: str = None) -> list:
    """同步所有 wiki 文件到 Notion"""
    results = []
    
    # 获取或创建 Database
    if not parent_id:
        parent_id = get_or_create_database()
        if not parent_id:
            print("[NOTION] 无法获取 Database，退出")
            return results
    
    for wiki_file in wiki_files:
        doc_data = read_wiki_content(wiki_file)
        blocks = notion_blocks_from_markdown(doc_data['content'])
        
        print(f"[NOTION] Creating: {doc_data['title']}")
        result = create_notion_page(doc_data['title'], blocks, parent_id)
        
        results.append({
            'file': doc_data['path'],
            'title': doc_data['title'],
            'result': result
        })
        
        if result.get('success'):
            print(f"   [OK] {result.get('url', 'N/A')}")
        else:
            print(f"   [FAIL] {result.get('error', 'Unknown')}")
    
    return results


def main():
    """主函数"""
    print("=" * 50)
    print("NOTION SYNC v2")
    print("=" * 50)
    
    # 检查 token
    token = get_notion_token()
    if not token:
        print("\n[ERROR] Notion API Token not configured")
        print("   设置方式:")
        print("   1. set NOTION_API_TOKEN=your_token")
        print("   2. 或创建 .notion_token 文件")
        return
    
    print("[OK] Token acquired")
    
    # 检查 Database ID
    db_id = NOTION_DATABASE_ID
    if not db_id:
        # 尝试从文件读取
        db_id_file = Path(__file__).parent / ".notion_database_id"
        if db_id_file.exists():
            db_id = db_id_file.read_text().strip()
    
    if not db_id:
        print("\n[ERROR] Notion Database ID not configured")
        print("")
        print("   需要配置 Notion Database:")
        print("   1. 在 Notion 里创建一个空页面/Database")
        print("   2. 打开这个 Database")
        print("   3. 复制 URL 中的 Database ID（32位十六进制）")
        print("   4. 设置环境变量: set NOTION_DATABASE_ID=你的ID")
        print("   5. 或者创建 .notion_database_id 文件写入 ID")
        print("")
        print("   Database ID 格式: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (32个字符)")
        print("")
        print("   跳过 Notion 同步...")
        return
    
    print(f"[OK] Database ID: {db_id[:8]}...")
    
    # 加载 wiki 文件
    print("\n[LOAD] Loading wiki files...")
    wiki_files = load_wiki_files()
    print(f"   Found {len(wiki_files)} files")
    
    if not wiki_files:
        print("[WARN] No wiki files found")
        return
    
    # 同步到 Notion
    print("\n[SYNC] Syncing to Notion...")
    results = sync_to_notion(wiki_files, db_id)
    
    success_count = sum(1 for r in results if r['result'].get('success'))
    print(f"\n[DONE] Success: {success_count}/{len(results)}")
    
    # 显示结果
    for r in results:
        status = "[OK]" if r['result'].get('success') else "[FAIL]"
        print(f"   {status} {r['title']}")


if __name__ == '__main__':
    main()
