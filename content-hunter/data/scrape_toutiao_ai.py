# -*- coding: utf-8 -*-
"""
内容捕手 - 头条/抖音AI技术热门内容追加抓取（100条）
头条搜索API + 抖音热门API + 搜索混合
"""
import requests
import json
import time
import re
import sys
import random

sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
]

def get_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://so.toutiao.com/',
        'Cookie': 'ttwid=1%7Cxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx; s_v_web_id=verify_xxxxxxxxxx;',
    }

def format_number(n):
    """格式化数字"""
    if not n:
        return '未知'
    if isinstance(n, str):
        try:
            n = int(n.replace('万', '').replace(',', '')) if '万' not in n else float(n.replace('万', '')) * 10000
        except:
            n = 0
    if isinstance(n, float):
        n = int(n)
    if n >= 100000000:
        return '%.1f亿' % (n / 100000000)
    elif n >= 10000:
        return '%.1f万' % (n / 10000)
    return str(n)

def get_toutiao_search(keyword, page=1):
    """头条搜索API"""
    url = 'https://so.toutiao.com/c/search/search'
    params = {
        'keyword': keyword,
        'pd': 'video',
        'page': page,
        'npc': '0',
        'nspm': '1',
        'pageSize': '20',
    }
    headers = get_headers()
    headers['Referer'] = 'https://so.toutiao.com/'
    try:
        resp = session.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('data', {}).get('videoList', [])
            if items:
                return items
    except Exception as e:
        print('  头条搜索失败 [%s]: %s' % (keyword, e))
    return []

def get_douyin_hot():
    """抖音热搜API"""
    url = 'https://www.douyin.com/aweme/v1/web/hot/search/list/'
    params = {
        'device_platform': 'webapp',
        'aid': '6383',
        'channel': 'channel_pc_web',
        'detail_list': '1',
    }
    headers = get_headers()
    headers['Referer'] = 'https://www.douyin.com/'
    try:
        resp = session.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            word_list = data.get('data', {}).get('word_list', [])
            return word_list
    except Exception as e:
        print('  抖音热搜API失败: %s' % e)
    return []

def get_toutiao_hot():
    """头条热榜API"""
    url = 'https://www.toutiao.com/api/pc/feed/'
    params = {
        'max_behot_time': '0',
        'tab_name': 'hot_list',
    }
    headers = get_headers()
    headers['Referer'] = 'https://www.toutiao.com/'
    try:
        resp = session.get(url, params=params, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('data', [])
    except Exception as e:
        print('  头条热榜失败: %s' % e)
    return []

# 读取现有条数
existing_count = 0
existing_titles = set()
try:
    with open('E:/workspace/content-hunter/data/douyin.md', 'r', encoding='utf-8') as f:
        content = f.read()
    matches = re.findall(r'第(\d+)条', content)
    if matches:
        existing_count = max(int(x) for x in matches)
    # 获取已有标题用于去重
    title_matches = re.findall(r'- 标题: (.+)', content)
    existing_titles = set(title_matches)
    print('现有抖音数据: %d 条' % existing_count)
    print('已有标题去重: %d 个' % len(existing_titles))
except Exception as e:
    print('读取现有文件失败: %s' % e)

print('=== 头条/抖音AI技术内容追加抓取 ===')
print('目标: 追加100条新内容')
print('')

# 策略1: 头条搜索AI相关视频
print('[策略1] 头条搜索AI技术视频...')
search_terms = [
    'AI人工智能技术', 'ChatGPT使用技巧', 'GPT使用教程', 'AI工具推荐',
    '大模型应用', 'AI绘画教程', '深度学习', '机器学习',
    'Claude教程', 'Gemini AI', 'AI Agent', 'AIGC创作',
    'Stable Diffusion', 'Midjourney技巧', 'AI视频生成',
    'Copilot教程', 'AI编程', '神经网络', 'LLM大模型',
    'OpenAI使用', '文心一言', '通义千问', 'Kimi AI', '豆包AI',
]

all_videos = []
for term in search_terms:
    if len(all_videos) >= 120:
        break
    print('  搜索: %s' % term)
    for page in range(1, 4):
        if len(all_videos) >= 120:
            break
        items = get_toutiao_search(term, page=page)
        if not items:
            break
        for item in items:
            if len(all_videos) >= 120:
                break
            video_data = {
                'title': item.get('title', ''),
                'author': '@' + item.get('user_info', {}).get('name', item.get('source', '未知')),
                'like': item.get('digg_count', item.get('go_detail_count', 0)),
                'comment': item.get('comment_count', 0),
                'video_duration': item.get('video_duration', 0),
                'abstract': item.get('abstract', ''),
                'url': item.get('display_url', item.get('url', '')),
            }
            if video_data['title'] and video_data['title'] not in existing_titles:
                all_videos.append(video_data)
        time.sleep(0.3)

print('  头条搜索到: %d 个视频' % len(all_videos))

# 策略2: 抖音热搜
print('')
print('[策略2] 获取抖音热搜...')
hot_words = get_douyin_hot()
ai_keywords = ['AI', 'ChatGPT', '人工智能', 'GPT', '大模型', '深度学习', '机器学习',
               '神经网络', 'AI绘画', 'AIGC', 'Copilot', 'Claude', 'Gemini', 'LLM',
               'OpenAI', '文心', '通义', 'Kimi', '豆包', '智谱', 'AI工具', 'AI技术', 'StableDiffusion']
ai_hot = [w for w in hot_words if any(k in w.get('word', '') for k in ai_keywords)]
print('  AI相关热搜: %d 个' % len(ai_hot))
for w in ai_hot[:10]:
    print('    - %s (热度:%s)' % (w.get('word', ''), format_number(w.get('hot_value', 0))))

# 策略3: 头条热榜中的AI相关
print('')
print('[策略3] 头条热榜...')
toutiao_hot = get_toutiao_hot()
ai_toutiao = [item for item in toutiao_hot if any(k in item.get('title', '') + item.get('abstract', '') for k in ai_keywords)]
print('  头条热榜AI内容: %d 个' % len(ai_toutiao))

# 合并去重
seen_titles = set(v['title'] for v in all_videos)
for item in ai_toutiao:
    title = item.get('title', '')
    if title and title not in seen_titles and title not in existing_titles:
        seen_titles.add(title)
        all_videos.append({
            'title': title,
            'author': '@' + item.get('source', '头条热榜'),
            'like': item.get('digg_count', 0),
            'comment': item.get('comment_count', 0),
            'video_duration': 0,
            'abstract': item.get('abstract', ''),
            'url': item.get('url', ''),
        })

print('')
print('=== 共获取 %d 个有效视频 ===' % len(all_videos))

# 生成话题标签
def gen_tags(title):
    tags = []
    t = title.lower()
    if 'chatgpt' in t or 'gpt' in t: tags.append('#ChatGPT')
    if 'ai' in t or '人工智能' in title: tags.append('#AI技术')
    if any(k in t for k in ['绘画', 'stable', 'midjourney', 'sd画']): tags.append('#AI绘画')
    if any(k in t for k in ['视频', 'sora', 'runway', 'pika']): tags.append('#AI视频')
    if any(k in t for k in ['代码', 'copilot', 'claude', '编程', 'agent']): tags.append('#AI编程')
    if any(k in t for k in ['大模型', 'llm', 'gpt-', 'gemini', '文心', '通义', 'kimi']): tags.append('#大模型')
    if any(k in t for k in ['深度学习', '神经网络', '机器学习']): tags.append('#深度学习')
    if not tags: tags.append('#AI技术')
    return ' '.join(tags)

# 追加到文件
start_num = existing_count + 1
md_lines = []

for i, v in enumerate(all_videos[:100]):
    num = start_num + i
    title = v.get('title', '未知标题')
    author = v.get('author', '@未知用户')
    like = format_number(v.get('like', 0))
    comment = format_number(v.get('comment', 0))
    url = v.get('url', '')
    abstract = v.get('abstract', '')[:200]
    summary = abstract if abstract else '暂无描述'

    md_lines.append('')
    md_lines.append('### 第%d条' % num)
    md_lines.append('- 标题: %s' % title)
    md_lines.append('- 作者: %s' % author)
    md_lines.append('- 点赞: %s' % like)
    md_lines.append('- 评论: %s' % comment)
    md_lines.append('- 话题: %s' % gen_tags(title))
    md_lines.append('- 内容总结: %s' % summary)
    md_lines.append('- 链接: %s' % url)

with open('E:/workspace/content-hunter/data/douyin.md', 'a', encoding='utf-8') as f:
    f.write('\n'.join(md_lines))

new_count = min(len(all_videos), 100)
print('追加完成！')
print('新增 %d 条，现有总计约 %d 条' % (new_count, existing_count + new_count))
