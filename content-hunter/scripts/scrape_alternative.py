# -*- coding: utf-8 -*-
"""
通过字节/百度/微博等替代平台获取AI技术热门内容
"""
import requests
import json
import re
import time
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

all_items = []
seen = set()

# 方法1: 百度搜索 (对中国内容友好)
print("=== 百度搜索 ===")
baidu_keywords = [
    '抖音 AI人工智能 教程',
    '抖音 ChatGPT 使用',
    '抖音 大模型 教程',
    '抖音 AIGC 工具',
    '抖音 AI绘图',
]

for kw in baidu_keywords:
    encoded = kw.replace(' ', '+')
    url = f'https://www.baidu.com/s?wd={encoded}+site:douyin.com&rn=20'
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f'百度 {kw[:15]}... -> {r.status_code}')
        ids = re.findall(r'douyin\.com/video/(\d+)', r.text)
        titles = re.findall(r'class="c-title">([^<]+)', r.text)
        print(f'  IDs:{len(ids)}, titles:{len(titles)}')
        for i, vid in enumerate(ids[:20]):
            if vid not in seen:
                seen.add(vid)
                title = titles[i] if i < len(titles) else ''
                all_items.append({
                    'id': vid,
                    'title': title.strip(),
                    'author': '',
                    'platform': 'douyin',
                    'digg': '0',
                    'url': f'https://www.douyin.com/video/{vid}'
                })
    except Exception as e:
        print(f'  Error: {e}')
    time.sleep(2)

# 方法2: 尝试微博搜索
print("\n=== 微博搜索 ===")
weibo_keywords = ['AI人工智能', 'ChatGPT', '大模型', 'AIGC']
for kw in weibo_keywords[:2]:
    url = f'https://s.weibo.com/weibo?q={kw}&typeall=1&suball=1&timescope=custom:2026-03-01:2026-04-08'
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f'微博 {kw} -> {r.status_code}')
        # 微博视频
        vids = re.findall(r'weibo\.com/tv/show/(\w+)', r.text)
        titles = re.findall(r'class="node_title">([^<]+)', r.text)
        print(f'  微博视频: {len(vids)}')
        for i, vid in enumerate(vids[:10]):
            if vid not in seen:
                seen.add(vid)
                all_items.append({
                    'id': f'weibo_{vid}',
                    'title': titles[i].strip() if i < len(titles) else '',
                    'author': '',
                    'platform': 'weibo',
                    'digg': '0',
                    'url': f'https://weibo.com/tv/show/{vid}'
                })
    except Exception as e:
        print(f'  Error: {e}')
    time.sleep(2)

# 方法3: 知乎
print("\n=== 知乎搜索 ===")
zhihu_keywords = ['AI人工智能', 'ChatGPT', '大模型']
for kw in zhihu_keywords:
    url = f'https://www.zhihu.com/search?type=content&q={kw}'
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f'知乎 {kw} -> {r.status_code}')
    except Exception as e:
        print(f'  Error: {e}')
    time.sleep(1)

# 方法4: 直接尝试抖音的几个公开数据接口
print("\n=== 尝试抖音热榜API ===")
try:
    # 抖音热榜
    url = 'https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383'
    r = requests.get(url, headers={
        **headers,
        'Referer': 'https://www.douyin.com/',
        'Cookie': ''
    }, timeout=10)
    print(f'抖音热榜: {r.status_code}')
    if r.status_code == 200:
        try:
            data = r.json()
            print(f'  data keys: {list(data.keys()) if isinstance(data, dict) else "not dict"}')
        except:
            print(f'  响应: {r.text[:200]}')
except Exception as e:
    print(f'  Error: {e}')

print(f"\n=== 汇总 ===")
print(f"总计获取: {len(all_items)} 条")

# 保存
with open('E:/workspace/content-hunter/data/douyin_raw.json', 'w', encoding='utf-8') as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)
print("已保存")
