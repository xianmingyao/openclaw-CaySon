#!/usr/bin/env python3
"""抓取抖音API搜索结果"""
import urllib.request, json, os, sys

DATA_DIR = r"E:\workspace\content-hunter\data"
OUTPUT_FILE = os.path.join(DATA_DIR, "douyin.md")

url = 'https://www.douyin.com/aweme/v1/web/search/item/?keyword=AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&count=20&offset=0&device_platform=webapp&aid=6383'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.douyin.com/',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    
    aweme_list = data.get('aweme_list', [])
    print(f'aweme_list: {len(aweme_list)} items')
    print(f'status_code: {data.get("status_code")}')
    print(f'has_more: {data.get("has_more")}')
    
    if aweme_list:
        for aweme in aweme_list[:3]:
            desc = aweme.get('desc', '')
            author = aweme.get('author', {}).get('nickname', '')
            aweme_id = aweme.get('aweme_id', '')
            digg_count = aweme.get('statistics', {}).get('digg_count', 0)
            print(f'  - {desc[:60]} | {author} | {digg_count}赞 | id:{aweme_id}')
    else:
        print('Keys:', list(data.keys()))
        print('data keys:', list(data.get('data', {}).keys()) if isinstance(data.get('data'), dict) else str(data.get('data'))[:200])
    
    # Save raw response
    with open(os.path.join(DATA_DIR, 'douyin_api_raw.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print('Raw saved.')
    
except Exception as e:
    print(f'Error: {e}')
