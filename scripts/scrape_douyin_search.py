#!/usr/bin/env python
"""Scrape Douyin AI content via search engine indexing."""

import urllib.request
import urllib.parse
import json
import os
import re
import time
from datetime import datetime

DATA_DIR = os.path.expanduser("~/.openclaw/workspace/content-hunter/data")
DOUYIN_FILE = os.path.join(DATA_DIR, "douyin.md")

SEARCH_QUERIES = [
    "site:douyin.com AI技术",
    "site:douyin.com 人工智能",
    "site:douyin.com ChatGPT",
    "site:douyin.com 大模型",
    "site:douyin.com AIGC",
    "site:douyin.com AI工具",
    "site:douyin.com AI绘画",
    "site:douyin.com LLM大模型",
    "site:douyin.com AI编程",
    "site:douyin.com DeepSeek",
    "site:douyin.com AI生成",
    "site:douyin.com AI视频",
    "site:douyin.com 机器学习",
    "site:douyin.com 深度学习",
    "site:douyin.com AI应用",
    "site:douyin.com AI Agent",
    "site:douyin.com RAG 大模型",
    "site:douyin.com GPT-5",
    "site:douyin.com AI变现",
    "site:douyin.com AI教程",
]

def search_duckduckgo(query):
    """Search via DuckDuckGo HTML."""
    url = f"https://duckduckgo.com/html/?q={urllib.parse.quote(query)}"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            content = r.read().decode('utf-8', errors='ignore')
            return content
    except Exception as e:
        print(f"    Error: {e}")
        return ""

def extract_douyin_results(html_content):
    """Extract Douyin video info from DuckDuckGo search results."""
    items = []
    
    # Find all result blocks
    # Pattern: <a href="...">title</a> ... snippet
    pattern = r'<a class="result__a" href="(https?://(?:www\.)?douyin\.com/(?:video/|search/)[^"]+)"[^>]*>([^<]+)</a>'
    matches = re.findall(pattern, html_content)
    
    for url, title in matches:
        title = re.sub(r'<[^>]+>', '', title).strip()
        if len(title) < 5:
            continue
        
        # Try to extract video ID from URL
        video_id_match = re.search(r'/video/(\d+)', url)
        video_id = video_id_match.group(1) if video_id_match else url
        
        items.append({
            'title': title,
            'url': url,
            'video_id': video_id,
        })
    
    # Also try to find snippets
    snippet_pattern = r'<a class="result__a"[^>]*href="(https?://(?:www\.)?douyin\.com/(?:video/|search/)[^"]+)"[^>]*>([^<]+)</a>.*?<a class="result__snippet"[^>]*>([^<]+)</a>'
    snippet_matches = re.findall(snippet_pattern, html_content, re.DOTALL)
    for url, title, snippet in snippet_matches:
        title = re.sub(r'<[^>]+>', '', title).strip()
        snippet = re.sub(r'<[^>]+>', '', snippet).strip()
        if len(title) < 5:
            continue
        video_id_match = re.search(r'/video/(\d+)', url)
        video_id = video_id_match.group(1) if video_id_match else url
        items.append({
            'title': title,
            'url': url,
            'snippet': snippet,
            'video_id': video_id,
        })
    
    return items

def search_google(query):
    """Search via Google."""
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&hl=zh-CN"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            content = r.read().decode('utf-8', errors='ignore')
            return content
    except Exception as e:
        print(f"    Google Error: {e}")
        return ""

def extract_from_google(html_content):
    """Extract Douyin results from Google search."""
    items = []
    # Google result pattern
    pattern = r'<a href="(https?://(?:www\.)?douyin\.com/(?:video/|search/)[^"&amp;]+)"[^>]*>([^<]+)</a>'
    matches = re.findall(pattern, html_content)
    for url, title in matches:
        title = re.sub(r'<[^>]+>', '', title).strip()
        if len(title) < 5:
            continue
        video_id_match = re.search(r'/video/(\d+)', url)
        video_id = video_id_match.group(1) if video_id_match else url
        items.append({
            'title': title,
            'url': url,
            'video_id': video_id,
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

def append_to_file(items, start_num):
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Dedupe by video_id
    seen = {}
    if os.path.exists(DOUYIN_FILE):
        with open(DOUYIN_FILE, 'r', encoding='utf-8') as f:
            existing = re.findall(r'- 抖音ID: (.+)', f.read())
            seen = set(existing)
    
    new_items = [it for it in items if it['video_id'] not in seen]
    
    with open(DOUYIN_FILE, 'a', encoding='utf-8') as f:
        if start_num == 1:
            f.write(f"# 抖音 AI技术热门内容\n\n")
            f.write(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        written = 0
        for i, item in enumerate(new_items):
            num = start_num + i
            title = item['title'][:200] if item['title'] else '暂无标题'
            snippet = item.get('snippet', '')[:200]
            summary = snippet if snippet else title
            
            f.write(f"### 第{num}条\n")
            f.write(f"- 标题 / Title: {title}\n")
            f.write(f"- 作者 / Author: @未知作者\n")
            f.write(f"- 抖音ID: {item['video_id']}\n")
            f.write(f"- 链接 / URL: {item['url']}\n")
            f.write(f"- 点赞 / Likes: 未知\n")
            f.write(f"- 评论 / Comments: 未知\n")
            f.write(f"- 分享 / Shares: 未知\n")
            f.write(f"- 播放 / Plays: 未知\n")
            f.write(f"- 话题 / Tags: #AI技术\n")
            f.write(f"- 内容总结 / Summary: {summary}\n\n")
            written += 1
    
    return written, new_items

if __name__ == "__main__":
    print("=" * 60)
    print("抖音 AI内容搜索抓取 (via 搜索引擎索引)")
    print("=" * 60)
    
    existing = get_existing_count()
    print(f"\n当前已有: {existing} 条 (目标: 100)")
    print(f"搜索 {len(SEARCH_QUERIES)} 个关键词...\n")
    
    all_items = []
    seen_urls = set()
    
    for i, query in enumerate(SEARCH_QUERIES):
        print(f"[{i+1}/{len(SEARCH_QUERIES)}] {query}")
        
        # Try DuckDuckGo
        html = search_duckduckgo(query)
        if html:
            items = extract_douyin_results(html)
            for item in items:
                if item['url'] not in seen_urls:
                    seen_urls.add(item['url'])
                    all_items.append(item)
            print(f"    -> DuckDuckGo: {len(items)} results (total unique: {len(all_items)})")
        
        time.sleep(1)  # Be polite
        
        # Also try Google
        html_g = search_google(query)
        if html_g:
            items_g = extract_from_google(html_g)
            for item in items_g:
                if item['url'] not in seen_urls:
                    seen_urls.add(item['url'])
                    all_items.append(item)
            print(f"    -> Google: {len(items_g)} results (total unique: {len(all_items)})")
        
        time.sleep(2)
    
    print(f"\n总共获取: {len(all_items)} 条唯一结果")
    
    if all_items:
        new_start = existing + 1
        written, new_items = append_to_file(all_items, new_start)
        print(f"追加写入: {written} 条新数据")
    
    final = get_existing_count()
    print(f"最终累计: {final} 条")
    
    if final >= 100:
        print("\n目标达成!")
    else:
        print(f"\n还差 {100 - final} 条 (抖音需登录API，建议手动补充)")
