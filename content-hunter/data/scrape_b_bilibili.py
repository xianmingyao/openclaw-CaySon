# -*- coding: utf-8 -*-
"""
内容捕手 - B站AI技术热门内容追加抓取（100条）
"""
import requests
import json
import time
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.bilibili.com',
    'Origin': 'https://www.bilibili.com'
})

def search_bilibili(keyword, page=1, pagesize=20):
    url = 'https://api.bilibili.com/x/web-interface/search/type'
    params = {
        'search_type': 'video',
        'keyword': keyword,
        'page': page,
        'page_size': pagesize,
        'order': 'totalrank',
        'duration': 0,
    }
    try:
        resp = session.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('code') == 0:
                return data.get('data', {}).get('result', [])
            print('  API error: code=%s' % data.get('code', 'unknown'))
    except Exception as e:
        print('  Exception: %s' % e)
    return []

def get_video_detail(bvid):
    try:
        url = 'https://api.bilibili.com/x/web-interface/view'
        params = {'bvid': bvid}
        resp = session.get(url, params=params, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('code') == 0:
                d = data.get('data', {})
                stat = d.get('stat', {})
                owner = d.get('owner', {})
                tags_data = d.get('tags', []) or []
                return {
                    'title': d.get('title', ''),
                    'author': owner.get('name', ''),
                    'bvid': bvid,
                    'aid': d.get('aid', ''),
                    'view': stat.get('view', 0),
                    'like': stat.get('like', 0),
                    'coin': stat.get('coin', 0),
                    'favorite': stat.get('favorite', 0),
                    'danmaku': stat.get('danmaku', 0),
                    'duration': d.get('duration', 0),
                    'desc': d.get('desc', ''),
                    'tags': [t.get('tag_name', '') for t in tags_data[:10]],
                    'tname': d.get('tname', ''),
                    'url': 'https://www.bilibili.com/video/%s' % bvid
                }
    except Exception as e:
        print('  Detail error %s: %s' % (bvid, e))
    return None

def format_duration(seconds):
    if not seconds:
        return '未知'
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return '%d:%02d:%02d' % (h, m, s)
    return '%d:%02d' % (m, s)

def format_number(n):
    if n >= 100000000:
        return '%.1f亿' % (n / 100000000)
    elif n >= 10000:
        return '%.1f万' % (n / 10000)
    return str(n)

# 读取现有bilibili.md条数
existing_count = 0
try:
    with open('E:/workspace/content-hunter/data/bilibili.md', 'r', encoding='utf-8') as f:
        content = f.read()
    matches = re.findall(r'第(\d+)条', content)
    if matches:
        existing_count = max(int(x) for x in matches)
    print('现有B站数据: %d 条' % existing_count)
except Exception as e:
    print('读取现有文件失败: %s' % e)
    existing_count = 0

search_terms = [
    'AI人工智能技术', 'ChatGPT使用技巧', 'GPT-4教程', '深度学习实战',
    '机器学习教程', '神经网络原理', '大模型LLM', 'AI绘画教程',
    'AI工具使用', 'AIGC内容创作', 'Copilot教程', 'AI编程工具',
    'ChatGPT提示词', 'AI Agent应用', '人工智能入门',
    'Claude教程', 'Gemini AI', 'Stable Diffusion', 'Midjourney技巧',
    'AI视频生成', 'Sora教程', '大模型微调', 'RAG技术',
    'AI克隆人', '数字人制作', 'AI配音', '国产大模型',
    'Kimi教程', '通义千问', '文心一言', '智谱AI',
]

print('=== B站AI技术内容追加抓取 ===')
print('目标: 追加100条新内容\n')

all_videos = []
seen_bvids = set()

for term in search_terms:
    if len(all_videos) >= 120:
        break
    print('[%s] 搜索: %s' % (time.strftime('%H:%M:%S'), term))
    for page in range(1, 4):
        if len(all_videos) >= 120:
            break
        results = search_bilibili(term, page=page)
        if not results:
            break
        for r in results:
            if not isinstance(r, dict):
                continue
            bvid = r.get('bvid', '')
            if not bvid or bvid in seen_bvids:
                continue
            seen_bvids.add(bvid)
            title = re.sub(r'<[^>]+>', '', r.get('title', ''))
            all_videos.append({
                'bvid': bvid,
                'title': title,
                'author': r.get('author', ''),
                'aid': r.get('aid', ''),
                'duration': r.get('duration', ''),
                'play': r.get('play', 0),
                'like': r.get('like', 0),
            })
            if len(all_videos) >= 120:
                break
        time.sleep(0.5)

print('\n搜索到 %d 个候选视频，获取详情...' % len(all_videos))

detailed_videos = []
for i, v in enumerate(all_videos[:100]):
    print('[%d/100] %s' % (i+1, v['title'][:40]))
    detail = get_video_detail(v['bvid'])
    if detail:
        detailed_videos.append(detail)
    time.sleep(0.3)

print('')
print('=== 获取到 %d 个详细视频，追加到bilibili.md ===' % len(detailed_videos))

start_num = existing_count + 1
md_lines = []

for i, v in enumerate(detailed_videos):
    num = start_num + i
    tags_str = ' '.join(['#%s' % t for t in v.get('tags', []) if t])
    desc = v.get('desc', '')[:200]
    summary = desc if desc else '暂无描述'

    md_lines.append('')
    md_lines.append('### 第%d条' % num)
    md_lines.append('- 标题 / Title: %s' % v['title'])
    md_lines.append('- UP主 / UP: %s' % v['author'])
    md_lines.append('- 播放 / Views: %s' % format_number(v['view']))
    md_lines.append('- 弹幕 / Danmaku: %s' % format_number(v['danmaku']))
    md_lines.append('- 点赞 / Likes: %s' % format_number(v['like']))
    md_lines.append('- 投币 / Coins: %s' % format_number(v['coin']))
    md_lines.append('- 收藏 / Favs: %s' % format_number(v['favorite']))
    md_lines.append('- 时长 / Duration: %s' % format_duration(v['duration']))
    md_lines.append('- 话题 / Tags: %s' % (tags_str if tags_str else '无'))
    if len(summary) > 100:
        md_lines.append('- 内容总结 / Summary: %s...' % summary[:97])
    else:
        md_lines.append('- 内容总结 / Summary: %s' % summary)
    md_lines.append('- 链接 / URL: %s' % v['url'])

with open('E:/workspace/content-hunter/data/bilibili.md', 'a', encoding='utf-8') as f:
    f.write('\n'.join(md_lines))

print('\n追加完成！')
print('新增 %d 条，现有总计约 %d 条' % (len(detailed_videos), existing_count + len(detailed_videos)))
