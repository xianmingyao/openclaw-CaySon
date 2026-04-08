# -*- coding: utf-8 -*-
import requests
import json
import re
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Referer': 'https://so.toutiao.com/',
}

keywords = ['AI人工智能 教程', 'ChatGPT 使用', '大模型 技术', 'AIGC 工具', 'AI绘图 教程']
all_videos = []
seen = set()

for kw in keywords:
    encoded_kw = kw.replace(' ', '%20')
    url = f'https://so.toutiao.com/search?keyword={encoded_kw}&pd=video'
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f'关键词:{kw} 状态:{r.status_code} 长度:{len(r.text)}')
        if r.status_code == 200:
            # 提取视频信息
            ids = re.findall(r'douyin\.com/video/(\d+)', r.text)
            titles = re.findall(r'title":*"([^"]+)"', r.text)
            authors = re.findall(r'screen_name":*"([^"]+)"', r.text)
            diggs = re.findall(r'(\d+)\s*赞', r.text)
            print(f'  IDs:{len(ids)} titles:{len(titles)} authors:{len(authors)}')
            for i, vid in enumerate(ids[:20]):
                if vid not in seen:
                    seen.add(vid)
                    all_videos.append({
                        'id': vid,
                        'title': titles[i] if i < len(titles) else '',
                        'author': authors[i] if i < len(authors) else '',
                        'digg': diggs[i] if i < len(diggs) else '0',
                        'url': f'https://www.douyin.com/video/{vid}'
                    })
    except Exception as e:
        print(f'失败: {e}')
    time.sleep(1)

print(f'\n获取到 {len(all_videos)} 条')
with open('E:/workspace/content-hunter/data/douyin_raw.json','w',encoding='utf-8') as f:
    json.dump(all_videos, f, ensure_ascii=False, indent=2)
