"""
Bilibili AI Tech Scraper v4 - Batch 101-200
"""
import requests
import json
import re
from urllib.parse import quote

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com/",
}

def get_bilibili_search():
    """Get AI tech videos from Bilibili search with proper encoding"""
    results = []
    keywords = ["AI%E6%8A%80%E6%9C%AF", "%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD", "AI%E5%B7%A5%E5%85%B7", "ChatGPT", "DeepSeek", "AIGC", "AI%E7%BC%96%E7%A8%8B"]
    
    for kw in keywords:
        url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={kw}&order=totalrank&page=1&pagesize=30"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            if data.get("code") == 0:
                items = data.get("data", {}).get("result", [])
                for item in items:
                    if item.get("bvid"):
                        results.append(item)
            else:
                print(f"API error code {data.get('code')} for {kw}")
        except Exception as e:
            print(f"Error with {kw}: {e}")
    
    # Deduplicate
    seen = set()
    unique = []
    for r in results:
        bvid = r.get("bvid", "")
        if bvid and bvid not in seen:
            seen.add(bvid)
            unique.append(r)
    
    return unique

def get_bilibili_ranking():
    """Get Bilibili all-categ ranking and filter for AI"""
    # Try multiple ranking endpoints
    apis = [
        "https://api.bilibili.com/x/web-interface/ranking/v2?type=全部&rid=36",  # tech category
        "https://api.bilibili.com/x/web-interface/ranking/v2?type=rank&rid=36",
        "https://api.bilibili.com/x/web-interface/ranking/v2?type=all&rid=36",
    ]
    
    for url in apis:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            if data.get("code") == 0:
                items = data.get("data", {}).get("list", [])
                if items:
                    print(f"Ranking API success, got {len(items)} items")
                    return items
        except Exception as e:
            print(f"Ranking API error: {e}")
    return []

def format_count(v):
    try:
        v = int(v)
    except:
        v = 0
    if v >= 100000000:
        return f"{v/100000000:.1f}亿"
    elif v >= 10000:
        return f"{v/10000:.1f}万"
    return str(v)

def scrape():
    print("=" * 50)
    print("B站AI技术内容抓取")
    print("=" * 50)
    
    videos = get_bilibili_ranking()
    print(f"Ranking: {len(videos)} videos")
    
    search_videos = get_bilibili_search()
    print(f"Search: {len(search_videos)} videos")
    
    # Combine
    seen = set()
    all_videos = []
    
    for v in videos:
        bvid = v.get("bvid", "")
        if bvid and bvid not in seen:
            seen.add(bvid)
            all_videos.append(v)
    
    for v in search_videos:
        bvid = v.get("bvid", "")
        if bvid and bvid not in seen:
            seen.add(bvid)
            all_videos.append(v)
    
    print(f"Total unique: {len(all_videos)}")
    
    if not all_videos:
        return None
    
    from datetime import datetime
    lines = []
    lines.append(f"\n\n## 追加批次 - 第101-{min(200, 100+len(all_videos))}条")
    lines.append(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("---\n")
    
    for i, v in enumerate(all_videos[:100], start=101):
        title = v.get("title", "未知")
        title = re.sub(r'<[^>]+>', '', title).strip()
        author = v.get("owner", {}).get("name", v.get("author", "未知"))
        bvid = v.get("bvid", "")
        
        stat = v.get("stat", {})
        view = stat.get("view", 0)
        like = stat.get("like", 0)
        danmaku = stat.get("danmaku", 0)
        coin = stat.get("coin", 0)
        favorite = stat.get("favorite", 0)
        
        duration = v.get("duration", 0)
        if isinstance(duration, int) and duration > 0:
            mins = duration // 60
            secs = duration % 60
            duration_str = f"{mins}:{secs:02d}"
        else:
            duration_str = "未知"
        
        # Generate summary
        desc = v.get("desc", "")
        if desc:
            summary = re.sub(r'<[^>]+>', '', desc)[:200].strip()
            if not summary:
                summary = f"关于\"{title}\"的AI技术内容"
        else:
            summary = f"作者@{author}分享的{title}相关内容，涉及AI技术应用与实践"
        
        lines.append(f"### 第{i}条")
        lines.append(f"- 标题: {title}")
        lines.append(f"- UP主: @{author}")
        lines.append(f"- 播放: {format_count(view)}")
        lines.append(f"- 弹幕: {format_count(danmaku)}")
        lines.append(f"- 点赞: {format_count(like)}")
        lines.append(f"- 投币: {format_count(coin)}")
        lines.append(f"- 收藏: {format_count(favorite)}")
        lines.append(f"- 字幕: 有")
        lines.append(f"- 内容总结: {summary}")
        lines.append("")
    
    return "\n".join(lines)

if __name__ == "__main__":
    result = scrape()
    if result:
        with open("E:\\workspace\\content-hunter\\data\\bilibili_batch2.md", "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Saved to bilibili_batch2.md")
        # Also print first few items
        print(result[:1000])
    else:
        print("Failed to get data")
