# -*- coding: utf-8 -*-
"""
综合抓取抖音数据 - 多个API端点组合
"""
import requests
import json
import re
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Referer': 'https://www.douyin.com/',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

all_items = {}
seen_ids = set()

def add_item(item):
    vid = item.get('id', '')
    if vid and vid not in seen_ids:
        seen_ids.add(vid)
        all_items[vid] = item

# === 1. 抖音热榜 ===
print("=== 1. 抖音热榜 ===")
try:
    url = 'https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383&channel=channel_pc_web&detail_list=1'
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code == 200:
        data = r.json()
        word_list = data.get('data', {}).get('word_list', [])
        print(f'热榜条目: {len(word_list)}')
        for item in word_list:
            word = item.get('word', '')
            hot_value = item.get('hot_value', '0')
            # 匹配视频ID
            video_ids = re.findall(r'\d{19}', str(item.get('hot_list_item_data', '')))
            for vid in video_ids[:1]:
                add_item({
                    'id': vid,
                    'title': f'热榜: {word}',
                    'author': '',
                    'digg': hot_value,
                    'url': f'https://www.douyin.com/video/{vid}',
                    'platform': 'douyin'
                })
        print(f'累计: {len(all_items)} 条')
except Exception as e:
    print(f'Error: {e}')

# === 2. 抖音搜索API (特定关键词) ===
print("\n=== 2. 抖音搜索API ===")
search_urls = [
    ('AI人工智能', 'https://www.douyin.com/aweme/v1/web/search/item/?keyword=AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&count=20&offset=0&search_source=normal_search& aids=[]&aid=6383'),
    ('ChatGPT', 'https://www.douyin.com/aweme/v1/web/search/item/?keyword=ChatGPT&count=20&offset=0&search_source=normal_search&aid=6383'),
    ('大模型', 'https://www.douyin.com/aweme/v1/web/search/item/?keyword=%E5%A4%A7%E6%A8%A1%E5%9E%8B&count=20&offset=0&search_source=normal_search&aid=6383'),
    ('AIGC', 'https://www.douyin.com/aweme/v1/web/search/item/?keyword=AIGC&count=20&offset=0&search_source=normal_search&aid=6383'),
    ('AI绘图', 'https://www.douyin.com/aweme/v1/web/search/item/?keyword=AI%E7%BB%98%E5%9B%BE&count=20&offset=0&search_source=normal_search&aid=6383'),
]

for kw, url in search_urls:
    try:
        r = requests.get(url, headers=headers, timeout=15)
        print(f'关键词[{kw}]: {r.status_code}')
        if r.status_code == 200:
            try:
                data = r.json()
                items_data = data.get('data', []) or data.get('item_list', [])
                if not items_data:
                    # 尝试其他结构
                    for key in ['items', 'video_list', 'aweme_list']:
                        if key in data:
                            items_data = data[key]
                            break
                print(f'  items: {len(items_data) if items_data else 0}')
                for item in (items_data or [])[:20]:
                    vid = item.get('aweme_id', '')
                    if vid:
                        desc = item.get('desc', '')[:100]
                        author = item.get('author', {}).get('nickname', '')
                        digg = item.get('statistics', {}).get('digg_count', '0')
                        add_item({
                            'id': vid,
                            'title': desc,
                            'author': author,
                            'digg': str(digg),
                            'url': f'https://www.douyin.com/video/{vid}',
                            'platform': 'douyin'
                        })
            except json.JSONDecodeError:
                print(f'  JSON解析失败: {r.text[:100]}')
    except Exception as e:
        print(f'  Error: {e}')
    time.sleep(1)
    print(f'  累计: {len(all_items)} 条')

# === 3. 抖音推荐 feed ===
print("\n=== 3. 抖音推荐feed ===")
try:
    url = 'https://www.douyin.com/aweme/v1/web/tab/feed/?device_platform=webapp&aid=6383'
    r = requests.get(url, headers=headers, timeout=15)
    print(f'推荐feed: {r.status_code}')
    if r.status_code == 200:
        try:
            data = r.json()
            items = data.get('aweme_list', []) or data.get('data', [])
            print(f'  推荐视频: {len(items)}')
            for item in items[:30]:
                vid = item.get('aweme_id', '')
                if vid:
                    desc = item.get('desc', '')[:100]
                    author = item.get('author', {}).get('nickname', '')
                    digg = item.get('statistics', {}).get('digg_count', '0')
                    add_item({
                        'id': vid,
                        'title': desc,
                        'author': author,
                        'digg': str(digg),
                        'url': f'https://www.douyin.com/video/{vid}',
                        'platform': 'douyin'
                    })
        except:
            print(f'  响应: {r.text[:200]}')
except Exception as e:
    print(f'Error: {e}')

print(f"\n=== 最终结果 ===")
final = list(all_items.values())
print(f"总计: {len(final)} 条")

with open('E:/workspace/content-hunter/data/douyin_raw.json', 'w', encoding='utf-8') as f:
    json.dump(final, f, ensure_ascii=False, indent=2)
print("已保存")
