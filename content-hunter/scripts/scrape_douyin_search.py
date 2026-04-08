# -*- coding: utf-8 -*-
"""
通过搜索引擎获取抖音AI相关内容
使用 Bing/Toutiao 搜索API 绕过反爬
"""
import requests
import json
import time
import re
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'https://so.toutiao.com/'
}

all_items = []
seen_urls = set()

# 方法1: 尝试头条搜索API (字节系，更容易通)
print("=== 方法1: 头条搜索API ===")
api_urls = [
    # 头条搜索
    'https://so.toutiao.com/search?keyword=AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&source=input&pd=video',
]

for url in api_urls:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"头条搜索状态: {r.status_code}, 长度: {len(r.text)}")
    except Exception as e:
        print(f"头条搜索失败: {e}")

# 方法2: 通过Google/Bing搜索 douyin.com AI
print("\n=== 方法2: 搜索引擎 ===")
search_keywords = [
    'site:douyin.com AI人工智能 教程',
    'site:douyin.com ChatGPT 使用教程',
    'site:douyin.com 大模型 LLM',
    'site:douyin.com AIGC 工具 教程',
    'site:douyin.com AI绘图 Midjourney',
    'site:douyin.com 人工智能 技术',
    'site:douyin.com AI写作 GPT',
    'site:douyin.com AI视频 生成',
]

# Bing免费搜索（通过serpapi风格）
for kw in search_keywords[:3]:  # 先试3个
    try:
        # 使用DuckDuckGo (免费，无需API key)
        ddg_url = f'https://html.duckduckgo.com/html/?q={kw}&ia=web'
        r = requests.get(ddg_url, headers=headers, timeout=10)
        if r.status_code == 200:
            # 提取抖音链接
            links = re.findall(r'https://www\.douyin\.com/video/\d+', r.text)
            print(f"关键词'{kw}': 找到 {len(links)} 个抖音链接")
            for link in links:
                if link not in seen_urls:
                    seen_urls.add(link)
    except Exception as e:
        print(f"搜索失败: {e}")
    time.sleep(1)

print(f"\n通过搜索引擎找到 {len(seen_urls)} 个抖音链接")

# 方法3: 尝试直接访问可用的抖音API端点
print("\n=== 方法3: 尝试抖音移动端API ===")
mobile_keywords = ['AI教程', 'ChatGPT', 'AIGC']
for kw in mobile_keywords:
    url = f'https://m.douyin.com/search/{kw}'
    try:
        r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        print(f"移动端抖音状态: {r.status_code}, URL: {r.url[:80]}")
        if 'verify' not in r.url.lower() and r.status_code == 200:
            # 提取视频信息
            titles = re.findall(r'"desc":"([^"]+)"', r.text)
            authors = re.findall(r'"nickname":"([^"]+)"', r.text)
            diggs = re.findall(r'"digg_count":(\d+)', r.text)
            print(f"  找到 {len(titles)} 条数据")
            for i, (title, author, digg) in enumerate(zip(titles[:20], authors[:20], diggs[:20])):
                if title and i not in seen_urls:
                    all_items.append({
                        'title': title,
                        'author': author,
                        'digg_count': digg,
                        'source': 'mobile_douyin'
                    })
    except Exception as e:
        print(f"移动端失败: {e}")
    time.sleep(1)

print(f"\n=== 汇总 ===")
print(f"抖音数据条目: {len(all_items)}")

# 保存
if all_items:
    with open('E:/workspace/content-hunter/data/douyin_raw.json', 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    print("已保存到 douyin_raw.json")
else:
    print("未能获取到抖音数据")
