#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sync_pull_feishu.py - 从飞书拉回更新

功能：
1. 获取飞书云文档列表
2. 对比本地 wiki，最后修改时间
3. 下载有更新的文档到本地

使用说明：
    python sync_pull_feishu.py          # 增量同步
    python sync_pull_feishu.py --force  # 强制全量拉回
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# ============== 配置 ==============
FEISHU_TOKEN_FILE = Path(__file__).parent / ".feishu_token"
WIKI_DIR = Path(__file__).parent / "wiki"
RAW_DIR = Path(__file__).parent / "raw"
LAST_SYNC_FILE = Path(__file__).parent / ".sync_state.json"


# ============== 飞书 API ==============

def get_feishu_token() -> str:
    """获取飞书 Access Token"""
    token_file = Path(__file__).parent / ".feishu_token"
    
    if token_file.exists():
        token_data = json.loads(token_file.read_text(encoding='utf-8'))
        return token_data.get('access_token', '')
    
    # 从环境变量或配置获取
    return os.environ.get('FEISHU_ACCESS_TOKEN', '')


def feishu_api(endpoint: str, token: str, method: str = "GET", data: dict = None) -> dict:
    """调用飞书 API"""
    base_url = "https://open.feishu.cn/open-apis"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
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


def get_feishu_documents(token: str) -> List[Dict]:
    """获取飞书云文档列表"""
    # 获取根目录文档
    docs = []
    
    # 方法1: 通过搜索 API 获取所有文档
    search_data = feishu_api(
        "/drive/v1/files/search?page_size=50&order_by=EditedTime&direction=DESC",
        token
    )
    
    if search_data.get("code") == 0:
        files = search_data.get("data", {}).get("files", [])
        for f in files:
            docs.append({
                'token': f.get('token'),
                'name': f.get('name'),
                'type': f.get('type'),
                'edited_time': f.get('edited_time', 0)
            })
    
    return docs


def get_feishu_doc_content(token: str, doc_token: str) -> Optional[str]:
    """获取飞书文档内容"""
    # 获取文档元信息
    meta = feishu_api(f"/doc/v2/{doc_token}/meta", token)
    
    if meta.get("code") != 0:
        return None
    
    # 获取文档内容（Markdown 格式）
    content = feishu_api(
        f"/doc/v2/{doc_token}/content",
        token
    )
    
    if content.get("code") == 0:
        # 转换为 Markdown（简化版）
        blocks = content.get("data", {}).get("content", [])
        return blocks_to_markdown(blocks)
    
    return None


def blocks_to_markdown(blocks: List) -> str:
    """将飞书 blocks 转换为 Markdown"""
    md_parts = []
    
    for block in blocks:
        block_type = block.get('block_type', 0)
        block_id = block.get('block_id', '')
        
        # 获取文本内容
        text = ""
        for item in block.get('text', []):
            for segment in item.get('text_segments', []):
                text += segment.get('content', '')
        
        # 根据 block_type 转换为对应 Markdown
        if block_type == 1:  # 段落
            md_parts.append(text)
        elif block_type == 2:  # 标题1
            md_parts.append(f"# {text}")
        elif block_type == 3:  # 标题2
            md_parts.append(f"## {text}")
        elif block_type == 4:  # 标题3
            md_parts.append(f"### {text}")
        elif block_type == 7:  # 代码块
            language = block.get('language', '')
            md_parts.append(f"```{language}\n{text}\n```")
        elif block_type == 13:  # 有序列表
            md_parts.append(f"1. {text}")
        elif block_type == 12:  # 无序列表
            md_parts.append(f"- {text}")
    
    return "\n\n".join(md_parts)


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
    从飞书拉回更新
    
    Returns:
        {pulled: int, skipped: int, errors: int}
    """
    print("=" * 50)
    print("FEISHU PULL - 双向同步（飞书 → 本地）")
    print("=" * 50)
    
    # 获取 Token
    token = get_feishu_token()
    if not token:
        print("[ERROR] 未配置飞书 Access Token")
        return {"pulled": 0, "skipped": 0, "errors": 1}
    
    # 加载上次同步状态
    last_sync = load_last_sync()
    last_sync_time = last_sync.get("timestamp", 0)
    
    # 获取飞书文档列表
    print("\n[1/3] 获取飞书文档列表...")
    docs = get_feishu_documents(token)
    print(f"      找到 {len(docs)} 个文档")
    
    # 筛选需要更新的文档
    to_pull = []
    for doc in docs:
        edited_time = doc.get('edited_time', 0)
        if force or edited_time > last_sync_time:
            to_pull.append(doc)
    
    print(f"\n[2/3] 筛选需要更新的文档...")
    print(f"      需要更新: {len(to_pull)} 个")
    
    # 下载文档
    print(f"\n[3/3] 下载文档到本地...")
    pulled = 0
    skipped = 0
    errors = 0
    
    for doc in to_pull:
        doc_token = doc.get('token')
        doc_name = doc.get('name', 'untitled')
        doc_type = doc.get('type', 'doc')
        
        print(f"      [{pulled + errors + 1}/{len(to_pull)}] {doc_name}...", end=" ")
        
        try:
            content = get_feishu_doc_content(token, doc_token)
            
            if content:
                # 保存到本地
                safe_name = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', doc_name)[:50]
                filename = f"feishu-{doc_token[:8]}-{safe_name}.md"
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
    import re
    
    force = "--force" in sys.argv or "-f" in sys.argv
    
    result = sync_pull(force=force)
    sys.exit(0 if result["errors"] == 0 else 1)
