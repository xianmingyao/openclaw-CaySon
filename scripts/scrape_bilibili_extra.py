#!/usr/bin/env python3
"""Additional Bilibili scrape for appending"""
import requests, re, time, os, sys
from datetime import datetime

os.environ['PYTHONIOENCODING'] = 'utf-8'

def clean_title(t):
    return re.sub(r'<[^>]+>', '', t)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://search.bilibili.com',
}

def scrape(kw, pages=2):
    results = []
    for page in range(1, pages+1):
        url = 'https://api.bilibili.com/x/web-interface/search/type'
        params = dict(search_type='video', keyword=kw, order='totalrank', page=page, page_size=30)
        try:
            r = requests.get(url, params=params, headers=headers, timeout=15)
            if r.status_code == 200:
                items = r.json().get('data', {}).get('result', [])
                for item in items:
                    results.append({
                        'title': clean_title(item.get('title', '')),
                        'author': item.get('author', ''),
                        'play': item.get('play', 0),
                        'likes': item.get('like', 0),
                        'bvid': item.get('bvid', ''),
                        'description': item.get('description', ''),
                        'danmaku': item.get('video_review', 0),
                        'coins': item.get('coin', 0),
                        'favorites': item.get('favorites', 0),
                        'tags': item.get('tag', [])[:5],
                    })
                sys.stderr.write(f'  [{kw}] p{page}: {len(items)} items\n')
        except Exception as e:
            sys.stderr.write(f'  Error: {e}\n')
        time.sleep(10)
    return results

# Read existing BVids
data_dir = os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace', 'content-hunter', 'data')
existing_path = os.path.join(data_dir, 'bilibili.md')
bvids = set(re.findall(r'BV[a-zA-Z0-9]{10}', open(existing_path, encoding='utf-8').read()))
sys.stderr.write(f'Existing BVids: {len(bvids)}\n')

# Fresh keywords targeting AI tech
kws = [
    'AI绘画 stable diffusion 教程',
    'Sora AI视频',
    'ChatGPT o4 使用技巧',
    'Claude AI 使用',
    'Grok AI 使用',
    'AI Agent 智能体',
    '大模型 微调训练',
    'AI编程 Copilot',
    'AI PPT 制作',
    'AI 写作技巧',
]

all_new = []
for kw in kws:
    items = scrape(kw, pages=2)
    new = [i for i in items if i['bvid'] not in bvids and i['bvid']]
    sys.stderr.write(f'  New: {len(new)}/{len(items)}\n')
    all_new.extend(new)
    time.sleep(8)

sys.stderr.write(f'Total new: {len(all_new)}\n')

if all_new:
    lines = []
    lines.append(f'\n## 追加数据 ({datetime.now().strftime("%Y-%m-%d %H:%M")})\n\n')
    for i, item in enumerate(all_new, 1):
        lines.append(f'### 追加{i}\n')
        lines.append(f'- 标题: {item["title"]}\n')
        lines.append(f'- UP主: @{item["author"]}\n')
        lines.append(f'- 播放: {item["play"]}\n')
        lines.append(f'- 点赞: {item["likes"]}\n')
        lines.append(f'- 弹幕: {item["danmaku"]}\n')
        lines.append(f'- 投币: {item["coins"]}\n')
        lines.append(f'- 收藏: {item["favorites"]}\n')
        if item.get('tags'):
            lines.append(f'- 话题: {" ".join(["#"+t for t in item["tags"]])}\n')
        lines.append(f'- 内容总结: {item["description"][:200]}\n\n')
    
    with open(existing_path, 'a', encoding='utf-8') as f:
        f.write(''.join(lines))
    
    sys.stderr.write(f'Appended {len(all_new)} items\n')

print('DONE')
