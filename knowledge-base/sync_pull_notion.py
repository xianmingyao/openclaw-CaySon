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


def get_all_pages(token: str, database_id: str) -> List[Dict]:
    """获取 Database 所有页面
    
    修复笔记（2026-04-25）：
    - 原问题：Notion 10000 页面一次性加载到内存导致 SIGKILL
    - 修复：改用生成器模式，分批 yield 页面，避免内存爆炸
    - 返回：生成器，逐个产出页面字典
    """
    cursor = None
    last_cursor = None
    consecutive_same_cursor = 0  # 计数器：检测 cursor 是否卡住
    page_count = 0
    
    while True:
        endpoint = f"/databases/{database_id}/query"
        data = {"page_size": 100}
        if cursor:
            data["start_cursor"] = cursor
        
        result = notion_api(endpoint, token, method="POST", data=data)
        
        if result.get('error'):
            print(f"[ERROR] {result.get('error')}")
            break
        
        # 检查 request_status 是否表明查询不完整
        request_status = result.get('request_status', {})
        if request_status.get('state') == 'incomplete':
            incomplete_reason = request_status.get('incomplete_reason', 'unknown')
            print(f"[WARN] Query incomplete: {incomplete_reason}")
            # 查询不完整时，如果有结果就继续，但没有更多则退出
            if not result.get('has_more'):
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
            
            page_count += 1
            
            yield {
                'id': page_id,
                'title': title,
                'last_edited': last_edited,
                'url': page.get('url', '')
            }
        
        if not result.get('has_more'):
            break
        
        # 检测 cursor 是否有效推进
        cursor = result.get('next_cursor')
        if cursor == last_cursor:
            consecutive_same_cursor += 1
            if consecutive_same_cursor >= 2:
                print(f"[ERROR] Cursor not advancing (stuck at: {cursor}), breaking to prevent infinite loop")
                break
        else:
            consecutive_same_cursor = 0
        
        last_cursor = cursor


def iter_pages(token: str, database_id: str, last_sync_time: int, force: bool = False, limit: int = None):
    """迭代需要更新的页面（生成器）
    
    Args:
        token: Notion token
        database_id: Database ID
        last_sync_time: 上次同步时间戳
        force: 是否强制全量拉回
        limit: 限制拉取页面数量
    
    Yields:
        page dict that needs updating
    """
    count = 0
    for page in get_all_pages(token, database_id):
        last_edited = page.get('last_edited', '')
        should_pull = False
        
        if force:
            should_pull = True
        elif last_edited:
            try:
                edited_ts = int(datetime.fromisoformat(last_edited.replace('Z', '+00:00')).timestamp())
                if edited_ts > last_sync_time:
                    should_pull = True
            except:
                should_pull = True
        else:
            should_pull = True
        
        if should_pull:
            count += 1
            if limit is not None and count > limit:
                break
            yield page


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
    从 Notion 拉回更新（生成器模式，避免内存爆炸）
    
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
    
    # 获取 Notion 页面列表（流式处理，不再一次性加载）
    print("\n[1/3] 获取 Notion Database 页面列表（流式）...")
    
    # 先快速统计总数（仅第一次迭代，不超过200页）
    total_count = 0
    sample_pages = []
    for page in get_all_pages(token, database_id):
        total_count += 1
        if total_count <= 5:
            sample_pages.append(page)
        if total_count >= 200:
            # 最多采样200条用于计数，不需要全部遍历完
            break
    
    print(f"      找到约 {total_count}+ 个页面（使用流式处理）")
    
    # 首次同步限制数量，避免超时
    effective_limit = limit
    if is_first_sync and (limit is None or limit > 100):
        print(f"\n[WARNING] 首次同步，限制为 100 页以避免超时")
        print(f"[WARNING] 使用 --limit=X 调整，或 --force 强制全量")
        effective_limit = min(limit or 100, 100)
    
    print(f"\n[2/3] 流式筛选并下载页面...")
    
    # 使用生成器流式处理页面
    pulled = 0
    skipped = 0
    errors = 0
    
    for page in iter_pages(token, database_id, last_sync_time, force, effective_limit):
        page_id = page.get('id')
        title = page.get('title', 'untitled')
        
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
