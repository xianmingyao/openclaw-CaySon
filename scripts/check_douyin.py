#!/usr/bin/env python3
import requests, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

url = 'https://www.douyin.com/discover?modal_id=735432'
try:
    r = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
    print(f'Status: {r.status_code}, Length: {len(r.text)}')
    
    # 搜索视频ID模式
    ids = re.findall(r'"aweme_id":"(\d+)"', r.text)
    print(f'Found aweme_ids: {len(set(ids))} unique')
    
    # 标题
    titles = re.findall(r'"desc":"([^"]{10,100})"', r.text)
    print(f'Found titles: {len(titles)}')
    for t in titles[:10]:
        print(f'  - {t[:60]}')
except Exception as e:
    print(f'Error: {e}')
