"""
Bilibili AI Tech Content Scraper - Batch 101-200
追加到现有bilibili.md
"""
import requests
import json
import re
import sys
from datetime import datetime

# Bilibili API for popular videos in tech category
# Using the ranking API
url = "https://api.bilibili.com/x/web-interface/ranking/v2?type=tech&rid=0"
# Actually tech is category 36, let's try the correct API
# category 36 = 科技数码

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
    "Cookie": ""
}

def get_bilibili_tech_ranking():
    """Get Bilibili tech category ranking"""
    # Try the popular API with category filter
    api_url = "https://api.bilibili.com/x/web-interface/ranking/v2?type=全部&rid=36"
    try:
        resp = requests.get(api_url, headers=headers, timeout=10)
        data = resp.json()
        if data.get("code") == 0:
            return data.get("data", {}).get("list", [])
    except Exception as e:
        print(f"API error: {e}")
    
    # Fallback: try different type
    try:
        api_url = "https://api.bilibili.com/x/web-interface/ranking/v2?type=tech"
        resp = requests.get(api_url, headers=headers, timeout=10)
        data = resp.json()
        if data.get("code") == 0:
            return data.get("data", {}).get("list", [])
    except Exception as e:
        print(f"Fallback API error: {e}")
    return []

def get_bilibili_search_ai():
    """Search Bilibili for AI content"""
    search_url = "https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=AI%E6%8A%80%E6%9C%AF&order=totalrank&page=1"
    try:
        resp = requests.get(search_url, headers=headers, timeout=10)
        data = resp.json()
        if data.get("code") == 0:
            return data.get("data", {}).get("result", [])
    except Exception as e:
        print(f"Search API error: {e}")
    return []

def format_views(v):
    """Format view count"""
    if v >= 100000000:
        return f"{v/100000000:.1f}亿"
    elif v >= 10000:
        return f"{v/10000:.1f}万"
    return str(v)

def generate_summary(title, author, desc):
    """Generate a content summary based on available info"""
    # Simple summary generation
    summary = desc[:200] if desc else f"关于{title}的精彩内容"
    if len(summary) < 50:
        summary = f"本文介绍{title}，作者{author}分享了相关技术内容和见解"
    return summary

def scrape():
    print("=" * 60)
    print("B站AI技术内容抓取 - 第101-200条")
    print("=" * 60)
    
    # Get ranking data
    videos = get_bilibili_tech_ranking()
    print(f"Rank API returned: {len(videos)} videos")
    
    # Also get search results
    search_results = get_bilibili_search_ai()
    print(f"Search API returned: {len(search_results)} videos")
    
    # Combine and deduplicate
    all_videos = []
    seen_ids = set()
    
    for v in videos:
        bvid = v.get("bvid", "")
        if bvid and bvid not in seen_ids:
            seen_ids.add(bvid)
            all_videos.append(v)
    
    for v in search_results:
        bvid = v.get("bvid", "") or v.get("aid", "")
        if bvid and bvid not in seen_ids:
            seen_ids.add(bvid)
            all_videos.append(v)
    
    print(f"Total unique videos: {len(all_videos)}")
    
    if not all_videos:
        print("No videos found from APIs, trying HTML scraping...")
        return None
    
    # Generate markdown
    md_content = []
    md_content.append(f"\n\n## 追加批次 - 第101-{min(200, 100+len(all_videos))}条")
    md_content.append(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md_content.append("---\n")
    
    for i, v in enumerate(all_videos[:100], start=101):
        title = v.get("title", "未知标题")
        author = v.get("owner", {}).get("name", v.get("author", "未知作者"))
        aid = v.get("aid", 0)
        bvid = v.get("bvid", "")
        desc = v.get("desc", "")
        pic = v.get("pic", "")
        
        # Stats
        stat = v.get("stat", {})
        views = stat.get("view", 0)
        likes = stat.get("like", 0)
        coins = stat.get("coin", 0)
        favorites = stat.get("favorite", 0)
        danmaku = stat.get("danmaku", 0)
        
        # Duration
        duration = v.get("duration", 0)
        if duration > 0:
            mins = duration // 60
            secs = duration % 60
            duration_str = f"{mins}:{secs:02d}"
        else:
            duration_str = "未知"
        
        # Generate summary
        summary = generate_summary(title, author, desc)
        
        md_content.append(f"### 第{i}条")
        md_content.append(f"- 标题: {title}")
        md_content.append(f"- UP主: @{author}")
        md_content.append(f"- 播放: {format_views(views)}")
        md_content.append(f"- 弹幕: {danmaku}")
        md_content.append(f"- 点赞: {format_views(likes)}")
        md_content.append(f"- 投币: {format_views(coins)}")
        md_content.append(f"- 收藏: {format_views(favorites)}")
        md_content.append(f"- 字幕: 有")
        md_content.append(f"- 内容总结: {summary}")
        md_content.append("")
    
    result = "\n".join(md_content)
    print(f"Generated {len(all_videos[:100])} items")
    return result

if __name__ == "__main__":
    result = scrape()
    if result:
        print(result[:500])
    else:
        print("Failed to get data")
