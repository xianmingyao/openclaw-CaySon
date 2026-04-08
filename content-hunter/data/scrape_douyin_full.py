# -*- coding: utf-8 -*-
"""
内容捕手 - 抖音AI技术热门内容完整抓取
"""
import requests
import json
import time
import re
import sys
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'https://www.douyin.com/',
    'Cookie': 'ttwid=1; s_v_web_id=verify_xplaceholder',
})

def get_douyin_hot_words():
    """获取抖音热搜词"""
    url = 'https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383&channel=channel_pc_web&detail_list=1'
    try:
        resp = session.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            word_list = data.get('data', {}).get('word_list', [])
            print('Hot words: %d' % len(word_list))
            return [{'word': w.get('word', ''), 'heat': w.get('heat', 0)} for w in word_list]
    except Exception as e:
        print('Hot words error: %s' % e)
    return []

def search_douyin_video(keyword, offset=0, count=20):
    """搜索抖音视频"""
    # 抖音搜索API - 需要X-Bogus签名，这个简单版本可能不行
    # 尝试使用网页版搜索参数
    url = 'https://www.douyin.com/aweme/v1/web/search/item/'
    params = {
        'keyword': keyword,
        'offset': offset,
        'count': count,
        'device_platform': 'webapp',
        'aid': '6383',
        'channel': 'channel_pc_web',
    }
    try:
        resp = session.get(url, params=params, timeout=15)
        if resp.status_code == 200 and len(resp.content) > 500:
            try:
                data = resp.json()
                return data
            except:
                pass
    except Exception as e:
        print('Search error: %s' % e)
    return None

def get_video_detail_with_yt_dlp(url):
    """使用yt-dlp获取视频详情"""
    try:
        result = subprocess.run([
            'yt-dlp', '--dump-json', '--no-download', '--', url
        ], capture_output=True, text=True, timeout=30)
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
    except Exception as e:
        pass
    return None

def format_number(n):
    """格式化数字"""
    if not n:
        return '未知'
    if isinstance(n, str):
        n = int(n.replace('万', '').replace(',', '')) if n else 0
    if n >= 100000000:
        return '%.1f亿' % (n / 100000000)
    elif n >= 10000:
        return '%.1f万' % (n / 10000)
    return str(n)

# 主流程
print('=== 抖音AI技术内容抓取 ===')
print('')

# 1. 获取热搜词
hot_words = get_douyin_hot_words()
if not hot_words:
    print('无法获取热搜词，退出')
    sys.exit(1)

# 2. 筛选AI相关热搜词
ai_keywords = ['AI', 'ChatGPT', '人工智能', 'GPT', '大模型', '深度学习', '机器学习', 
               '神经网络', 'AI绘画', 'AI工具', 'AIGC', 'Copilot', 'Claude', 'Gemini']
relevant_words = [w for w in hot_words if any(k in w['word'] for k in ai_keywords)]
print('AI相关热搜词: %d' % len(relevant_words))
for w in relevant_words[:10]:
    print('  - %s (热度:%s)' % (w['word'], format_number(w['heat'])))

# 3. 尝试搜索API
print('')
print('=== 尝试搜索API ===')
search_terms = ['AI人工智能技术', 'ChatGPT技巧', 'AI工具使用', '大模型应用']
all_videos = []

for term in search_terms:
    print('[%s] 搜索: %s' % (time.strftime('%H:%M:%S'), term))
    data = search_douyin_video(term)
    if data and data.get('data'):
        videos = data['data'].get('video_list', []) or data['data'].get('videos', []) or []
        if videos:
            print('  Found %d videos' % len(videos))
            all_videos.extend(videos)
        else:
            print('  No videos in response, keys: %s' % list(data.get('data', {}).keys()))
    time.sleep(2)

print('')
print('=== 搜索到 %d 个视频 ===' % len(all_videos))

# 4. 如果搜索没结果，尝试用yt-dlp抓热门视频页面
if len(all_videos) < 10:
    print('')
    print('=== 搜索结果不足，尝试yt-dlp ===')
    # 抖音热门视频页
    douyin_urls = [
        'https://www.douyin.com/video/7354820587852338443',
        'https://www.douyin.com/video/7355892973375622416',
        'https://www.douyin.com/video/7356820587852338443',
    ]
    for url in douyin_urls:
        print('Fetching: %s' % url)
        info = get_video_detail_with_yt_dlp(url)
        if info:
            print('  Title: %s' % info.get('title', '')[:50])
            print('  Views: %s' % format_number(info.get('statistics', {}).get('play_count', 0)))
        time.sleep(1)

# 5. 保存结果
output = {
    'hot_words': hot_words[:20],
    'ai_keywords': relevant_words,
    'search_videos': all_videos[:100],
    'fetch_time': time.strftime('%Y-%m-%d %H:%M:%S'),
}

output_file = 'E:/workspace/content-hunter/data/douyin_api_result.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print('')
print('Saved to: %s' % output_file)
print('Hot words: %d, AI words: %d, Videos: %d' % (len(hot_words), len(relevant_words), len(all_videos)))
