#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sync_pull_notion.py - 从 Notion 拉回更新

功能：
1. 获取 Notion Database 所有页面
2. 对比本地 wiki，最后编辑时间
3. 下载有更新的页面内容到本地

使用说明：
    python sync_pull_notion.py          # 增量同步
    python sync_pull_notion.py --force  # 强制全量拉回
"""

import os
import sys
import re
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# ============== 配置 ==============
NOTION_TOKEN_FILE = Path(__file__).parent / ".notion_token"
NOTION_DB_ID_FILE = Path(__file__).parent / ".notion_database_id"
WIKI_DIR = Path(__file__).parent / "wiki"
LAST_SYNC_FILE = Path(__file__).parent / ".notion_sync_state.json"


# ============== Notion API ==============

def get_notion_token() -> str:
    """获取 Notion Token"""
    token_file = NOTION_TOKEN_FILE
    
    if token_file.exists():
        return token_file.read_text(encoding='utf-8').strip()
    
    return os.environ.get('NOTION_TOKEN', '')


def get_database_id() -> str:
    """获取 Notion Database ID"""
    db_file = NOTION_DB_ID_FILE
    
    if db_file.exists():
        return db_file.read_text(encoding='utf-8').strip()
    
    return os.environ.get('NOTION_DATABASE_ID', '')


def notion_api(endpoint: str, token: str, method: str = "GET", data: dict = None) -> dict:
    """调用 Notion API"""
    base_url = "https://api.notion.com/v1"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    url = f"{base_url}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        else:
            response = requests.post(url, headers=headers, json=data, timeout=30)
        
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def notion_blocks_to_markdown(blocks: List) -> str:
    """将 Notion blocks 转换为 Markdown"""
    md_parts = []
    
    for block in blocks:
        block_type = block.get('type', '')
        block_content = block.get(block_type, {})
        
        # 获取纯文本内容
        def get_plain_text(rich_text: List) -> str:
            return ''.join([t.get('plain_text', '') for t in rich_text])
        
        text = get_plain_text(block_content.get('rich_text', []))
        
        if not text.strip():
            continue
        
        # 根据 block_type 转换
        if block_type == 'paragraph':
            md_parts.append(text)
        elif block_type == 'heading_1':
            md_parts.append(f"# {text}")
        elif block_type == 'heading_2':
            md_parts.append(f"## {text}")
        elif block_type == 'heading_3':
            md_parts.append(f"### {text}")
        elif block_type == 'bulleted_list_item':
            md_parts.append(f"- {text}")
        elif block_type == 'numbered_list_item':
            md_parts.append(f"1. {text}")
        elif block_type == 'code':
            language = block_content.get('language', '')
            md_parts.append(f"```{language}\n{text}\n```")
        elif block_type == 'quote':
            md_parts.append(f"> {text}")
        elif block_type == 'callout':
            md_parts.append(f"> 📌 {text}")
        elif block_type == 'to_do':
            checked = block_content.get('checked', False)
            check_mark = "✅" if checked else "☐"
            md_parts.append(f"{check_mark} {text}")
    
    return "\n\n".join(md_parts)


def get_page_content(page_id: str, token: str) -> Optional[str]:
    """获取 Notion 页面内容"""
    # 获取块children
    blocks = []
    cursor = None
    
    while True:
        endpoint = f"/blocks/{page_id}/children"
        if cursor:
            endpoint += f"?start_cursor={cursor}"
        
        result = notion_api(endpoint, token)
        
        if result.get('error'):
            return None
        
        blocks.extend(result.get('results', []))
        
        if not result.get('has_more'):
            break
        
        cursor = result.get('next_cursor')
    
    return notion_blocks_to_markdown(blocks)


def get_all_pages(token: str, database_id: str) -> List[Dict]:
    """获取 Database 所有页面"""
    pages = []
    cursor = None
    
    while True:
        endpoint = f"/databases/{database_id}/query"
        data = {"page_size": 100}
        if cursor:
            data["start_cursor"] = cursor
        
        result = notion_api(endpoint, token, method="POST", data=data)
        
        if result.get('error'):
            print(f"[ERROR] {result.get('error')}")
            break
        
        for page in result.get('results', []):
            page_id = page.get('id', '').replace('-', '')
            properties = page.get('properties', {})
            
            # 获取标题
            title = "Untitled"
            for prop_name, prop in properties.items():
                if prop.get('type') == 'title':
                    title = ''.join([t.get('plain_text', '') for t in prop.get('title', [])])
                    break
            
            # 获取最后编辑时间
            last_edited = page.get('last_edited_time', '')
            
            pages.append({
                'id': page_id,
                'title': title,
                'last_edited': last_edited,
                'url': page.get('url', '')
            })
        
        if not result.get('has_more'):
            break
        
        cursor = result.get('next_cursor')
    
    return pages


def load_last_sync() -> Dict:
    """加载上次同步状态"""
    if LAST_SYNC_FILE.exists():
        return json.loads(LAST_SYNC_FILE.read_text(encoding='utf-8'))
    return {}


def save_last_sync(state: Dict):
    """保存同步状态"""
    LAST_SYNC_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


# ============== 主流程 ==============

def sync_pull(force: bool = False) -> Dict:
    """
    从 Notion 拉回更新
    
    Returns:
        {pulled: int, skipped: int, errors: int}
    """
    print("=" * 50)
    print("NOTION PULL - 双向同步（Notion → 本地）")
    print("=" * 50)
    
    # 获取配置
    token = get_notion_token()
    database_id = get_database_id()
    
    if not token or not database_id:
        print("[ERROR] 未配置 Notion Token 或 Database ID")
        return {"pulled": 0, "skipped": 0, "errors": 1}
    
    # 加载上次同步状态
    last_sync = load_last_sync()
    last_sync_time = last_sync.get("timestamp", 0)
    
    # 获取 Notion 页面列表
    print("\n[1/3] 获取 Notion Database 页面列表...")
    pages = get_all_pages(token, database_id)
    print(f"      找到 {len(pages)} 个页面")
    
    # 筛选需要更新的页面
    to_pull = []
    for page in pages:
        last_edited = page.get('last_edited', '')
        if last_edited:
            try:
                edited_ts = int(datetime.fromisoformat(last_edited.replace('Z', '+00:00')).timestamp())
                if force or edited_ts > last_sync_time:
                    to_pull.append(page)
            except:
                to_pull.append(page)
    
    print(f"\n[2/3] 筛选需要更新的页面...")
    print(f"      需要更新: {len(to_pull)} 个")
    
    # 下载页面
    print(f"\n[3/3] 下载页面到本地...")
    pulled = 0
    skipped = 0
    errors = 0
    
    for page in to_pull:
        page_id = page.get('id')
        title = page.get('title', 'untitled')
        
        print(f"      [{pulled + errors + 1}/{len(to_pull)}] {title}...", end=" ")
        
        try:
            content = get_page_content(page_id, token)
            
            if content:
                # 保存到本地
                safe_name = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', title)[:50]
                filename = f"notion-{page_id[:8]}-{safe_name}.md"
                filepath = WIKI_DIR / "来源" / filename
                filepath.parent.mkdir(exist_ok=True)
                filepath.write_text(content, encoding='utf-8')
                
                print("✅")
                pulled += 1
            else:
                print("⏭️ (无内容)")
                skipped += 1
                
        except Exception as e:
            print(f"❌ ({e})")
            errors += 1
    
    # 更新同步状态
    save_last_sync({
        "timestamp": int(datetime.now().timestamp()),
        "pulled": pulled,
        "skipped": skipped,
        "errors": errors
    })
    
    print(f"\n[DONE] 拉取完成: {pulled} ✅ / {skipped} ⏭️ / {errors} ❌")
    
    return {"pulled": pulled, "skipped": skipped, "errors": errors}


if __name__ == '__main__':
    force = "--force" in sys.argv or "-f" in sys.argv
    
    result = sync_pull(force=force)
    sys.exit(0 if result["errors"] == 0 else 1)
