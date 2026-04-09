#!/usr/bin/env python3
"""
B站AI内容抓取 - 强制重写版
"""
import requests
import json
import time
import re
import os

DATA_DIR = r"E:\workspace\content-hunter\data"
OUTPUT_FILE = os.path.join(DATA_DIR, "bilibili.md")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com',
    'Accept': 'application/json, text/plain, */*',
}

BILIBILI_AI_KEYWORDS = [
    'AI人工智能', 'ChatGPT', '大模型', '机器学习', '深度学习',
    'AIGC', 'LLM', 'GPT', 'AI工具', 'AI应用', 'AI绘画',
    'AI视频', 'Claude', 'Gemini', 'Sora', 'OpenAI', 'AI助手',
    '文心一言', '通义千问', 'KIMI', '豆包', 'AI创作', 'AI编程',
    'AI Agent', 'RAG', 'LangChain', 'AI开发', 'DeepSeek'
]

def is_ai_related(title, description=''):
    text = f"{title} {description}"
    ai_keywords = ['ai', '人工智能', 'chatgpt', '大模型', '机器学习', '深度学习',
                   'aigc', 'llm', 'gpt', '文心一言', '通义千问', 'kimi', '豆包',
                   'claude', 'gemini', 'sora', 'openai', 'ai绘画', 'ai视频',
                   'ai工具', 'ai应用', 'ai助手', 'ai创作', 'ai编程', 'ai agent',
                   'rag', 'langchain', 'ai开发', 'ai技术', 'ai学习', 'ai教程',
                   'stable diffusion', 'midjourney', 'grok', 'copilot', 'cursor',
                   'o1', 'o3', 'gpt-4', '视频生成', 'ai音乐', 'ai配音',
                   'deepseek']
    text_lower = text.lower()
    for kw in ai_keywords:
        if kw.lower() in text_lower:
            return True, kw
    return False, None

def scrape_bilibili(keyword, page=1):
    url = 'https://api.bilibili.com/x/web-interface/search/type'
    params = {
        'search_type': 'video',
        'keyword': keyword,
        'page': page,
        'order': 'totalrank',
    }
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = resp.json()
        if data['code'] == 0:
            return data['data']['result']
        return []
    except Exception as e:
        print(f"  Error: {e}")
        return []

def format_item(item, seq):
    title = item.get('title', '').replace('<em class="keyword">', '').replace('</em>', '')
    author = item.get('author', '未知UP')
    views = item.get('play', item.get('view', 0))
    danmaku = item.get('video_review', item.get('danmaku', 0))
    likes = item.get('like', 0)
    coins = item.get('coin', 0)
    favs = item.get('favorite', 0)
    duration = item.get('duration', '未知')
    bvid = item.get('bvid', '')
    description = item.get('description', '')
    
    if description:
        summary = description[:200] if len(description) > 200 else description
    else:
        summary = f"B站AI技术视频，UP主{author}，播放{views}"
    
    return f"""### 第{seq}条
- 标题: {title}
- UP主: {author}
- 播放: {views}
- 弹幕: {danmaku}
- 点赞: {likes}
- 投币: {coins}
- 收藏: {favs}
- 时长: {duration}
- BV号: {bvid}
- 内容总结: {summary}
"""

def main():
    print("B站AI内容抓取开始")
    all_items = []
    seen_bvids = set()
    
    for kw in BILIBILI_AI_KEYWORDS:
        if len(all_items) >= 150:
            break
        print(f"  搜索: {kw}")
        for page in range(1, 4):
            items = scrape_bilibili(kw, page=page)
            if not items:
                break
            for item in items:
                bvid = item.get('bvid', '')
                if bvid and bvid not in seen_bvids:
                    seen_bvids.add(bvid)
                    title = item.get('title', '')
                    is_ai, matched = is_ai_related(title)
                    if is_ai:
                        all_items.append(item)
                        if len(all_items) >= 150:
                            break
            if len(all_items) >= 150:
                break
            time.sleep(0.3)
        time.sleep(0.5)
    
    print(f"找到 {len(all_items)} 条AI内容")
    
    # 取前100条
    items_100 = all_items[:100]
    
    # 写文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("# B站AI技术热门内容\n\n")
        f.write(f"抓取时间: 2026-04-09\n\n")
        for i, item in enumerate(items_100):
            f.write(format_item(item, i + 1))
            f.write('\n')
    
    print(f"写入 {len(items_100)} 条到 {OUTPUT_FILE}")

if __name__ == '__main__':
    main()
