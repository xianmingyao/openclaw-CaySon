#!/usr/bin/env python3
"""
Bilibili AI Tech Search Scraper v2
Uses requests + proper encoding
"""
import requests
import json
import re
import time

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Origin': 'https://www.bilibili.com',
    'Referer': 'https://www.bilibili.com/',
    'Cookie': 'SESSDATA=; bili_jct=;',  # empty cookies
})

def search_bilibili(keyword, page=1, page_size=30):
    """Search Bilibili videos via API"""
    import urllib.parse
    encoded_kw = urllib.parse.quote(keyword)
    url = f"https://api.bilibili.com/x/web-interface/search/type?search_key={encoded_kw}&category_id=0&search_type=video&order=totalrank&duration=0&page={page}&page_size={page_size}&platform=web&highlight=1"
    
    try:
        resp = session.get(url, timeout=10)
        resp.encoding = 'utf-8'
        print(f"Status: {resp.status_code}, Length: {len(resp.text)}")
        print(f"Response preview: {resp.text[:200]}")
        
        data = resp.json()
        print(f"Code: {data.get('code')}, Message: {data.get('message')}")
        
        if data.get('code') == 0:
            return data.get('data', {}).get('result', [])
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def format_view_count(v):
    if v >= 10000:
        return f"{v/10000:.1f}万"
    return str(v)

def main():
    keyword = "AI人工智能"
    print(f"Searching Bilibili for: {keyword}")
    
    all_results = []
    for page in range(1, 4):
        print(f"\nFetching page {page}...")
        results = search_bilibili(keyword, page=page, page_size=30)
        if not results:
            continue
        all_results.extend(results)
        print(f"Got {len(results)} results, total: {len(all_results)}")
        time.sleep(2)
    
    print(f"\nTotal results: {len(all_results)}")
    
    if not all_results:
        print("No results - trying alternative search...")
        # Try with different order
        keyword2 = "人工智能技术"
        for page in range(1, 3):
            results = search_bilibili(keyword2, page=page, page_size=30)
            if results:
                all_results.extend(results)
            time.sleep(1)
    
    lines = [f"# B站 AI人工智能 热门视频\n"]
    lines.append(f"抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"搜索关键词: {keyword}\n")
    lines.append(f"总计: {len(all_results)} 条\n")
    lines.append("---\n")
    
    for i, v in enumerate(all_results[:100], 1):
        title = v.get('title', '').replace('<em class="keyword">', '').replace('</em>', '')
        author = v.get('author', '')
        play = v.get('play', 0)
        video_review = v.get('video_review', 0)
        favorites = v.get('favorites', 0)
        likes = v.get('like', 0)
        duration = v.get('duration', '')
        description = v.get('description', '')[:150]
        arcurl = v.get('arcurl', '')
        bvid = v.get('bvid', '')
        
        lines.append(f"### 第{i}条\n")
        lines.append(f"- 标题: {title}\n")
        lines.append(f"- UP主: {author}\n")
        lines.append(f"- 播放: {format_view_count(play)}\n")
        lines.append(f"- 弹幕: {format_view_count(video_review)}\n")
        lines.append(f"- 点赞: {format_view_count(likes)}\n")
        lines.append(f"- 收藏: {format_view_count(favorites)}\n")
        lines.append(f"- 时长: {duration}\n")
        lines.append(f"- 内容总结: {description}...\n")
        lines.append(f"- 链接: {arcurl}\n")
        lines.append("\n")
    
    content = '\n'.join(lines)
    
    output_path = r"E:\workspace\content-hunter-data\data\bilibili.md"
    with open(output_path, 'a', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\nDone! Appended {min(len(all_results), 100)} items to {output_path}")

if __name__ == '__main__':
    main()
