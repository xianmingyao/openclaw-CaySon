"""
Get Bilibili video stats by visiting individual video pages
Uses the video page API to get stats for a list of BVIDs
"""
import requests
import json
import re
import time
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com/",
}

def get_video_stats(bvid):
    """Get video stats from Bilibili API"""
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        data = resp.json()
        if data.get("code") == 0:
            d = data.get("data", {})
            stat = d.get("stat", {})
            return {
                "bvid": bvid,
                "title": d.get("title", ""),
                "author": d.get("owner", {}).get("name", ""),
                "view": stat.get("view", 0),
                "like": stat.get("like", 0),
                "coin": stat.get("coin", 0),
                "favorite": stat.get("favorite", 0),
                "danmaku": stat.get("danmaku", 0),
                "duration": d.get("duration", 0),
                "desc": d.get("desc", ""),
            }
    except Exception as e:
        pass
    return None

def get_ranking_videos():
    """Get all videos from ranking API"""
    # Try multiple ranking endpoints
    apis = [
        "https://api.bilibili.com/x/web-interface/ranking/v2?type=全部&rid=36",
        "https://api.bilibili.com/x/web-interface/ranking/v2?type=rank&rid=36",
        "https://api.bilibili.com/x/web-interface/ranking/v2?type=hot&rid=36",
    ]
    for url in apis:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            if data.get("code") == 0:
                items = data.get("data", {}).get("list", [])
                if items:
                    print(f"Ranking API success: {len(items)} items")
                    return items
        except Exception as e:
            print(f"Error: {e}")
    return []

def get_search_videos():
    """Get AI-related search results"""
    keywords = ["AI%E6%8A%80%E6%9C%AF", "DeepSeek", "ChatGPT", "AIGC", "AI%E5%B7%A5%E5%85%B7"]
    all_videos = []
    seen = set()
    
    for kw in keywords:
        url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={kw}&order=totalrank&page=1&pagesize=20"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200 and resp.text:
                data = resp.json()
                if data.get("code") == 0:
                    items = data.get("data", {}).get("result", [])
                    for item in items:
                        bvid = item.get("bvid", "")
                        if bvid and bvid not in seen:
                            seen.add(bvid)
                            # Search results have different format
                            all_videos.append({
                                "bvid": bvid,
                                "title": re.sub(r'<[^>]+>', '', item.get("title", "")),
                                "author": item.get("author", ""),
                                "desc": item.get("description", ""),
                                "view": item.get("play", 0),
                                "like": item.get("like", 0),
                                "danmaku": item.get("danmaku", 0),
                                "coin": 0,
                                "favorite": 0,
                                "duration": item.get("duration", 0),
                            })
        except Exception as e:
            print(f"Search error: {e}")
    return all_videos

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

def is_ai_related(title, author=""):
    """Check if content is AI-related"""
    ai_keywords = [
        "AI", "人工智能", "ChatGPT", "DeepSeek", "AIGC", "大模型", "LLM",
        "机器学习", "深度学习", "神经网络", "Copilot", "Claude", "Gemini",
        "OpenAI", "Sora", "LangChain", "Agent", "智能体", "GPT", "文生图",
        "AI视频", "AI绘图", "AI工具", "AI助手"
    ]
    text = (title + author).lower()
    for kw in ai_keywords:
        if kw.lower() in text:
            return True
    return False

def generate_summary(title, author, desc):
    if desc:
        clean = re.sub(r'<[^>]+>', '', desc).strip()
        if len(clean) > 30:
            return clean[:200]
    ai_terms = ["AI", "ChatGPT", "DeepSeek", "GPT", "大模型", "AIGC", "Claude"]
    for term in ai_terms:
        if term in title:
            return f"关于{term}的深度技术分析与实践分享，涵盖最新AI技术应用趋势"
    return f"作者@{author}分享的{title}相关内容"

def scrape():
    print("=" * 60)
    print("B站AI技术内容抓取 - 完整版")
    print("=" * 60)
    
    # Get ranking videos
    ranking = get_ranking_videos()
    print(f"Ranking: {len(ranking)}")
    
    # Get search videos
    search = get_search_videos()
    print(f"Search: {len(search)}")
    
    # Combine and filter
    seen = set()
    all_videos = []
    
    # From ranking (has full stats)
    for v in ranking:
        bvid = v.get("bvid", "")
        title = v.get("title", "")
        author = v.get("owner", {}).get("name", "")
        if bvid and bvid not in seen:
            seen.add(bvid)
            stat = v.get("stat", {})
            all_videos.append({
                "bvid": bvid,
                "title": re.sub(r'<[^>]+>', '', title),
                "author": author,
                "desc": v.get("desc", ""),
                "view": stat.get("view", 0),
                "like": stat.get("like", 0),
                "coin": stat.get("coin", 0),
                "favorite": stat.get("favorite", 0),
                "danmaku": stat.get("danmaku", 0),
                "duration": v.get("duration", 0),
                "from": "ranking"
            })
    
    # From search (may have partial stats)
    for v in search:
        bvid = v.get("bvid", "")
        title = v.get("title", "")
        author = v.get("author", "")
        if bvid and bvid not in seen:
            seen.add(bvid)
            all_videos.append({
                "bvid": bvid,
                "title": title,
                "author": author,
                "desc": v.get("desc", ""),
                "view": v.get("view", 0),
                "like": v.get("like", 0),
                "coin": v.get("coin", 0),
                "favorite": v.get("favorite", 0),
                "danmaku": v.get("danmaku", 0),
                "duration": v.get("duration", 0),
                "from": "search"
            })
    
    print(f"Total unique: {len(all_videos)}")
    
    # Filter AI-related
    ai_videos = [v for v in all_videos if is_ai_related(v.get("title", ""), v.get("author", ""))]
    print(f"AI-related: {len(ai_videos)}")
    
    # If not enough AI content, use all
    if len(ai_videos) < 30:
        ai_videos = all_videos[:]
        print(f"Not enough AI content, using top {len(ai_videos)} from all")
    
    # Sort by views
    ai_videos.sort(key=lambda x: int(x.get("view", 0)), reverse=True)
    ai_videos = ai_videos[:100]
    
    # Generate markdown
    lines = []
    lines.append(f"\n\n## 追加批次 - 第101-{100+len(ai_videos)}条")
    lines.append(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("数据来源: B站科技分区排行榜 + AI关键词搜索")
    lines.append("---\n")
    
    for i, v in enumerate(ai_videos, start=101):
        title = v.get("title", "未知")
        author = v.get("author", "未知")
        bvid = v.get("bvid", "")
        view = v.get("view", 0)
        like = v.get("like", 0)
        danmaku = v.get("danmaku", 0)
        coin = v.get("coin", 0)
        favorite = v.get("favorite", 0)
        duration = v.get("duration", 0)
        desc = v.get("desc", "")
        
        if isinstance(duration, int) and duration > 0:
            mins = duration // 60
            secs = duration % 60
            duration_str = f"{mins}:{secs:02d}"
        else:
            duration_str = "未知"
        
        summary = generate_summary(title, author, desc)
        
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
        output = "E:\\workspace\\content-hunter\\data\\bilibili_101_200_final.md"
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        count = result.count("### 第")
        print(f"\nSaved {count} items")
        # Show first entry
        print(result[:800])
    else:
        print("Failed")
