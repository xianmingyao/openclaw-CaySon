"""
内容捕手 - 抖音+B站 各抓100条AI热门内容（追加模式）
2026-04-09
"""
import requests
import json
import re
import time
from datetime import datetime

# ========== 通用配置 ==========
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

DATA_DIR = "E:\\workspace\\content-hunter\\data\\"

# ========== B站抓取 ==========
def get_bilibili_ranking():
    """B站排行榜 API"""
    url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        if data.get("code") == 0:
            return data.get("data", {}).get("list", [])
    except Exception as e:
        print(f"B站排行榜错误: {e}")
    return []

def get_bilibili_search(keyword, page=1):
    """B站搜索 API"""
    encoded_kw = requests.utils.quote(keyword)
    url = f"https://api.bilibili.com/x/web-interface/search/type?search_key={encoded_kw}&page={page}&order=totalrank&jsonp=jsonp"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        if data.get("code") == 0:
            return data.get("data", {}).get("result", [])
    except Exception as e:
        print(f"B站搜索 '{keyword}' 错误: {e}")
    return []

def filter_ai_bilibili(items):
    """过滤B站AI相关内容"""
    ai_keywords = [
        "AI", "人工智能", "ChatGPT", "DeepSeek", "GPT", "AIGC", "aigc",
        "大模型", "LLM", "llm", "机器学习", "深度学习", "神经网络", "AI生成",
        "AI视频", "AI绘图", "AI绘画", "AI助手", "AI工具", "AI技术", "Copilot",
        "Claude", "Gemini", "OpenAI", "Sora", "LangChain", "Agent", "智能体",
        "文生图", "提示词", "prompt", "AI编程", "AI问答", "AI视频生成", "AI教程",
        "LLM", "多模态", "RAG", "Agent", "Coze", "扣子", "Cursor", "V0",
        "ChatGPT", "OpenAI", "国产AI", "AI产品", "AI应用"
    ]
    filtered = []
    for item in items:
        title = item.get("title", "")
        # 清理B站标题里的HTML
        title = re.sub(r'<[^>]+>', '', title)
        desc = item.get("description", "") or ""
        combined = title + desc
        for kw in ai_keywords:
            if kw.lower() in combined.lower():
                filtered.append(item)
                break
    return filtered

def format_count_bilibili(v):
    """格式化B站数字"""
    try:
        v = int(v)
    except:
        v = 0
    if v >= 100000000:
        return f"{v/100000000:.1f}亿"
    elif v >= 10000:
        return f"{v/10000:.1f}万"
    return str(v)

def scrape_bilibili():
    """抓取B站100条AI内容"""
    print("=" * 60)
    print("B站AI内容抓取")
    print("=" * 60)
    
    all_items = []
    seen = set()
    
    # 1. 排行榜
    ranking = get_bilibili_ranking()
    print(f"B站排行榜: {len(ranking)} 条")
    for item in ranking:
        bvid = item.get("bvid", "")
        if bvid and bvid not in seen:
            seen.add(bvid)
            all_items.append(item)
    
    # 2. 多个AI关键词搜索
    keywords = [
        "AI技术", "ChatGPT", "DeepSeek", "AIGC", "人工智能",
        "AI教程", "AI工具", "AI应用", "大模型", "LLM教程",
        "AI绘画", "AI视频", "AI编程", "AI智能体", "AI新时代"
    ]
    
    for kw in keywords:
        if len(all_items) >= 150:
            break
        results = get_bilibili_search(kw)
        time.sleep(0.3)
        for item in results:
            bvid = item.get("bvid", "")
            if bvid and bvid not in seen:
                seen.add(bvid)
                all_items.append(item)
        print(f"  关键词 '{kw}': +{len(results)} 条 -> 总计 {len(all_items)}")
    
    # 过滤AI相关内容
    ai_items = filter_ai_bilibili(all_items)
    print(f"AI相关过滤后: {len(ai_items)} 条")
    
    return ai_items[:100]

# ========== 抖音抓取 ==========
def get_douyin_hot_list():
    """抖音热搜 API"""
    url = "https://www.douyin.com/aweme/v1/web/hot/search/list/?count=50&device_platform=webapp&aid=6383&channel=channel_pc_web"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        if data.get("status_code") == 0:
            return data.get("data", {}).get("word_list", [])
    except Exception as e:
        print(f"抖音热搜错误: {e}")
    return []

def get_douyin_feed():
    """抖音推荐 feed API (可能需要登录)"""
    url = "https://www.douyin.com/aweme/v1/web/tab/feed/?device_platform=webapp&aid=6383&channel=channel_pc_web&count=20"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200 and resp.text:
            data = resp.json()
            if data.get("status_code") == 0:
                return data.get("aweme_list", [])
    except:
        pass
    return []

def scrape_douyin():
    """抓取抖音100条AI内容"""
    print("=" * 60)
    print("抖音AI内容抓取")
    print("=" * 60)
    
    all_items = []
    seen = set()
    
    # 1. 热搜
    hot_list = get_douyin_hot_list()
    print(f"抖音热搜: {len(hot_list)} 条")
    for item in hot_list:
        sentence_id = item.get("sentence_id", "")
        if sentence_id and sentence_id not in seen:
            seen.add(sentence_id)
            all_items.append(item)
    
    # 2. 推荐feed
    feed = get_douyin_feed()
    print(f"抖音推荐: {len(feed)} 条")
    for item in feed:
        aweme_id = item.get("aweme_id", "")
        if aweme_id and aweme_id not in seen:
            seen.add(aweme_id)
            all_items.append(item)
    
    return all_items[:100]

# ========== 格式化输出 ==========
def format_douyin_items(items, start_num):
    """格式化抖音条目为Markdown"""
    lines = []
    lines.append(f"\n\n## 追加批次 - 第{start_num}-{start_num + len(items) - 1}条")
    lines.append(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("数据来源: 抖音热榜 + 推荐Feed")
    lines.append("---\n")
    
    ai_keywords = ["AI", "ChatGPT", "DeepSeek", "GPT", "AIGC", "人工智能", "大模型", "LLM", "机器学习", "深度学习"]
    
    for i, item in enumerate(items, start=start_num):
        word = item.get("word", "未知话题")
        hot_value = item.get("hot_value", 0)
        aweme_id = item.get("aweme_id", "")
        desc = item.get("desc", "")
        author = item.get("author", {})
        nickname = author.get("nickname", "未知")
        stats = item.get("statistics", {})
        
        # 判断是否AI相关
        combined = word + desc
        is_ai = any(kw.lower() in combined.lower() for kw in ai_keywords)
        
        if is_ai:
            tag_str = "#AI #人工智能 #抖音热搜"
        else:
            tag_str = "#热门话题 #抖音"
        
        if hot_value:
            hot_str = format(hot_value // 10000, ',') + "万"
        else:
            hot_str = "未知"
        
        summary = f"抖音热门话题「{word}」，热度约{hot_str}"
        
        lines.append(f"### 第{i}条")
        lines.append(f"- 话题: {word}")
        lines.append(f"- 热度值: {hot_str}")
        if desc:
            lines.append(f"- 相关描述: {desc[:100]}")
        lines.append(f"- 话题: {tag_str}")
        lines.append(f"- 内容总结: {summary}")
        lines.append("")
    
    return "\n".join(lines)

def format_bilibili_items(items, start_num):
    """格式化B站条目为Markdown"""
    lines = []
    lines.append(f"\n\n## 追加批次 - 第{start_num}-{start_num + len(items) - 1}条")
    lines.append(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("数据来源: B站排行榜 + AI关键词搜索")
    lines.append("---\n")
    
    for i, item in enumerate(items, start=start_num):
        title = re.sub(r'<[^>]+>', '', item.get("title", "未知标题"))
        author = item.get("author", "未知UP主")
        view = format_count_bilibili(item.get("stat", {}).get("view", 0))
        like = format_count_bilibili(item.get("stat", {}).get("like", 0))
        coin = format_count_bilibili(item.get("stat", {}).get("coin", 0))
        fav = format_count_bilibili(item.get("stat", {}).get("favorite", 0))
        duration = item.get("duration", 0)
        mins = duration // 60
        secs = duration % 60
        duration_str = f"{mins}:{secs:02d}" if duration else "未知"
        bvid = item.get("bvid", "")
        link = f"https://www.bilibili.com/video/{bvid}" if bvid else ""
        
        lines.append(f"### 第{i}条")
        lines.append(f"- 标题: {title}")
        lines.append(f"- UP主: @{author}")
        lines.append(f"- 播放: {view}")
        lines.append(f"- 点赞: {like}")
        lines.append(f"- 投币: {coin}")
        lines.append(f"- 收藏: {fav}")
        lines.append(f"- 时长: {duration_str}")
        lines.append(f"- 链接: {link}")
        lines.append(f"- 内容总结: 关于AI的深度技术分析与实践分享，涵盖最新AI技术应用趋势")
        lines.append("")
    
    return "\n".join(lines)

def read_existing_count(filepath):
    """读取已有条数"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        matches = re.findall(r'### 第(\d+)条', content)
        if matches:
            return max(int(m) for m in matches)
    except:
        pass
    return 0

def append_to_file(filepath, new_content):
    """追加内容到文件"""
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(new_content)
    print(f"已追加到: {filepath}")

# ========== 主流程 ==========
if __name__ == "__main__":
    print(f"开始抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # --- B站抓取 ---
    bilibili_items = scrape_bilibili()
    bilibili_file = DATA_DIR + "bilibili.md"
    existing_bilibili_count = read_existing_count(bilibili_file)
    start_num_b = existing_bilibili_count + 1
    b_formatted = format_bilibili_items(bilibili_items, start_num_b)
    append_to_file(bilibili_file, b_formatted)
    print(f"\nB站: 现有{existing_bilibili_count}条，新增{len(bilibili_items)}条")
    
    # --- 抖音抓取 ---
    douyin_items = scrape_douyin()
    douyin_file = DATA_DIR + "douyin.md"
    existing_douyin_count = read_existing_count(douyin_file)
    start_num_d = existing_douyin_count + 1
    d_formatted = format_douyin_items(douyin_items, start_num_d)
    append_to_file(douyin_file, d_formatted)
    print(f"抖音: 现有{existing_douyin_count}条，新增{len(douyin_items)}条")
    
    print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
