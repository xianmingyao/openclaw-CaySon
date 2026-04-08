# -*- coding: utf-8 -*-
"""
内容捕手 - B站AI技术热门内容抓取脚本
使用B站官方API，无需登录
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
    """搜索B站视频"""
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
    """获取视频详情"""
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
    """格式化时长"""
    if not seconds:
        return '未知'
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return '%d:%02d:%02d' % (h, m, s)
    return '%d:%02d' % (m, s)

def format_number(n):
    """格式化数字"""
    if n >= 100000000:
        return '%.1f亿' % (n / 100000000)
    elif n >= 10000:
        return '%.1f万' % (n / 10000)
    return str(n)

# 搜索关键词列表 - AI技术相关
search_terms = [
    'AI人工智能技术',
    'ChatGPT使用技巧',
    'GPT-4教程',
    '深度学习实战',
    '机器学习教程',
    '神经网络原理',
    '大模型LLM',
    'AI绘画教程',
    'AI工具使用',
    'AIGC内容创作',
    'Copilot教程',
    'AI编程工具',
    'ChatGPT提示词',
    'AI Agent应用',
    '人工智能入门',
]

print('=== B站AI技术内容抓取开始 ===')
print('目标: 100条AI技术热门内容')
print('')

all_videos = []
seen_bvids = set()

for term in search_terms:
    print('[%s] 搜索: %s' % (time.strftime('%H:%M:%S'), term))
    for page in range(1, 4):  # 每词3页
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
            
            # 清理HTML标签
            title = re.sub(r'<[^>]+>', '', r.get('title', ''))
            
            video_info = {
                'bvid': bvid,
                'title': title,
                'author': r.get('author', ''),
                'aid': r.get('aid', ''),
                'duration': r.get('duration', ''),
                'pubdate': r.get('pubdate', ''),
                'play': r.get('play', 0),
                'like': r.get('like', 0),
            }
            all_videos.append(video_info)
            
            if len(all_videos) >= 120:  # 多抓一些，容错
                break
        if len(all_videos) >= 120:
            break
        time.sleep(0.5)
    if len(all_videos) >= 120:
        break
    time.sleep(1)

print('')
print('=== 搜索到 %d 个视频，开始获取详情 ===' % len(all_videos))

# 获取详细数据
detailed_videos = []
for i, v in enumerate(all_videos[:100]):
    print('[%d/%d] %s' % (i+1, min(100, len(all_videos)), v['title'][:40]))
    detail = get_video_detail(v['bvid'])
    if detail:
        detailed_videos.append(detail)
    time.sleep(0.3)

print('')
print('=== 获取到 %d 个详细视频 ===' % len(detailed_videos))

# 保存JSON
output_json = 'E:/workspace/content-hunter/data/bilibili_ai_100.json'
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(detailed_videos, f, ensure_ascii=False, indent=2)
print('JSON已保存: %s' % output_json)

# 转换为Markdown格式并追加
existing_count = 0
try:
    with open('E:/workspace/content-hunter/data/bilibili.md', 'r', encoding='utf-8') as f:
        content = f.read()
    matches = re.findall(r'第(\d+)条', content)
    if matches:
        existing_count = max(int(x) for x in matches)
    print('现有B站数据: %d 条' % existing_count)
except:
    existing_count = 0

md_lines = []
start_num = existing_count + 1

for i, v in enumerate(detailed_videos):
    num = start_num + i
    tags_str = ' '.join(['#%s' % t for t in v.get('tags', []) if t])
    
    # 生成内容总结
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
    md_lines.append('- 内容总结 / Summary: %s...' % summary if len(summary) > 100 else '- 内容总结 / Summary: %s' % summary)
    md_lines.append('- 链接 / URL: %s' % v['url'])

# 追加到文件
output_md = 'E:/workspace/content-hunter/data/bilibili.md'
with open(output_md, 'a', encoding='utf-8') as f:
    f.write('\n'.join(md_lines))
print('')
print('=== 追加 %d 条到 %s ===' % (len(detailed_videos), output_md))
print('Done!')
