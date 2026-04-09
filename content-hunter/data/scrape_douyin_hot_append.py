"""
从抖音热榜API抓取AI相关内容
"""
import requests
import re
import os
import json
from datetime import datetime

DATA_DIR = r"E:\workspace\content-hunter\data"
PC_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def count_items(filepath):
    if not os.path.exists(filepath):
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return len(re.findall(r'### 第\d+条', content))

def save_append(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(content)

def is_ai_related(title, author=""):
    ai_kws = [
        'ai', 'chatgpt', 'gpt', '大模型', 'llm', '深度学习', '机器学习',
        '神经网络', 'openai', '文心', '通义', 'kimi', '豆包', 'deepseek', 'gemini',
        'copilot', 'midjourney', 'diffusion', 'aigc', 'agent', '智能体', '生成式',
        'prompt', '提示词', '开源模型', 'sora', 'runway', 'pika', 'cursor', 'claude',
        '数字人', 'ai工具', 'ai应用', 'ai助手', 'ai创作', 'ai学习', 'ai教程',
        'langchain', 'rag', 'embedding', '向量', '微调', '部署', '推理', 'token',
        'python', '编程', '开发', '算法', '算力', 'gpu', '科技', '技术', '教程',
        '自动化', '机器人', '人工智能', '智能化', 'AI'
    ]
    text = (title + author).lower()
    return any(kw.lower() in text for kw in ai_kws)

def fetch_douyin_hot_api():
    """从抖音热榜API抓取"""
    url = "https://www.douyin.com/aweme/v1/web/hot/search/list/"
    params = {
        "device_platform": "webapp",
        "aid": "6383",
        "channel": "channel_pc_web",
        "count": "50",
        "offset": "0",
    }
    headers = {
        "User-Agent": PC_UA,
        "Referer": "https://www.douyin.com/",
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        if data.get("status_code") == 0:
            return data.get("data", {}).get("trending_list", [])
    except Exception as e:
        print(f"API error: {e}")
    return []

def format_views(v):
    try:
        v = int(v)
    except:
        v = 0
    if v >= 100000000:
        return f"{v/100000000:.1f}亿"
    elif v >= 10000:
        return f"{v/10000:.1f}万"
    return str(v)

def main():
    NOW = datetime.now().strftime("%Y-%m-%d")
    douyin_path = os.path.join(DATA_DIR, "douyin.md")
    existing_count = count_items(douyin_path)
    
    # 读取已有标题
    seen_titles = set()
    if os.path.exists(douyin_path):
        with open(douyin_path, "r", encoding="utf-8") as f:
            for line in f:
                m = re.search(r'- 标题: (.+)', line)
                if m:
                    seen_titles.add(m.group(1).strip())
    
    print(f"Current: {existing_count} items")
    
    # 抓取热榜
    items = fetch_douyin_hot_api()
    print(f"Fetched {len(items)} hot items")
    
    # 过滤AI相关
    ai_items = []
    for item in items:
        word = item.get("word", "")
        if is_ai_related(word):
            hot_val = item.get("hot_value", 0)
            videos = item.get("video_count", 0)
            ai_items.append({
                "title": word,
                "author": "抖音热榜",
                "likes": format_views(hot_val),
                "topics": f"#AI #人工智能 #热榜",
                "duration": f"{videos}个相关视频",
                "comment": "未知",
                "collect": "未知",
                "share": "未知",
                "url": f"https://www.douyin.com/search/{word}",
                "keyword": "抖音热榜"
            })
            print(f"  + [AI] {word} (热度: {format_views(hot_val)})")
    
    print(f"AI-related hot items: {len(ai_items)}")
    
    # 再尝试从热搜榜抓更多
    # 用不同的endpoint
    try:
        url2 = "https://www.douyin.com/aweme/v1/web/hot/search/list/"
        params2 = dict(params)
        params2["offset"] = "50"
        resp2 = requests.get(url2, params=params2, headers=headers, timeout=10)
        data2 = resp2.json()
        if data2.get("status_code") == 0:
            more = data2.get("data", {}).get("trending_list", [])
            for item in more:
                word = item.get("word", "")
                if is_ai_related(word) and word not in [x["title"] for x in ai_items]:
                    hot_val = item.get("hot_value", 0)
                    videos = item.get("video_count", 0)
                    ai_items.append({
                        "title": word,
                        "author": "抖音热榜",
                        "likes": format_views(hot_val),
                        "topics": f"#AI #人工智能 #热榜",
                        "duration": f"{videos}个相关视频",
                        "comment": "未知",
                        "collect": "未知",
                        "share": "未知",
                        "url": f"https://www.douyin.com/search/{word}",
                        "keyword": "抖音热榜"
                    })
    except Exception as e:
        print(f"More API error: {e}")
    
    print(f"Total AI items: {len(ai_items)}")
    
    # 格式化
    new_entries = []
    for i, item in enumerate(ai_items, 1):
        if item["title"] in seen_titles:
            continue
        seen_titles.add(item["title"])
        idx = existing_count + len(new_entries) + 1
        entry = f"""
### 第{idx}条
- 标题: {item['title']}
- 作者: @{item['author']}
- 点赞: {item['likes']}
- 评论: {item['comment']}
- 收藏: {item['collect']}
- 转发: {item['share']}
- 时长: {item['duration']}
- 话题: {item['topics']}
- 链接: {item['url']}
- 内容总结: 抖音热榜话题：{item['title']}，热度{item['likes']}
"""
        new_entries.append(entry)
    
    if new_entries:
        content = "\n".join(new_entries)
        header = f"\n\n---\n\n## 抖音 AI内容追加批次 ({NOW} 13:00) - 新增 {len(new_entries)} 条\n\n"
        save_append(douyin_path, header + content)
        print(f"\n[DONE] Douyin: appended {len(new_entries)} items, total now {existing_count + len(new_entries)}")
    else:
        print("\n[WARN] No new items")

if __name__ == "__main__":
    main()
