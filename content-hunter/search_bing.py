# -*- coding: utf-8 -*-
import urllib.request
import urllib.parse
import re
import time
import os
import sys

# Fix stdout encoding for Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

def fetch_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        return html
    except Exception as e:
        return f'ERROR: {e}'

def bing_search(query, num=20):
    q = urllib.parse.quote(query)
    url = f'https://www.bing.com/search?q={q}&count={num}'
    return fetch_url(url)

def clean_html(text):
    return re.sub(r'<[^>]+>', '', text).strip()

def extract_bing_results(html, domain):
    """Extract titles and links from Bing search results"""
    results = []
    
    # Find all result blocks
    # Bing uses li with class="b_algo"
    items = re.findall(r'<li[^>]*class="b_algo"[^>]*>(.*?)</li>', html, re.DOTALL)
    
    for item in items:
        # Extract title from h2
        title_match = re.search(r'<h2[^>]*>(.*?)</h2>', item, re.DOTALL)
        if not title_match:
            continue
        title = clean_html(title_match.group(1))
        
        # Extract link - Bing redirects through /url?q=
        link_match = re.search(r'href="(/url\?q=([^"]+))"', item)
        if not link_match:
            continue
        link = urllib.parse.unquote(link_match.group(2))
        
        # Filter by domain
        if domain not in link:
            continue
        
        # Extract snippet/description
        snippet_match = re.search(r'<p[^>]*>(.*?)</p>', item, re.DOTALL)
        snippet = clean_html(snippet_match.group(1)) if snippet_match else ''
        
        results.append({
            'title': title[:100],
            'url': link[:200],
            'snippet': snippet[:200]
        })
    
    return results

# ========== 抖音 ==========
print('=' * 60)
print('[1/2] Bing 搜索: 抖音 AI热门内容')
print('=' * 60)

douyin_results = []
queries_dy = [
    'site:douyin.com AI人工智能 教程 2026',
    'site:douyin.com ChatGPT 使用技巧',
    'site:douyin.com AI绘画 教程',
    'site:douyin.com 大模型 LLM',
    'site:douyin.com AIGC 创作',
    'site:douyin.com AI工具 效率',
    'site:douyin.com 深度学习 教程',
    'site:douyin.com AI视频 Sora',
]

for q in queries_dy:
    print(f'  [{q[:40]}...]', end=' ')
    html = bing_search(q)
    if html.startswith('ERROR'):
        print(f'ERROR: {html}')
        continue
    items = extract_bing_results(html, 'douyin.com')
    print(f'找到 {len(items)} 条')
    douyin_results.extend(items)
    time.sleep(0.5)

# 去重
seen = set()
unique_dy = []
for r in douyin_results:
    key = r['title'][:30]
    if key and key not in seen:
        seen.add(key)
        unique_dy.append(r)

print(f'\n抖音共获取 {len(unique_dy)} 条有效结果')

# ========== B站 ==========
print('\n' + '=' * 60)
print('[2/2] Bing 搜索: B站 AI热门内容')
print('=' * 60)

bilibili_results = []
queries_bilibili = [
    'site:bilibili.com AI人工智能 教程 2026',
    'site:bilibili.com ChatGPT 使用教程',
    'site:bilibili.com stable diffusion AI绘画',
    'site:bilibili.com 大模型 LLM 教程',
    'site:bilibili.com AIGC 人工智能创作',
    'site:bilibili.com 深度学习 神经网络',
    'site:bilibili.com 机器学习 python',
    'site:bilibili.com AI视频生成 Sora',
]

for q in queries_bilibili:
    print(f'  [{q[:40]}...]', end=' ')
    html = bing_search(q)
    if html.startswith('ERROR'):
        print(f'ERROR: {html}')
        continue
    items = extract_bing_results(html, 'bilibili.com')
    print(f'找到 {len(items)} 条')
    bilibili_results.extend(items)
    time.sleep(0.5)

# 去重
seen = set()
unique_bilibili = []
for r in bilibili_results:
    key = r['title'][:30]
    if key and key not in seen:
        seen.add(key)
        unique_bilibili.append(r)

print(f'\nB站共获取 {len(unique_bilibili)} 条有效结果')

# ========== 保存 ==========
data_dir = 'E:/workspace/content-hunter/data/'
os.makedirs(data_dir, exist_ok=True)

timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

# 抖音
douyin_file = os.path.join(data_dir, 'douyin.md')
with open(douyin_file, 'a', encoding='utf-8') as f:
    f.write(f'\n\n## 抖音 AI技术热门内容\n')
    f.write(f'抓取时间: {timestamp}\n')
    f.write(f'数据来源: Bing site:douyin.com 搜索\n\n')
    for i, r in enumerate(unique_dy[:100], 1):
        f.write(f'### 第{i}条\n')
        f.write(f'- 标题: {r["title"]}\n')
        f.write(f'- 链接: {r["url"]}\n')
        f.write(f'- 摘要: {r["snippet"]}\n')
        f.write(f'- 内容总结: 抖音平台AI相关热门教程与资讯\n\n')

# B站
bilibili_file = os.path.join(data_dir, 'bilibili.md')
with open(bilibili_file, 'a', encoding='utf-8') as f:
    f.write(f'\n\n## B站 AI技术热门内容\n')
    f.write(f'抓取时间: {timestamp}\n')
    f.write(f'数据来源: Bing site:bilibili.com 搜索\n\n')
    for i, r in enumerate(unique_bilibili[:100], 1):
        f.write(f'### 第{i}条\n')
        f.write(f'- 标题: {r["title"]}\n')
        f.write(f'- 链接: {r["url"]}\n')
        f.write(f'- 摘要: {r["snippet"]}\n')
        f.write(f'- 内容总结: B站AI技术热门教程与资讯\n\n')

print(f'\n[DONE]')
print(f'抖音: {len(unique_dy)} 条 -> {douyin_file}')
print(f'B站: {len(unique_bilibili)} 条 -> {bilibili_file}')
