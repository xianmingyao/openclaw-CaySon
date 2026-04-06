#!/usr/bin/env python
"""Try to get Douyin AI content from Baidu search."""

import time
import urllib.request
import urllib.parse
import re
import os
import json
from datetime import datetime

DATA_DIR = os.path.expanduser("~/.openclaw/workspace/content-hunter/data")
DOUYIN_FILE = os.path.join(DATA_DIR, "douyin.md")

def search_baidu(query):
    """Search Baidu for Douyin AI content."""
    try:
        url = f'https://www.baidu.com/s?wd={urllib.parse.quote(query)}&rn=10'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.baidu.com',
        })
        with urllib.request.urlopen(req, timeout=10) as r:
            content = r.read().decode('utf-8', errors='ignore')
        return content
    except Exception as e:
        print(f"Baidu error: {e}")
        return ""

def extract_douyin_from_baidu(html):
    """Extract Douyin URLs and titles from Baidu results."""
    items = []
    # Find result links
    pattern = r'href="(https?://(?:www\.)?douyin\.com/(?:video/|search/)[^"]+)"'
    urls = re.findall(pattern, html)
    
    # Try to find titles near links
    for url in urls:
        items.append({
            'url': url,
            'title': '抖音视频',
            'video_id': re.search(r'/video/(\d+)', url).group(1) if '/video/' in url else url
        })
    return items

def get_existing_count():
    if not os.path.exists(DOUYIN_FILE):
        return 0
    with open(DOUYIN_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.findall(r'### 第(\d+)条', content)
        if matches:
            return max(int(m) for m in matches)
    return 0

def append_douyin_results(items, start_num):
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Dedupe
    existing_ids = set()
    if os.path.exists(DOUYIN_FILE):
        with open(DOUYIN_FILE, 'r', encoding='utf-8') as f:
            existing_ids = set(re.findall(r'- 抖音ID: (.+)', f.read()))
    
    new_items = [it for it in items if str(it['video_id']) not in existing_ids]
    
    with open(DOUYIN_FILE, 'a', encoding='utf-8') as f:
        if start_num == 1:
            f.write(f"# 抖音 AI技术热门内容\n\n")
            f.write(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        written = 0
        for i, item in enumerate(new_items):
            num = start_num + i
            title = item.get('title', '抖音视频')
            f.write(f"### 第{num}条\n")
            f.write(f"- 标题 / Title: {title}\n")
            f.write(f"- 作者 / Author: @未知作者\n")
            f.write(f"- 抖音ID: {item['video_id']}\n")
            f.write(f"- 链接: {item['url']}\n")
            f.write(f"- 点赞 / Likes: 未知\n")
            f.write(f"- 评论 / Comments: 未知\n")
            f.write(f"- 分享 / Shares: 未知\n")
            f.write(f"- 播放 / Plays: 未知\n")
            f.write(f"- 话题 / Tags: #AI技术\n")
            f.write(f"- 内容总结 / Summary: {title}\n\n")
            written += 1
    
    return written

if __name__ == "__main__":
    queries = [
        'site:douyin.com AI技术 视频',
        'site:douyin.com 人工智能 最新',
        'site:douyin.com ChatGPT 使用教程',
        '抖音 AI工具 推荐',
        'site:douyin.com DeepSeek',
        'site:douyin.com AIGC 教程',
    ]
    
    all_items = []
    seen_urls = set()
    
    for q in queries:
        print(f"Searching Baidu: {q}")
        html = search_baidu(q)
        if html:
            items = extract_douyin_from_baidu(html)
            for item in items:
                if item['url'] not in seen_urls:
                    seen_urls.add(item['url'])
                    all_items.append(item)
            print(f"  -> {len(items)} items (total: {len(all_items)})")
        time.sleep(3)
    
    print(f"\nTotal unique: {len(all_items)}")
    
    if all_items:
        existing = get_existing_count()
        written = append_douyin_results(all_items, existing + 1)
        print(f"Written: {written}")
    
    final = get_existing_count()
    print(f"Final count: {final}")
