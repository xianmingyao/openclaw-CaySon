#!/usr/bin/env python3
"""
AI技术内容专项抓取器
只抓取标题/话题中包含AI相关关键词的内容
"""
import json
import re
import os
from datetime import datetime

DATA_DIR = r"E:\workspace\content-hunter\data"
BILIBILI_KEYWORDS = ["AI", "人工智能", "ChatGPT", "大模型", "机器学习", "深度学习", "AIGC", "LLM", "GPT", "文心一言", "通义千问", "豆包", "KIMI", "AI绘画", "AI视频", "AI生成", "AI助手", "AI工具", "Claude", "Gemini", "Grok", "Sora", "OpenAI", "AI技术", "AI应用"]
DOUYIN_KEYWORDS = ["AI", "人工智能", "ChatGPT", "大模型", "机器学习", "深度学习", "AIGC", "LLM", "GPT", "文心一言", "通义千问", "豆包", "KIMI", "AI绘画", "AI视频", "AI生成", "AI助手", "AI工具", "Claude", "Gemini", "Grok", "Sora", "AI技术", "AI应用"]

def matches_ai_keywords(text, keywords):
    """检查文本是否匹配AI关键词"""
    if not text:
        return False
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True
    return False

def get_current_count(filepath):
    """获取当前文件中的条目数"""
    if not os.path.exists(filepath):
        return 0
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    matches = re.findall(r'(?m)^### 第(\d+)条', content)
    if matches:
        return max(int(m) for m in matches)
    return 0

def format_douyin_item(item, seq):
    """格式化抖音条目"""
    title = item.get('title', '')
    author = item.get('author', item.get('nickname', '@未知'))
    likes = item.get('digg_count', item.get('collect_count', '未知'))
    tags = item.get('topics', [])
    tag_str = ' '.join([f'#{t}' for t in tags]) if tags else ''
    desc = item.get('desc', item.get('description', ''))
    
    # 生成内容总结
    if desc:
        summary = desc[:200] if len(desc) > 200 else desc
    else:
        summary = f"抖音AI相关视频，作者{author}，获赞{likes}"
    
    return f"""### 第{seq}条
- 标题: {title}
- 作者: @{author}
- 点赞: {likes}
- 话题: {tag_str}
- 内容总结: {summary}
"""

def format_bilibili_item(item, seq):
    """格式化B站条目"""
    title = item.get('title', '')
    author = item.get('author', item.get('owner', {}).get('name', '未知UP'))
    views = item.get('view', item.get('views', '未知'))
    danmaku = item.get('danmaku', item.get('pts', 0))
    likes = item.get('like', item.get('likes', '未知'))
    coins = item.get('coin', item.get('coins', '未知'))
    favs = item.get('favorite', item.get('favs', '未知'))
    duration = item.get('duration', '未知')
    bvid = item.get('bvid', '')
    desc = item.get('description', item.get('desc', ''))
    
    has_subtitle = "有" if danmaku and int(danmaku) > 0 else "无"
    
    # 生成内容总结
    if desc:
        summary = desc[:200] if len(desc) > 200 else desc
    else:
        summary = f"B站AI相关视频，UP主{author}，播放{views}"
    
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

def append_items(filepath, items, format_func):
    """追加条目到文件"""
    current_count = get_current_count(filepath)
    start_seq = current_count + 1
    
    with open(filepath, 'a', encoding='utf-8') as f:
        for i, item in enumerate(items):
            seq = start_seq + i
            f.write(format_func(item, seq))
            f.write('\n')
    
    new_count = len(items)
    return new_count

print("AI内容抓取辅助脚本已就绪")
print(f"目标目录: {DATA_DIR}")
print(f"B站AI关键词数: {len(BILIBILI_KEYWORDS)}")
print(f"抖音AI关键词数: {len(DOUYIN_KEYWORDS)}")
