import requests, json, re, sys

# Try Bilibili search API for AI videos
url = 'https://api.bilibili.com/x/web-interface/search/type'
params = {
    'search_type': 'video',
    'keyword': 'AI人工智能',
    'page': 1,
    'order': 'totalrank',
    'duration': 0,
    'tids': 0
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.bilibili.com'
}
try:
    r = requests.get(url, params=params, headers=headers, timeout=10)
    data = r.json()
    if data['code'] == 0:
        videos = data['data']['result'][:20]
        for v in videos:
            title = v.get('title','').replace('<em class="keyword">','').replace('</em>','')
            author = v.get('author','')
            play = v.get('play','')
            like = v.get('like','')
            duration = v.get('duration','')
            bvid = v.get('bvid','')
            description = v.get('description','')[:100]
            print(f"Title: {title}")
            print(f"Author: {author}")
            print(f"Play: {play}, Like: {like}, Duration: {duration}")
            print(f"BV: {bvid}")
            print(f"Desc: {description}")
            print('---')
        print(f"\nTotal fetched: {len(videos)}")
    else:
        print(f'Error: {data["code"]} {data.get("message","")}')
except Exception as e:
    print(f'Exception: {e}')
