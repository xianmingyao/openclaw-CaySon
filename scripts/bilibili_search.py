#!/usr/bin/env python3
"""
Bilibili AI Tech Search Scraper
Uses requests + BeautifulSoup to get video search results
"""
import requests
import json
import re
import time
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.bilibili.com/',
}

def search_bilibili(keyword, page=1, page_size=30):
    """Search Bilibili videos"""
    url = f"https://api.bilibili.com/x/web-interface/search/type"
    params = {
        'search_key': keyword,
        'category_id': 0,
        'search_type': 'video',
        'order': 'totalrank',
        'duration': 0,
        'page': page,
        'page_size': page_size,
        'platform': 'web',
        'highlight': 1,
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        if data.get('code') == 0:
            return data.get('data', {}).get('result', [])
        else:
            print(f"API error: {data.get('message', 'unknown')}")
            return []
    except Exception as e:
        print(f"Request error: {e}")
        return []

def format_view_count(v):
    """Format view count"""
    if v >= 10000:
        return f"{v/10000:.1f}万"
    return str(v)

def main():
    keyword = "AI人工智能"
    print(f"Searching Bilibili for: {keyword}")
    
    all_results = []
    # Get 3 pages = 90 results
    for page in range(1, 4):
        print(f"Fetching page {page}...")
        results = search_bilibili(keyword, page=page, page_size=30)
        if not results:
            print(f"No results for page {page}")
            continue
        all_results.extend(results)
        time.sleep(1)
    
    print(f"Total results: {len(all_results)}")
    
    # Format as markdown
    lines = ["# B站 AI人工智能 热门视频\n"]
    lines.append(f"抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"总计: {len(all_results)} 条\n")
    lines.append("---\n")
    
    for i, v in enumerate(all_results, 1):
        title = v.get('title', '').replace('<em class="keyword">', '').replace('</em>', '')
        author = v.get('author', '')
        play = v.get('play', 0)
        video_review = v.get('video_review', 0)  # danmaku
        favorites = v.get('favorites', 0)
        likes = v.get('like', 0)
        duration = v.get('duration', '')
        description = v.get('description', '')[:100]
        bvid = v.get('bvid', '')
        arcurl = v.get('arcurl', '')
        
        lines.append(f"### 第{i}条\n")
        lines.append(f"- 标题: {title}\n")
        lines.append(f"- UP主: {author}\n")
        lines.append(f"- 播放: {format_view_count(play)}\n")
        lines.append(f"- 弹幕: {format_view_count(video_review)}\n")
        lines.append(f"- 点赞: {format_view_count(likes)}\n")
        lines.append(f"- 投币: 未知\n")
        lines.append(f"- 收藏: {format_view_count(favorites)}\n")
        lines.append(f"- 时长: {duration}\n")
        lines.append(f"- 内容总结: {description}...\n")
        lines.append(f"- 链接: {arcurl}\n")
        lines.append(f"- BV号: {bvid}\n")
        lines.append("\n")
    
    content = '\n'.join(lines)
    
    output_path = r"E:\workspace\content-hunter-data\data\bilibili.md"
    # Append mode
    with open(output_path, 'a', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Appended {len(all_results)} items to {output_path}")

if __name__ == '__main__':
    main()
