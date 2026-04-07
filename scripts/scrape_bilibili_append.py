#!/usr/bin/env python3
"""Try to append fresh Bilibili data"""
import requests
import re
import os
import sys
import time
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8'

def clean_title(title):
    return re.sub(r'<[^>]+>', '', title)

def scrape_bilibili_incremental(keyword, pages=2, page_size=30):
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://search.bilibili.com",
    }
    
    for page in range(1, pages + 1):
        url = "https://api.bilibili.com/x/web-interface/search/type"
        params = {
            "search_type": "video",
            "keyword": keyword,
            "order": "hot",  # Use hot order which might have higher rate limit
            "page": page,
            "page_size": page_size,
        }
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=15)
            if resp.status_code == 200 and resp.text.strip():
                data = resp.json()
                status = data.get("data", {}).get("cost_result", {})
                sys.stderr.write(f"  [{keyword}] page {page}: {resp.status_code}, cost={status}\n")
                items = data.get("data", {}).get("result", [])
                for item in items:
                    results.append({
                        "title": clean_title(item.get("title", "")),
                        "author": item.get("author", ""),
                        "play": item.get("play", 0),
                        "danmaku": item.get("video_review", 0),
                        "likes": item.get("like", 0),
                        "coins": item.get("coin", 0),
                        "favorites": item.get("favorites", 0),
                        "duration": item.get("duration", ""),
                        "description": item.get("description", ""),
                        "bvid": item.get("bvid", ""),
                        "tags": item.get("tag", [])[:5],
                    })
        except Exception as e:
            sys.stderr.write(f"  Error: {e}\n")
        time.sleep(3)  # Longer delay to avoid rate limiting
    
    return results

def format_bilibili_md(items):
    lines = ["# B站 AI技术热门内容\n\n"]
    lines.append(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    lines.append(f"总计: {len(items)} 条\n\n---\n\n")
    
    for i, item in enumerate(items, 1):
        lines.append(f"### 第{i}条\n")
        lines.append(f"- 标题: {item.get('title', '无标题')}\n")
        lines.append(f"- UP主: @{item.get('author', '未知')}\n")
        lines.append(f"- 播放: {item.get('play', 0)}\n")
        lines.append(f"- 弹幕: {item.get('danmaku', 0)}\n")
        lines.append(f"- 点赞: {item.get('likes', 0)}\n")
        lines.append(f"- 投币: {item.get('coins', 0)}\n")
        lines.append(f"- 收藏: {item.get('favorites', 0)}\n")
        if item.get('tags'):
            lines.append(f"- 话题: {' '.join(['#'+t for t in item['tags']])}\n")
        desc = item.get('description', '暂无描述')[:300]
        lines.append(f"- 内容总结: {desc}\n\n")
    
    return ''.join(lines)

def parse_existing_items():
    """Read existing bilibili.md to avoid duplicates"""
    data_dir = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "content-hunter", "data")
    path = os.path.join(data_dir, "bilibili.md")
    
    if not os.path.exists(path):
        return set()
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract bvid from existing - look for patterns
    bvids = re.findall(r'BV[a-zA-Z0-9]{10}', content)
    sys.stderr.write(f"Found {len(bvids)} existing BVids\n")
    return set(bvids)

if __name__ == "__main__":
    data_dir = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "content-hunter", "data")
    existing_path = os.path.join(data_dir, "bilibili.md")
    
    # Read existing BVids
    existing_bvids = parse_existing_items()
    sys.stderr.write(f"Existing BVids: {len(existing_bvids)}\n")
    
    # Try fresh scrape
    keywords = ["AI技术教程 2026", "ChatGPT使用技巧", "大模型应用", "AI工具推荐", "LLM部署"]
    all_new = []
    
    for kw in keywords:
        sys.stderr.write(f"\n=== {kw} ===\n")
        items = scrape_bilibili_incremental(kw, pages=2, page_size=30)
        # Filter out existing
        new_items = [i for i in items if i['bvid'] not in existing_bvids]
        sys.stderr.write(f"  New items: {len(new_items)}/{len(items)}\n")
        all_new.extend(new_items)
        time.sleep(5)
    
    sys.stderr.write(f"\nTotal new items: {len(all_new)}\n")
    
    if all_new:
        # Read existing content
        existing_content = ""
        if os.path.exists(existing_path):
            with open(existing_path, "r", encoding="utf-8") as f:
                existing_content = f.read()
        
        # Append new items
        # Parse existing count
        existing_count = existing_content.count("### 第")
        sys.stderr.write(f"Existing items: {existing_count}\n")
        
        # Add new items to existing
        new_md = format_bilibili_md(all_new)
        
        # Combine - but we need to renumber
        # Simple approach: just append new items
        combined = existing_content + "\n\n## 新增数据 (追加于 " + datetime.now().strftime('%Y-%m-%d %H:%M') + ")\n\n" + new_md
        
        # Save
        with open(existing_path, "w", encoding="utf-8") as f:
            f.write(combined)
        
        sys.stderr.write(f"Appended {len(all_new)} new items\n")
    else:
        sys.stderr.write("No new items to append\n")
    
    print("DONE")
