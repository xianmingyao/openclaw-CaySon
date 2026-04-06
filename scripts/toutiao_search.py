import requests, json

# Try Toutiao search API
url = 'https://so.toutiao.com/csearch/search'
params = {
    'keyword': 'AI人工智能 视频',
    'pd': 'video',
    'offset': 0,
    'count': 20,
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://so.toutiao.com/',
}
try:
    r = requests.get(url, params=params, headers=headers, timeout=10)
    print('Status:', r.status_code)
    print('Response:', r.text[:1000])
except Exception as e:
    print(f'Exception: {e}')
