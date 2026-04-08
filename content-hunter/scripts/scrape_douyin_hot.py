# -*- coding: utf-8 -*-
"""
深入抓取抖音热榜API + 百度索引的抖音内容
"""
import requests
import json
import re
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Referer': 'https://www.douyin.com/',
    'Accept': 'application/json, text/plain, */*',
}

all_items = []
seen_ids = set()

# === 方法1: 抖音热榜API ===
print("=== 抖音热榜 ===")
try:
    url = 'https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383&channel=channel_pc_web&detail_list=1'
    r = requests.get(url, headers=headers, timeout=15)
    print(f'状态: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        if 'data' in data and 'word_list' in data['data']:
            word_list = data['data']['word_list']
            print(f'热榜条目: {len(word_list)}')
            for item in word_list:
                word = item.get('word', '')
                hot_value = item.get('hot_value', '0')
                # 尝试获取视频ID
                video_ids = re.findall(r'\d{19}', str(item))
                for vid in video_ids[:1]:
                    if vid not in seen_ids:
                        seen_ids.add(vid)
                        all_items.append({
                            'id': vid,
                            'title': f'#{word}#',
                            'author': '',
                            'digg': hot_value,
                            'url': f'https://www.douyin.com/video/{vid}',
                            'platform': 'douyin_hot'
                        })
            print(f'  提取到: {len(all_items)} 条热榜内容')
        else:
            print(f'  data结构: {str(data)[:300]}')
except Exception as e:
    print(f'Error: {e}')

# === 方法2: 抖音热门话题API ===
print("\n=== 抖音热门话题 ===")
try:
    url = 'https://www.douyin.com/aweme/v1/web/challenge/search/?device_platform=webapp&aid=6383&keyword=AI'
    r = requests.get(url, headers=headers, timeout=15)
    print(f'话题搜索状态: {r.status_code}')
    if r.status_code == 200:
        try:
            data = r.json()
            print(f'  keys: {list(data.keys()) if isinstance(data, dict) else "not dict"}')
        except:
            print(f'  响应: {r.text[:200]}')
except Exception as e:
    print(f'Error: {e}')

# === 方法3: 通过百度深度抓取（有标题的） ===
print("\n=== 百度深度抓取 ===")
baidu_kws = [
    ('抖音 AI人工智能 教程', 30),
    ('抖音 ChatGPT 使用技巧', 30),
    ('抖音 大模型 LLM', 30),
    ('抖音 AIGC 工具教程', 30),
]

for kw, count in baidu_kws:
    encoded = kw.replace(' ', '+')
    url = f'https://www.baidu.com/s?wd={encoded}&rn={count}'
    try:
        r = requests.get(url, headers={
            **headers,
            'Accept': 'text/html',
        }, timeout=15)
        if r.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, 'html.parser')
            
            # 找所有搜索结果条目
            results = soup.find_all('div', class_='c-container')
            for res in results:
                link = res.find('a', href=True)
                if not link:
                    continue
                href = link.get('href', '')
                # 找抖音链接
                vid_match = re.search(r'douyin\.com/video/(\d+)', href)
                if vid_match:
                    vid = vid_match.group(1)
                    if vid not in seen_ids:
                        seen_ids.add(vid)
                        # 尝试从同一result块获取标题
                        title = link.get_text(strip=True)[:200]
                        # 也尝试从h3获取
                        h3 = res.find('h3')
                        if h3:
                            title = h3.get_text(strip=True)[:200]
                        all_items.append({
                            'id': vid,
                            'title': title,
                            'author': '',
                            'digg': '0',
                            'url': f'https://www.douyin.com/video/{vid}',
                            'platform': 'douyin_baidu'
                        })
            
            print(f'关键词[{kw[:10]}]: 找到 {len(results)} 个结果, 当前总计 {len(all_items)} 条')
    except Exception as e:
        print(f'  Error: {e}')
    time.sleep(3)

print(f"\n=== 最终汇总 ===")
print(f"总计获取: {len(all_items)} 条")

# 去重
unique = {}
for item in all_items:
    if item['id'] not in unique:
        unique[item['id']] = item

final = list(unique.values())
print(f"去重后: {len(final)} 条")

with open('E:/workspace/content-hunter/data/douyin_raw.json', 'w', encoding='utf-8') as f:
    json.dump(final, f, ensure_ascii=False, indent=2)
print("已保存到 douyin_raw.json")
