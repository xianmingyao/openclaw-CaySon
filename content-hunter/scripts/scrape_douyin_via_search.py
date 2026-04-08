# -*- coding: utf-8 -*-
"""
通过搜索引擎（Google/Bing/DuckDuckGo）获取抖音AI内容
"""
import requests
import json
import re
import time
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def scrape_via_duckduckgo(keyword, max_results=30):
    """通过DuckDuckGo获取搜索结果"""
    results = []
    seen = set()
    
    for page in range(1, 4):  # 3页
        offset = (page - 1) * 30
        url = f'https://html.duckduckgo.com/html/?q={keyword}&s={(page-1)*30}'
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code != 200:
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                # 找抖音链接
                if 'douyin.com/video' in href:
                    match = re.search(r'douyin\.com/video/(\d+)', href)
                    if match:
                        vid = match.group(1)
                        if vid not in seen:
                            seen.add(vid)
                            # 尝试从链接上下文获取标题
                            title = link.get_text(strip=True)
                            if len(title) > 5:
                                results.append({
                                    'id': vid,
                                    'title': title[:200],
                                    'author': '',
                                    'digg': '0',
                                    'url': f'https://www.douyin.com/video/{vid}'
                                })
        except Exception as e:
            print(f'  DDG page {page} error: {e}')
        time.sleep(2)
    
    return results

def scrape_via_bing_api(keyword):
    """通过Bing获取搜索结果"""
    results = []
    seen = set()
    
    url = f'https://cn.bing.com/search?q={keyword}+site:douyin.com'
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            # 提取抖音链接
            ids = re.findall(r'douyin\.com/video/(\d+)', r.text)
            print(f'  Bing: 找到 {len(ids)} 个抖音链接')
            for vid in ids:
                if vid not in seen:
                    seen.add(vid)
                    results.append({
                        'id': vid,
                        'title': '',
                        'author': '',
                        'digg': '0', 
                        'url': f'https://www.douyin.com/video/{vid}'
                    })
    except Exception as e:
        print(f'  Bing error: {e}')
    
    return results

# 主流程
all_results = []
seen_ids = set()

search_keywords = [
    '抖音 AI人工智能 教程',
    '抖音 ChatGPT 使用技巧',
    '抖音 大模型 LLM 教程',
    '抖音 AIGC 工具 使用',
    '抖音 AI绘图 Midjourney',
    '抖音 AI写作 prompts',
    '抖音 人工智能 技术',
    '抖音 AI视频 生成',
]

print("=== 通过DuckDuckGo搜索 ===")
for kw in search_keywords:
    print(f"搜索: {kw}")
    results = scrape_via_duckduckgo(kw)
    for r in results:
        if r['id'] not in seen_ids:
            seen_ids.add(r['id'])
            all_results.append(r)
    print(f"  本次增加: {len(results)}, 累计: {len(all_results)}")
    time.sleep(1)

print(f"\n=== 通过Bing搜索 ===")
for kw in search_keywords[:3]:
    print(f"搜索: {kw}")
    results = scrape_via_bing_api(kw)
    for r in results:
        if r['id'] not in seen_ids:
            seen_ids.add(r['id'])
            all_results.append(r)
    time.sleep(2)

print(f"\n总计获取: {len(all_results)} 条")

if all_results:
    with open('E:/workspace/content-hunter/data/douyin_raw.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"已保存到 douyin_raw.json")
else:
    print("警告: 未能获取到抖音数据")
