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

# Windows 控制台编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

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


def get_filtered_pages(token: str, database_id: str, last_sync_time: int = 0, force: bool = False, limit: int = None) -> List[Dict]:
    """获取 Database 页面（API级别过滤，仅返回需要更新的页面）
    
    优化笔记（2026-05-06）：
    - 原问题：双重遍历（计数+下载），无API过滤，32674页巨慢
    - 修复：使用 Notion filter 参数，API级别过滤 last_edited_time
    - 单次遍历，只拿需要更新的页面，效率提升 100x+
    
    Args:
        token: Notion token
        database_id: Database ID
        last_sync_time: 上次同步时间戳（只拉取 > 此时间的页面）
        force: 是否强制全量拉回
        limit: 限制拉取页面数量
    
    Yields:
        page dict that needs updating
    """
    cursor = None
    last_cursor = None
    consecutive_same_cursor = 0
    page_count = 0
    
    while True:
        endpoint = f"/databases/{database_id}/query"
        
        # 构建查询参数
        data = {"page_size": 100}
        
        # API级别过滤：只查询 last_edited_time > last_sync_time 的页面
        if not force and last_sync_time > 0:
            # 将 Unix 时间戳转回 ISO 格式
            filter_ts = datetime.fromtimestamp(last_sync_time).strftime('%Y-%m-%dT%H:%M:%S.000Z')
            data["filter"] = {
                "property": "last_edited_time",
                "timestamp": "last_edited_time",
                "last_edited_time": {
                    "after": filter_ts
                }
            }
        
        if cursor:
            data["start_cursor"] = cursor
        
        result = notion_api(endpoint, token, method="POST", data=data)
        
        if result.get('error'):
            print(f"[ERROR] {result.get('error')}")
            break
        
        # 处理 rate limit
        status_code = result.get('code', '')
        if status_code == 'resource_exhausted':
            print(f"[WARN] Rate limited, waiting 2s...")
            import time
            time.sleep(2)
            continue
        
        results_list = result.get('results', [])
        if not results_list:
            # 如果过滤后没结果（增量同步场景），直接结束
            break
        
        for page in results_list:
            page_id = page.get('id', '').replace('-', '')
            properties = page.get('properties', {})
            
            # 获取标题
            title = "Untitled"
            for prop_name, prop in properties.items():
                if prop.get('type') == 'title':
                    title = ''.join([t.get('plain_text', '') for t in prop.get('title', [])])
                    break
            
            last_edited = page.get('last_edited_time', '')
            page_count += 1
            
            yield {
                'id': page_id,
                'title': title,
                'last_edited': last_edited,
                'url': page.get('url', '')
            }
            
            # limit 检查
            if limit and page_count >= limit:
                print(f"      (达到限制 {limit} 页)")
                return
        
        if not result.get('has_more'):
            break
        
        # 检测 cursor 是否有效推进
        cursor = result.get('next_cursor')
        if cursor == last_cursor:
            consecutive_same_cursor += 1
            if consecutive_same_cursor >= 2:
                print(f"[ERROR] Cursor stuck at: {cursor}, breaking")
                break
        else:
            consecutive_same_cursor = 0
        
        last_cursor = cursor


def load_last_sync() -> Dict:
    """加载上次同步状态"""
    if LAST_SYNC_FILE.exists():
        return json.loads(LAST_SYNC_FILE.read_text(encoding='utf-8'))
    return {}


def save_last_sync(state: Dict):
    """保存同步状态"""
    LAST_SYNC_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')


# ============== 主流程 ==============

def sync_pull(force: bool = False, limit: int = None) -> Dict:
    """
    从 Notion 拉回更新（API级过滤，单次遍历）
    
    Args:
        force: 是否强制全量拉回
        limit: 限制拉取页面数量（用于测试）
    
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
    is_first_sync = last_sync_time == 0 and not force
    
    print(f"\n[1/2] {'强制全量拉取' if force else '增量拉取（仅上次同步后更新的页面）'}...")
    if not force and last_sync_time > 0:
        last_sync_str = datetime.fromtimestamp(last_sync_time).strftime('%Y-%m-%d %H:%M:%S')
        print(f"      只同步 > {last_sync_str} 更新的页面")
    
    # 首次同步限制数量，避免超时
    effective_limit = limit
    if is_first_sync and (limit is None or limit > 100):
        print(f"\n[WARNING] 首次同步，限制为 100 页以避免超时")
        print(f"[WARNING] 使用 --limit=X 调整，或 --force 强制全量")
        effective_limit = min(limit or 100, 100)
    
    # 单次遍历：API级别过滤 + 下载
    pulled = 0
    skipped = 0
    errors = 0
    
    for page in get_filtered_pages(token, database_id, last_sync_time, force, effective_limit):
        page_id = page.get('id')
        title = page.get('title', 'untitled')
        last_edited = page.get('last_edited', '')
        
        print(f"      [{pulled + errors + 1}] {title[:40]}...", end=" ")
        
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
    
    # 解析 --limit 参数
    limit = None
    for arg in sys.argv:
        if arg.startswith("--limit="):
            limit = int(arg.split("=")[1])
    
    result = sync_pull(force=force, limit=limit)
    sys.exit(0 if result["errors"] == 0 else 1)
