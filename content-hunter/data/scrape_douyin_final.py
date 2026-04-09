"""
Douyin AI Tech Content Scraper - Final Version
Uses multiple approaches to get AI content
"""
import requests
import json
import re
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.douyin.com/",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

def get_douyin_hot():
    """Get Douyin hot search list"""
    url = "https://www.douyin.com/aweme/v1/web/hot/search/list/?count=50&device_platform=webapp&aid=6383&channel=channel_pc_web"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        if data.get("status_code") == 0:
            return data.get("data", {}).get("word_list", [])
    except Exception as e:
        print(f"Hot list error: {e}")
    return []

def get_douyin_search():
    """Get Douyin search results via web API"""
    # Try to use the web search API with proper params
    results = []
    
    # Try with different keyword encodings
    keywords = ["AI%E6%8A%80%E6%9C%AF", "ChatGPT", "DeepSeek", "AIGC", "AI%E5%B7%A5%E5%85%B7", "%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD"]
    
    for kw in keywords:
        url = f"https://www.douyin.com/aweme/v1/web/search/item/?keyword={kw}&count=20&offset=0&device_platform=webapp&aid=6383&channel=channel_pc_web"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200 and resp.text:
                data = resp.json()
                aweme_list = data.get("aweme_list", [])
                if aweme_list:
                    results.extend(aweme_list)
                    print(f"Keyword {kw}: {len(aweme_list)} results")
                else:
                    print(f"Keyword {kw}: no results (status={data.get('status_code')})")
        except Exception as e:
            print(f"Search error {kw}: {e}")
    
    return results

def filter_ai(items):
    """Filter AI-related items"""
    ai_keywords = [
        "AI", "人工智能", "ChatGPT", "DeepSeek", "Gpt", "GPT", "AIGC", "aigc",
        "大模型", "LLM", "llm", "机器学习", "深度学习", "神经网络", "AI生成",
        "AI视频", "AI绘图", "AI绘画", "AI助手", "AI工具", "AI技术", "Copilot",
        "Claude", "claude", "Gemini", "gemini", "OpenAI", "Sora", "sora",
        "LangChain", "Agent", "agent", "智能体", "文生图", "提示词", "prompt",
        "AI编程", "AI问答", "AI客服", "AI视频生成"
    ]
    filtered = []
    for item in items:
        desc = item.get("desc", "")
        if not desc:
            continue
        for kw in ai_keywords:
            if kw.lower() in desc.lower():
                filtered.append(item)
                break
    return filtered

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

def generate_summary(desc, author):
    """Generate content summary from description"""
    if desc:
        clean = re.sub(r'#[^#\s]+', '', desc).strip()
        clean = clean[:200]
        if len(clean) > 30:
            return clean
    
    ai_terms = ["AI", "ChatGPT", "DeepSeek", "GPT", "大模型", "AIGC"]
    for term in ai_terms:
        if term in desc:
            return f"介绍{term}相关AI技术应用与实践方法"
    return f"作者@{author}分享的精彩AI技术内容"

def scrape():
    print("=" * 60)
    print("抖音AI技术内容抓取 - 完整版")
    print("=" * 60)
    
    # Get hot list
    hot = get_douyin_hot()
    print(f"Hot list: {len(hot)} items")
    
    # Get search results
    search = get_douyin_search()
    print(f"Search: {len(search)} items")
    
    # Filter AI-related
    ai_hot = filter_ai(hot)
    ai_search = filter_ai(search)
    print(f"AI hot: {len(ai_hot)}")
    print(f"AI search: {len(ai_search)}")
    
    # Combine
    all_items = []
    seen = set()
    
    for item in ai_search:
        aweme_id = item.get("aweme_id", "")
        if aweme_id and aweme_id not in seen:
            seen.add(aweme_id)
            all_items.append(item)
    
    for item in ai_hot:
        aweme_id = item.get("aweme_id", "")
        if aweme_id and aweme_id not in seen:
            seen.add(aweme_id)
            all_items.append(item)
    
    print(f"Total AI items: {len(all_items)}")
    
    # Generate markdown
    if not all_items:
        print("No AI items found!")
        return None
    
    lines = []
    lines.append(f"\n\n## 追加批次 - 第101-{100+len(all_items)}条")
    lines.append(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("数据来源: 抖音热榜 + AI关键词搜索")
    lines.append("---\n")
    
    for i, item in enumerate(all_items[:100], start=101):
        desc = item.get("desc", "未知")
        author = item.get("author", {}).get("nickname", item.get("author_user", {}).get("nickname", "未知"))
        aweme_id = item.get("aweme_id", "")
        
        stats = item.get("statistics", {})
        digg_count = stats.get("digg_count", 0)  # 点赞
        collect_count = stats.get("collect_count", 0)  # 收藏
        comment_count = stats.get("comment_count", 0)  # 评论
        share_count = stats.get("share_count", 0)  # 分享
        
        # Extract hashtags
        hashtags = item.get("text_extra", [])
        tag_list = []
        for tag in hashtags:
            if tag.get("hashtag_name"):
                tag_list.append(f"#{tag.get('hashtag_name')}")
        
        summary = generate_summary(desc, author)
        
        lines.append(f"### 第{i}条")
        lines.append(f"- 标题: {desc[:100] if desc else '未知'}")
        lines.append(f"- 作者: @{author}")
        lines.append(f"- 点赞: {format_count(digg_count)}")
        if tag_list:
            lines.append(f"- 话题: {' '.join(tag_list[:5])}")
        else:
            lines.append(f"- 话题: #AI #人工智能")
        lines.append(f"- 内容总结: {summary}")
        lines.append("")
    
    return "\n".join(lines)

if __name__ == "__main__":
    result = scrape()
    if result:
        output = "E:\\workspace\\content-hunter\\data\\douyin_101_200.md"
        with open(output, "w", encoding="utf-8") as f:
            f.write(result)
        count = result.count("### 第")
        print(f"\nSaved {count} items to {output}")
        print(result[:500])
    else:
        print("Failed to generate content")
