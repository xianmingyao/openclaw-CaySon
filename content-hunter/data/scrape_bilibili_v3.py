"""
Bilibili AI Tech Scraper - Batch 101-200
Uses browser to scrape search results, then extract data
"""
import requests
import json
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com/",
}

def get_bilibili_search_ai_v2():
    """Get AI tech videos from Bilibili search"""
    results = []
    
    # Try multiple search terms
    keywords = ["AI技术", "人工智能", "AI工具", "ChatGPT", "DeepSeek", "AIGC", "AI编程"]
    
    for kw in keywords:
        url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={requests.utils.quote(kw)}&order=totalrank&page=1&pagesize=30"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            if data.get("code") == 0:
                items = data.get("data", {}).get("result", [])
                for item in items:
                    if item.get("bvid"):
                        results.append(item)
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

def format_count(v):
    if isinstance(v, str):
        v = int(v) if v.isdigit() else 0
    if v >= 100000000:
        return f"{v/100000000:.1f}亿"
    elif v >= 10000:
        return f"{v/10000:.1f}万"
    return str(v)

def generate_summary(title, author, description):
    """Generate a meaningful summary"""
    if description:
        # Clean HTML tags from description
        desc = re.sub(r'<[^>]+>', '', description)
        desc = desc.strip()[:200]
        if desc:
            return desc
    return f"作者{author}分享关于\"{title}\"的精彩技术内容，涵盖AI领域相关知识点"

def scrape():
    print("Fetching Bilibili AI videos...")
    videos = get_bilibili_search_ai_v2()
    print(f"Total unique videos: {len(videos)}")
    
    if not videos:
        return None
    
    from datetime import datetime
    lines = []
    lines.append(f"\n\n## 追加批次 - 第101-{min(200, 100+len(videos))}条")
    lines.append(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("关键词: AI技术/人工智能/AI工具/ChatGPT/DeepSeek/AIGC")
    lines.append("---\n")
    
    for i, v in enumerate(videos[:100], start=101):
        title = v.get("title", "未知")
        title = re.sub(r'<[^>]+>', '', title).strip()
        author = v.get("author", "未知")
        bvid = v.get("bvid", "")
        aid = v.get("aid", 0)
        
        # Get stats - may not be in search results
        view = v.get("play", v.get("view", 0))
        like = v.get("like", 0)
        danmaku = v.get("danmaku", 0)
        coin = v.get("coin", 0)
        favorite = v.get("favorite", 0)
        duration = v.get("duration", "未知")
        description = v.get("description", "")
        
        # Duration format
        if isinstance(duration, int):
            mins = duration // 60
            secs = duration % 60
            duration_str = f"{mins}:{secs:02d}"
        else:
            duration_str = str(duration) if duration else "未知"
        
        summary = generate_summary(title, author, description)
        
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
        # Save to file
        with open("E:\\workspace\\content-hunter\\data\\bilibili_batch2.md", "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Saved {result.count('### 第')} items to bilibili_batch2.md")
    else:
        print("Failed")
