#!/usr/bin/env python
"""Scrape Bilibili AI trending content and Douyin AI trending content."""

import urllib.request
import urllib.parse
import json
import os
import sys
import re
from datetime import datetime

DATA_DIR = os.path.expanduser("~/.openclaw/workspace/content-hunter/data")
BILIBILI_FILE = os.path.join(DATA_DIR, "bilibili.md")
DOUYIN_FILE = os.path.join(DATA_DIR, "douyin.md")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com/',
    'Origin': 'https://www.bilibili.com',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
}

def get_bilibili_ai_content():
    """Fetch AI-related trending videos from Bilibili."""
    search_keywords = ["AI技术", "人工智能", "ChatGPT", "大模型", "LLM", "AIGC", "AI绘画", "AI工具", "AI编程", "AI大模型", "AI应用", "机器学习", "深度学习", "AI生成", "AI视频"]
    all_items = []
    
    for kw in search_keywords:
        try:
            url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={urllib.parse.quote(kw)}&page=1&page_size=30&order=totalrank"
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as r:
                raw = r.read()
                # Try to decode gzip
                try:
                    import gzip
                    raw = gzip.decompress(raw)
                except:
                    pass
                data = json.loads(raw.decode('utf-8'))
                items = data.get('data', {}).get('result', [])
                for item in items:
                    if item.get('bvid'):
                        title = item.get('title', '')
                        # Clean HTML tags like <em class="keyword">
                        title = re.sub(r'<[^>]+>', '', title)
                        all_items.append({
                            'title': title,
                            'author': item.get('author', ''),
                            'bvid': item.get('bvid', ''),
                            'play': item.get('play', '0'),
                            'like': item.get('like', '0'),
                            'tag': kw,
                            'duration': item.get('duration', ''),
                            'description': item.get('description', ''),
                            'pubdate': item.get('pubdate', ''),
                        })
            print(f"  [Bilibili] '{kw}' -> {len(items)} results", file=sys.stderr)
        except Exception as e:
            print(f"  [Bilibili] Error with keyword '{kw}': {e}", file=sys.stderr)
    
    # Dedupe by bvid
    seen = set()
    unique_items = []
    for item in all_items:
        if item['bvid'] not in seen:
            seen.add(item['bvid'])
            unique_items.append(item)
    
    return unique_items

def get_douyin_ai_content():
    """Fetch AI-related trending content from Douyin via web search."""
    # Douyin doesn't have a public API, so use web scraping approach
    # Try the search page with different keywords
    search_keywords = ["AI技术 抖音", "人工智能", "ChatGPT", "大模型", "AIGC", "AI工具", "AI绘画"]
    all_items = []
    
    # Use a simpler approach - try to fetch via web fetch tool
    for kw in search_keywords:
        try:
            encoded_kw = urllib.parse.quote(kw)
            # Use mobile-friendly search URL
            url = f"https://www.douyin.com/aweme/v1/web/search/item/?keyword={encoded_kw}&count=20&offset=0&search_source=tab_search&channel_id=0&sort_type=0&publish_time=0&source=search_history&pc_client_type=1&version_code=190500&version_name=19.5.0"
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                'Referer': 'https://www.douyin.com/',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            })
            with urllib.request.urlopen(req, timeout=10) as r:
                raw = r.read()
                try:
                    import gzip
                    raw = gzip.decompress(raw)
                except:
                    pass
                data = json.loads(raw.decode('utf-8'))
                aweme_list = data.get('aweme_list', []) or data.get('data', {}).get('aweme_list', [])
                for aweme in aweme_list:
                    all_items.append({
                        'title': aweme.get('desc', ''),
                        'author': aweme.get('author', {}).get('nickname', ''),
                        'aweme_id': aweme.get('aweme_id', ''),
                        'digg_count': aweme.get('statistics', {}).get('digg_count', 0),
                        'comment_count': aweme.get('statistics', {}).get('comment_count', 0),
                        'share_count': aweme.get('statistics', {}).get('share_count', 0),
                        'play_count': aweme.get('statistics', {}).get('play_count', 0),
                        'tag': kw,
                    })
            print(f"  [Douyin] '{kw}' -> results", file=sys.stderr)
        except Exception as e:
            print(f"  [Douyin] Error with keyword '{kw}': {e}", file=sys.stderr)
    
    # Dedupe
    seen = set()
    unique_items = []
    for item in all_items:
        if item['aweme_id'] and item['aweme_id'] not in seen:
            seen.add(item['aweme_id'])
            unique_items.append(item)
    
    return unique_items

def get_existing_count(filepath):
    """Get current item count in file."""
    if not os.path.exists(filepath):
        return 0
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.findall(r'### 第(\d+)条', content)
        if matches:
            return max(int(m) for m in matches)
    return 0

def append_bilibili_to_file(items, start_num):
    """Append Bilibili items to markdown file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(BILIBILI_FILE, 'a', encoding='utf-8') as f:
        if start_num == 1:
            f.write(f"# B站 AI技术热门内容\n\n")
            f.write(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for i, item in enumerate(items):
            num = start_num + i
            f.write(f"### 第{num}条\n")
            f.write(f"- 标题 / Title: {item['title']}\n")
            f.write(f"- UP主 / UP: {item['author']}\n")
            f.write(f"- BV ID: {item['bvid']}\n")
            f.write(f"- 播放 / Views: {item['play']}\n")
            f.write(f"- 点赞 / Likes: {item['like']}\n")
            f.write(f"- 话题 / Tags: #{item['tag']}\n")
            f.write(f"- 时长 / Duration: {item['duration']}\n")
            desc = item['description'][:300] if item['description'] else '暂无描述'
            f.write(f"- 内容总结 / Summary: {desc}\n\n")
    
    return len(items)

def append_douyin_to_file(items, start_num):
    """Append Douyin items to markdown file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(DOUYIN_FILE, 'a', encoding='utf-8') as f:
        if start_num == 1:
            f.write(f"# 抖音 AI技术热门内容\n\n")
            f.write(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for i, item in enumerate(items):
            num = start_num + i
            title = item['title'][:200] if item['title'] else '暂无标题'
            author = item['author'] or '未知作者'
            f.write(f"### 第{num}条\n")
            f.write(f"- 标题 / Title: {title}\n")
            f.write(f"- 作者 / Author: @{author}\n")
            f.write(f"- 抖音ID: {item['aweme_id']}\n")
            f.write(f"- 点赞 / Likes: {item['digg_count']}\n")
            f.write(f"- 评论 / Comments: {item['comment_count']}\n")
            f.write(f"- 分享 / Shares: {item['share_count']}\n")
            f.write(f"- 播放 / Plays: {item['play_count']}\n")
            f.write(f"- 话题 / Tags: #{item['tag']}\n")
            f.write(f"- 内容总结 / Summary: {title}\n\n")
    
    return len(items)

if __name__ == "__main__":
    print("=" * 60)
    print("内容捕手 - AI技术热门内容抓取 (2026-04-06)")
    print("=" * 60)
    
    existing_bilibili = get_existing_count(BILIBILI_FILE)
    existing_douyin = get_existing_count(DOUYIN_FILE)
    print(f"\n当前已有: B站 {existing_bilibili}条, 抖音 {existing_douyin}条")
    print(f"目标: 每平台100条")
    
    print("\n[1/4] 正在抓取 B站 AI技术热门内容...")
    bilibili_items = get_bilibili_ai_content()
    print(f"  -> 获取到 {len(bilibili_items)} 条原始数据")
    
    if bilibili_items:
        n = append_bilibili_to_file(bilibili_items, existing_bilibili + 1)
        print(f"  -> 追加写入 {n} 条到 {BILIBILI_FILE}")
    else:
        print("  -> B站API受限，跳过")
    
    print("\n[2/4] 正在抓取 抖音 AI技术热门内容...")
    douyin_items = get_douyin_ai_content()
    print(f"  -> 获取到 {len(douyin_items)} 条原始数据")
    
    if douyin_items:
        n = append_douyin_to_file(douyin_items, existing_douyin + 1)
        print(f"  -> 追加写入 {n} 条到 {DOUYIN_FILE}")
    else:
        print("  -> 抖音无公开API，尝试备选方案...")
        # Try fetching the web search page instead
        try:
            url = "https://www.douyin.com/search/AI%E6%8A%80%E6%9C%AF?type=video"
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html',
            })
            with urllib.request.urlopen(req, timeout=10) as r:
                content = r.read().decode('utf-8', errors='ignore')
                # Try to find video data in the HTML
                import re
                # Look for JSON data embedded in the page
                patterns = [
                    r'"aweme_id":"(\w+)"',
                    r'"desc":"([^"]{10,200})"',
                    r'"nickname":"([^"]{1,50})"',
                ]
                # This is a fallback, results may be limited
                print(f"  -> 网页内容长度: {len(content)} bytes")
        except Exception as e:
            print(f"  -> 备选方案失败: {e}")
    
    print("\n[3/4] 最终统计...")
    total_b = get_existing_count(BILIBILI_FILE)
    total_d = get_existing_count(DOUYIN_FILE)
    print(f"  B站累计: {total_b} 条 (目标100)")
    print(f"  抖音累计: {total_d} 条 (目标100)")
    
    if total_b < 100 or total_d < 100:
        remaining_b = max(0, 100 - total_b)
        remaining_d = max(0, 100 - total_d)
        print(f"\n  ⚠️  未达目标，B站还差{remaining_b}条，抖音还差{remaining_d}条")
        print(f"  💡 提示: 抖音公开API受限，建议手动补充或使用Apify TikTok scraper")
    else:
        print(f"\n  ✅ 目标达成!")
    
    print("\n[4/4] 完成!")
