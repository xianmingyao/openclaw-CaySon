import urllib.request
import json

url = 'https://api.bilibili.com/x/web-interface/search/type?keyword=AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&search_type=video&order=hot&page=1&pagesize=20&platform=web'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://search.bilibili.com/',
    'Origin': 'https://search.bilibili.com',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
}
req = urllib.request.Request(url, headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode('utf-8'))
    if data.get('code') == 0:
        results = data.get('data', {}).get('result', [])
        print(f'Found {len(results)} results')
        for i, r in enumerate(results[:5]):
            title = r.get('title', '').replace('<em class=\"keyword\">', '').replace('</em>', '')
            print(f"  {i+1}. {title} - {r.get('author', '')} - {r.get('play', 0)} plays")
    else:
        print(f"API error: {data.get('message', 'unknown')}")
except Exception as e:
    print(f'Error: {e}')
