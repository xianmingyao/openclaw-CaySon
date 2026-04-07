#!/usr/bin/env python3
"""Douyin AI tech content scraper via mobile API"""
import requests
import re
import json
import sys
import os
import time
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8'

def format_markdown(items):
    lines = ["# 抖音 AI技术热门内容\n\n"]
    lines.append(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    lines.append(f"总计: {len(items)} 条\n\n---\n\n")
    
    for i, item in enumerate(items, 1):
        lines.append(f"### 第{i}条\n")
        lines.append(f"- 标题: {item.get('title', '')}\n")
        lines.append(f"- 作者: @{item.get('author', '')}\n")
        lines.append(f"- 点赞: {item.get('digg_count', 0)}\n")
        lines.append(f"- 收藏: {item.get('collect_count', 0)}\n")
        lines.append(f"- 评论: {item.get('comment_count', 0)}\n")
        if item.get('tags'):
            lines.append(f"- 话题: {' '.join(['#'+t for t in item['tags']])}\n")
        desc = item.get('description', '')[:300]
        lines.append(f"- 内容总结: {desc}\n\n")
    
    return ''.join(lines)

def scrape_douyin_keyword(keyword, count=30):
    """Try to get Douyin data via mobile API"""
    items = []
    
    # Try mobile API endpoints
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    
    # Method 1: Try theToutiao/Douyin web search API
    urls_to_try = [
        f"https://www.douyin.com/aweme/v1/web/search/item/?keyword={keyword}&count={count}&offset=0",
    ]
    
    for url in urls_to_try:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('status_code') == 0:
                    aweme_list = data.get('item_list', [])
                    for aw in aweme_list:
                        desc = aw.get('desc', '')
                        author = aw.get('author', {}).get('nickname', '')
                        stats = aw.get('statistics', {})
                        tags = []
                        for t in aw.get('challenges', []):
                            tags.append(t.get('title', ''))
                        items.append({
                            'title': desc[:100] if desc else '无标题',
                            'author': author,
                            'digg_count': stats.get('digg_count', 0),
                            'collect_count': stats.get('collect_count', 0),
                            'comment_count': stats.get('comment_count', 0),
                            'share_count': stats.get('share_count', 0),
                            'description': desc,
                            'tags': tags,
                            'aweme_id': aw.get('aweme_id', ''),
                        })
                    sys.stderr.write(f"  Mobile API: got {len(aweme_list)} items\n")
                    return items
        except Exception as e:
            sys.stderr.write(f"  Mobile API error: {e}\n")
    
    return items

def scrape_douyin_web(keyword, count=50):
    """Try web scraping of Douyin search page"""
    items = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": "",
    }
    
    # Try to get the search page
    url = f"https://www.douyin.com/search/{keyword}?type=video"
    try:
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        sys.stderr.write(f"  Status: {resp.status_code}, URL: {resp.url}\n")
        
        # Try to find JSON data in the page
        text = resp.text
        # Look for __INITIAL_STATE__ or similar
        m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', text)
        if m:
            try:
                jd = json.loads(m.group(1))
                sys.stderr.write(f"  Found NEXT_DATA\n")
            except:
                pass
        
        # Look for routeCache
        patterns = [
            r'"awemeId":"(\d+)"',
            r'"desc":"([^"]+)"',
            r'"nickname":"([^"]+)"',
        ]
        
        # Try to extract video info
        desc_matches = re.findall(r'"description":"([^"]{10,200})"', text)
        author_matches = re.findall(r'"nickname":"([^"]{1,30})"', text)
        digg_matches = re.findall(r'"diggCount":(\d+)', text)
        
        sys.stderr.write(f"  Found {len(desc_matches)} descs, {len(author_matches)} authors\n")
        
        for i in range(min(len(desc_matches), count)):
            try:
                items.append({
                    'title': desc_matches[i][:100] if i < len(desc_matches) else '无标题',
                    'author': author_matches[i] if i < len(author_matches) else '',
                    'digg_count': int(digg_matches[i]) if i < len(digg_matches) else 0,
                    'collect_count': 0,
                    'comment_count': 0,
                    'share_count': 0,
                    'description': desc_matches[i] if i < len(desc_matches) else '',
                    'tags': [],
                    'aweme_id': '',
                })
            except:
                pass
                
    except Exception as e:
        sys.stderr.write(f"  Web scrape error: {e}\n")
    
    return items

def scrape_douyin_by_hot():
    """Get trending AI content from 抖音热榜"""
    items = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
    }
    
    # Try the hot list API
    try:
        resp = requests.get(
            "https://www.douyin.com/aweme/v1/web/hot/search/list/",
            headers=headers,
            timeout=10,
            params={"device_platform": "webapp", "aid": "6383", "channel": "channel_pc_web"}
        )
        sys.stderr.write(f"Hot list status: {resp.status_code}\n")
        if resp.status_code == 200:
            data = resp.json()
            if data.get('status_code') == 0:
                word_list = data.get('data', {}).get('word_list', [])
                sys.stderr.write(f"Got {len(word_list)} hot words\n")
                return [w.get('word', '') for w in word_list if w.get('word')]
    except Exception as e:
        sys.stderr.write(f"Hot list error: {e}\n")
    
    return []

if __name__ == "__main__":
    sys.stderr.write("Starting Douyin scraper...\n")
    
    keywords = ["AI技术", "人工智能", "ChatGPT", "AI工具", "大模型", "AI绘画", "AI视频", "LLM"]
    
    all_results = []
    
    for kw in keywords:
        sys.stderr.write(f"\n=== {kw} ===\n")
        items = scrape_douyin_web(kw, count=50)
        if not items:
            items = scrape_douyin_keyword(kw, count=30)
        all_results.extend(items)
        time.sleep(1)
    
    # Deduplicate
    seen = set()
    unique = []
    for item in all_results:
        aweme_id = item.get('aweme_id', '')
        title = item.get('title', '')
        key = aweme_id or title
        if key and key not in seen and len(key) > 5:
            seen.add(key)
            unique.append(item)
    
    sys.stderr.write(f"\nTotal unique: {len(unique)}\n")
    unique.sort(key=lambda x: x['digg_count'], reverse=True)
    top100 = unique[:100]
    
    data_dir = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "content-hunter", "data")
    os.makedirs(data_dir, exist_ok=True)
    
    md = format_markdown(top100)
    out_path = os.path.join(data_dir, "douyin.md")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    
    sys.stderr.write(f"Saved {len(top100)} items to {out_path}\n")
    print("DOUYIN DONE")
