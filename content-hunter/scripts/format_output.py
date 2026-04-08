# -*- coding: utf-8 -*-
"""
将抓取的数据格式化为标准md文件（追加模式）
"""
import json
import os
import sys
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

today = datetime.now().strftime('%Y-%m-%d %H:%M')

# ====== 格式化B站数据 ======
print("=== 格式化B站数据 ===")
with open('E:/workspace/content-hunter/data/bilibili_raw.json', 'r', encoding='utf-8') as f:
    bilibili_items = json.load(f)

import re
def clean_title(title):
    title = re.sub(r'<em class="keyword">', '', title)
    title = re.sub(r'</em>', '', title)
    return title

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

bilibili_md = 'E:/workspace/content-hunter/data/bilibili.md'
file_exists = os.path.exists(bilibili_md)

with open(bilibili_md, 'a', encoding='utf-8') as f:
    if not file_exists:
        f.write('# B站AI技术热门内容\n\n')
    
    f.write(f'## 抓取时间: {today} (本次共 {len(bilibili_items[:100])} 条)\n\n')
    
    for i, item in enumerate(bilibili_items[:100], 1):
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

print(f"[OK] B站: 写入 {len(bilibili_items[:100])} 条到 {bilibili_md}")

# ====== 格式化抖音数据 ======
print("\n=== 格式化抖音数据 ===")
with open('E:/workspace/content-hunter/data/douyin_raw.json', 'r', encoding='utf-8') as f:
    douyin_items = json.load(f)

douyin_md = 'E:/workspace/content-hunter/data/douyin.md'
file_exists = os.path.exists(douyin_md)

# 尝试读取抖音热榜API的原始数据以获取更多信息
# 由于API数据有限，我们用热榜词作为标题
with open(douyin_md, 'a', encoding='utf-8') as f:
    if not file_exists:
        f.write('# 抖音AI技术热门内容\n\n')
    
    f.write(f'## 抓取时间: {today} (本次共 {len(douyin_items)} 条)\n')
    f.write(f'## 数据说明: 数据来源为抖音热榜API，部分内容可能缺少完整视频信息\n\n')
    
    for i, item in enumerate(douyin_items, 1):
        title = item.get('title', f'AI话题 #{i}')
        author = item.get('author', '未知')
        digg = item.get('digg', '0')
        url = item.get('url', '')
        vid = item.get('id', '')
        
        # 格式化热度值
        try:
            hot = int(digg)
            if hot >= 100000000:
                hot_str = f'{hot/100000000:.1f}亿'
            elif hot >= 10000:
                hot_str = f'{hot/10000:.1f}万'
            else:
                hot_str = str(hot)
        except:
            hot_str = digg
        
        f.write(f'### 第{i}条\n')
        f.write(f'- 标题: {title}\n')
        f.write(f'- 作者: @{author}\n')
        f.write(f'- 热度: {hot_str}\n')
        if url:
            f.write(f'- 链接: {url}\n')
        if vid and len(str(vid)) == 19:
            f.write(f'- 视频ID: {vid}\n')
        f.write(f'- 内容总结: 抖音热榜话题内容，详细视频信息请访问链接查看\n\n')

print(f"[OK] 抖音: 写入 {len(douyin_items)} 条到 {douyin_md}")

# ====== 生成汇总 =====
print("\n=== 汇总 ===")
print(f"B站: {len(bilibili_items[:100])} 条")
print(f"抖音: {len(douyin_items)} 条")
print(f"总计: {len(bilibili_items[:100]) + len(douyin_items)} 条")
