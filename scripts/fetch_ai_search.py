# -*- coding: utf-8 -*-
"""使用B站搜索API抓取AI技术内容"""
import urllib.request
import json
import sys
import re
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

DATA_DIR = r'E:\workspace\content-hunter-data\data'

AI_QUERIES = [
    'AI技术', '人工智能', '大模型', 'LLM', 'GPT', 'ChatGPT',
    'AI工具', 'AI应用', '深度学习', '机器学习', '神经网络',
    'AI创业', 'AI投资', 'AI公司', 'AI助手', 'AI视频',
    '文心一言', 'Kimi', 'ChatGLM', 'Qwen', 'DeepSeek',
    'OpenAI', 'Anthropic', 'Claude', 'Gemini', 'Sora'
]

def search_bilibili(query, page=1, duration=0, order='totalrank'):
    """B站搜索API"""
    search_url = f'https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={urllib.parse.quote(query)}&page={page}&duration={duration}&order={order}'
    req = urllib.request.Request(search_url, headers={
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://www.bilibili.com'
    })
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    return data['data']['result']

def format_md_item(item, idx):
    """格式化单个视频条目"""
    title = re.sub(r'<[^>]+>', '', item.get('title', ''))  # 去除HTML标签
    author = item.get('author', '未知')
    bvid = item.get('bvid', '')
    href = f'https://www.bilibili.com/video/{bvid}'
    play = item.get('play', 0)
    like = item.get('like', 0)
    pubdate = item.get('pubdate', 0)
    duration = item.get('duration', '')
    
    return f"""### 第{idx}条
- 标题: {title}
- UP主: @{author}
- 链接: {href}
- 播放: {play}
- 点赞: {like}
- 时长: {duration}
"""

def main():
    all_items = []
    seen_bvids = set()
    
    print("开始搜索B站AI技术内容...")
    
    for query in AI_QUERIES:
        print(f"  搜索: {query}...")
        try:
            results = search_bilibili(query, page=1)
            count = 0
            for item in results[:10]:  # 每词取前10条
                bvid = item.get('bvid', '')
                if bvid and bvid not in seen_bvids:
                    seen_bvids.add(bvid)
                    all_items.append(item)
                    count += 1
            print(f"    -> 新增 {count} 条 (累计 {len(seen_bvids)})")
        except Exception as e:
            print(f"    -> 错误: {e}")
    
    print(f"\n总计获取 {len(all_items)} 个不重复AI相关视频")
    
    if not all_items:
        print("未获取到数据，请检查网络或B站API限制")
        return
    
    # 生成Markdown
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    md_lines = [
        "",
        "---",
        f"**追加来源**: B站搜索API（多关键词）",
        f"**追加时间**: {now}",
        f"**本次新增**: {len(all_items)} 条",
        "",
    ]
    
    for i, item in enumerate(all_items[:100], 1):
        md_lines.append(format_md_item(item, i))
    
    # 读取现有数量
    bilibili_file = f'{DATA_DIR}\\bilibili.md'
    existing = 0
    if os.path.exists(bilibili_file):
        with open(bilibili_file, 'r', encoding='utf-8') as f:
            content = f.read()
        existing = len(re.findall(r'### 第\d+条', content))
    
    print(f"现有条目: {existing}, 本次新增: {len(all_items[:100])}")
    
    # 追加写入
    with open(bilibili_file, 'a', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
    
    print(f"✅ 已追加到: {bilibili_file}")

import urllib.parse
import os
import re

if __name__ == '__main__':
    main()
