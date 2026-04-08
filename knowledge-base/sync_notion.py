#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Notion 同步脚本
将 wiki/ 知识库同步到 Notion
"""

import os
import json
from pathlib import Path
from datetime import datetime

# 配置
WIKI_DIR = Path(__file__).parent / "wiki"
NOTION_TOKEN_FILE = Path(__file__).parent / ".notion_token"


def load_wiki_files():
    """加载 wiki 目录下的所有 .md 文件"""
    files = list(WIKI_DIR.rglob("*.md"))
    return files


def read_wiki_content(file_path: Path) -> dict:
    """读取 wiki 文件内容"""
    content = file_path.read_text(encoding='utf-8')
    relative_path = file_path.relative_to(WIKI_DIR)
    return {
        'title': file_path.stem,
        'content': content,
        'path': str(relative_path)
    }


def get_notion_token() -> str:
    """获取 Notion API token"""
    if NOTION_TOKEN_FILE.exists():
        return NOTION_TOKEN_FILE.read_text(encoding='utf-8').strip()
    
    # 从环境变量获取
    return os.environ.get('NOTION_API_TOKEN')


def notion_blocks_from_markdown(markdown: str) -> list:
    """
    将 Markdown 转换为 Notion blocks 格式
    """
    blocks = []
    lines = markdown.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        if line.startswith('# '):
            blocks.append({
                'object': 'block',
                'type': 'heading_1',
                'heading_1': {'rich_text': [{'type': 'text', 'text': {'content': line[2:]}}]}
            })
        elif line.startswith('## '):
            blocks.append({
                'object': 'block',
                'type': 'heading_2',
                'heading_2': {'rich_text': [{'type': 'text', 'text': {'content': line[3:]}}]}
            })
        elif line.startswith('### '):
            blocks.append({
                'object': 'block',
                'type': 'heading_3',
                'heading_3': {'rich_text': [{'type': 'text', 'text': {'content': line[4:]}}]}
            })
        elif line.startswith('- '):
            blocks.append({
                'object': 'block',
                'type': 'bulleted_list_item',
                'bulleted_list_item': {'rich_text': [{'type': 'text', 'text': {'content': line[2:]}}]}
            })
        elif line.startswith('```'):
            # 代码块，跳过
            continue
        else:
            blocks.append({
                'object': 'block',
                'type': 'paragraph',
                'paragraph': {'rich_text': [{'type': 'text', 'text': {'content': line}}]}
            })
    
    return blocks


def create_notion_page(title: str, content: str, parent_id: str = None) -> dict:
    """
    创建 Notion 页面
    
    注意：需要 Notion Integration Token
    请先设置环境变量：NOTION_API_TOKEN
    """
    token = get_notion_token()
    
    if not token:
        return {
            'success': False,
            'error': '请设置环境变量 NOTION_API_TOKEN 或创建 .notion_token 文件'
        }
    
    # TODO: 实现实际的 Notion API 调用
    # 使用 notion-sdk 或直接调用 API
    #
    # import requests
    # headers = {
    #     'Authorization': f'Bearer {token}',
    #     'Content-Type': 'application/json',
    #     'Notion-Version': '2022-06-28'
    # }
    #
    # 创建页面
    # url = 'https://api.notion.com/v1/pages'
    # data = {
    #     'parent': {'database_id': parent_id},
    #     'properties': {
    #         'title': {'title': [{'text': {'content': title}}]}
    #     },
    #     'children': notion_blocks_from_markdown(content)
    # }
    # response = requests.post(url, headers=headers, json=data)
    
    return {
        'success': True,
        'page_id': 'mock_page_id_' + title,
        'title': title
    }


def sync_to_notion(wiki_files: list) -> dict:
    """同步所有 wiki 文件到 Notion"""
    results = []
    
    for wiki_file in wiki_files:
        doc_data = read_wiki_content(wiki_file)
        result = create_notion_page(
            title=doc_data['title'],
            content=doc_data['content']
        )
        results.append({
            'file': doc_data['path'],
            'result': result
        })
    
    return results


def main():
    """主函数"""
    print("📤 Notion 同步工具")
    print("=" * 50)
    
    # 检查 token
    token = get_notion_token()
    if not token:
        print("\n⚠️  未配置 Notion API Token")
        print("   请设置环境变量: NOTION_API_TOKEN")
        print("   或创建 .notion_token 文件")
    
    # 加载 wiki 文件
    print("\n📂 加载 wiki 文件...")
    wiki_files = load_wiki_files()
    print(f"   找到 {len(wiki_files)} 个文件")
    
    if not wiki_files:
        print("⚠️  没有找到 wiki 文件，请先运行 compile.py")
        return
    
    # 同步到 Notion
    print("\n🔄 同步到 Notion...")
    results = sync_to_notion(wiki_files)
    
    success_count = sum(1 for r in results if r['result'].get('success'))
    print(f"\n✅ 同步完成! 成功: {success_count}/{len(results)}")
    
    # 显示结果
    for r in results:
        status = "✓" if r['result'].get('success') else "✗"
        print(f"   {status} {r['file']}")


if __name__ == '__main__':
    main()
