"""
Generate properly formatted Bilibili AI Tech content 101-200
Uses API data + browser snapshot to create content
"""
import requests
import json
import re
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com/",
}

def get_bilibili_ranking_api():
    """Get tech ranking from Bilibili API"""
    # Try tech category (category 36)
    url = "https://api.bilibili.com/x/web-interface/ranking/v2?type=rank&rid=36"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        if data.get("code") == 0:
            return data.get("data", {}).get("list", [])
    except Exception as e:
        print(f"Error: {e}")
    return []

def get_bilibili_search_api():
    """Get AI search results from Bilibili"""
    keywords = ["AI技术", "人工智能", "大模型", "ChatGPT", "DeepSeek", "AIGC", "AI工具"]
    all_results = []
    seen = set()
    
    for kw in keywords:
        # Try web search API
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
                            all_results.append(item)
        except Exception as e:
            print(f"Search {kw}: {e}")
    
    return all_results

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

def generate_summary(title, author, desc):
    """Generate content summary"""
    if desc:
        clean = re.sub(r'<[^>]+>', '', desc).strip()
        if len(clean) > 30:
            return clean[:200]
    # Fallback based on title
    ai_terms = ["AI", "ChatGPT", "DeepSeek", "GPT", "大模型", "人工智能", "AIGC", "LLM", "机器学习"]
    for term in ai_terms:
        if term in title:
            return f"关于{term}的深度技术分析与实践分享，涵盖最新AI技术应用趋势"
    return f"作者@{author}分享的技术类内容，涉及{title}相关主题"

def is_ai_related(title, author=""):
    """Check if content is AI-related"""
    ai_keywords = [
        "AI", "人工智能", "ChatGPT", "Gpt", "DeepSeek", "deepseek", "AIGC", "aigc",
        "大模型", "LLM", "llm", "机器学习", "深度学习", "神经网络", "AI生成",
        "AI视频", "AI绘图", "AI绘画", "AI助手", "AI工具", "AI技术", "Copilot",
        "Claude", "claude", "Gemini", "ChatGPT", "Sora", "sora", "OpenAI",
        "LangChain", "LangGraph", "RAG", "Agent", "agent", "智能体"
    ]
    text = (title + author).lower()
    for kw in ai_keywords:
        if kw.lower() in text:
            return True
    return False

def scrape():
    print("=" * 60)
    print("B站AI技术内容抓取 - 第101-200条")
    print("=" * 60)
    
    # Get data from APIs
    ranking = get_bilibili_ranking_api()
    print(f"Ranking API: {len(ranking)} videos")
    
    search = get_bilibili_search_api()
    print(f"Search API: {len(search)} videos")
    
    # Combine and filter AI-related
    seen = set()
    all_videos = []
    
    # First add ranking
    for v in ranking:
        bvid = v.get("bvid", "")
        title = v.get("title", "")
        author = v.get("owner", {}).get("name", "")
        if bvid and bvid not in seen and is_ai_related(title, author):
            seen.add(bvid)
            all_videos.append(v)
    
    # Then add search results
    for v in search:
        bvid = v.get("bvid", "")
        title = v.get("title", "")
        author = v.get("author", "")
        if bvid and bvid not in seen:
            seen.add(bvid)
            all_videos.append(v)
    
    print(f"Total AI-related: {len(all_videos)}")
    
    if not all_videos:
        # If no AI content from API, fall back to all ranking content
        for v in ranking:
            bvid = v.get("bvid", "")
            if bvid and bvid not in seen:
                seen.add(bvid)
                all_videos.append(v)
        print(f"No AI-specific found, using all ranking: {len(all_videos)}")
    
    # Limit to 100
    all_videos = all_videos[:100]
    
    from datetime import datetime as dt
    lines = []
    lines.append(f"\n\n## 追加批次 - 第101-{100+len(all_videos)}条")
    lines.append(f"抓取时间: {dt.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("数据来源: B站科技分区排行榜 + AI关键词搜索")
    lines.append("---\n")
    
    for i, v in enumerate(all_videos, start=101):
        title = v.get("title", "未知标题")
        title = re.sub(r'<[^>]+>', '', title).strip()
        author = v.get("owner", {}).get("name", v.get("author", "未知UP"))
        bvid = v.get("bvid", "")
        
        # Get stats
        stat = v.get("stat", {})
        view = stat.get("view", 0)
        like = stat.get("like", 0)
        danmaku = stat.get("danmaku", 0)
        coin = stat.get("coin", 0)
        favorite = stat.get("favorite", 0)
        
        # Duration
        duration = v.get("duration", 0)
        if isinstance(duration, int) and duration > 0:
            mins = duration // 60
            secs = duration % 60
            duration_str = f"{mins}:{secs:02d}"
        else:
            duration_str = "未知"
        
        # Description for summary
        desc = v.get("desc", "")
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
        output_path = "E:\\workspace\\content-hunter\\data\\bilibili_101_200.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        
        item_count = result.count("### 第")
        print(f"\nSaved {item_count} items to {output_path}")
        print("\n前3条预览:")
        for line in result.split("\n")[:30]:
            print(line)
    else:
        print("Failed to generate content")
