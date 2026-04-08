# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime

# 读取原始数据
with open('E:/workspace/content-hunter/data/bilibili_raw.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f'共有 {len(items)} 条B站数据')

# 格式化播放量
def format_num(s):
    s = str(s)
    if '万' in s:
        return s
    try:
        n = int(s)
        if n >= 10000:
            return f'{n/10000:.1f}万'
        return str(n)
    except:
        return s

# 格式化标题（去除em标签）
def clean_title(title):
    import re
    title = re.sub(r'<em class="keyword">', '', title)
    title = re.sub(r'</em>', '', title)
    return title

# 追加写入md
md_path = 'E:/workspace/content-hunter/data/bilibili.md'
today = datetime.now().strftime('%Y-%m-%d %H:%M')

file_exists = os.path.exists(md_path)
with open(md_path, 'a', encoding='utf-8') as f:
    if not file_exists:
        f.write('# B站AI技术热门内容\n\n')
    
    f.write(f'## 抓取时间: {today} (本次共 {len(items[:100])} 条)\n\n')
    
    for i, item in enumerate(items[:100], 1):
        title = clean_title(item.get('title', ''))
        author = item.get('author', '')
        play = item.get('play', '0')
        video_review = item.get('video_review', '0')
        favorites = item.get('favorites', '0')
        like = item.get('like', '0')
        duration = item.get('duration', '00:00')
        bvid = item.get('bvid', '')
        description = item.get('description', '')
        arcurl = item.get('arcurl', f'https://www.bilibili.com/video/{bvid}')
        
        f.write(f'### 第{i}条\n')
        f.write(f'- 标题: {title}\n')
        f.write(f'- UP主: {author}\n')
        f.write(f'- 播放: {format_num(play)}\n')
        f.write(f'- 弹幕: {format_num(video_review)}\n')
        f.write(f'- 点赞: {format_num(like)}\n')
        f.write(f'- 收藏: {format_num(favorites)}\n')
        f.write(f'- 时长: {duration}\n')
        f.write(f'- BV号: {bvid}\n')
        f.write(f'- 链接: {arcurl}\n')
        desc_text = description[:200] if description else '暂无简介'
        f.write(f'- 内容总结: {desc_text}\n\n')

print(f'已追加写入 {min(len(items), 100)} 条到 {md_path}')
