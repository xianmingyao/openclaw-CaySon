import requests
import json
import time
import re

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.bilibili.com',
    'Origin': 'https://www.bilibili.com'
})

all_results = []

# Try multiple search terms
search_terms = [
    'AI人工智能',
    'ChatGPT教程',
    'GPT-4使用',
    '机器学习教程',
    '深度学习实战',
    '神经网络原理'
]

for term in search_terms:
    print(f'\n=== Searching: {term} ===')
    
    # Try searching using the web-interface search API
    for page in range(1, 6):
        try:
            url = 'https://api.bilibili.com/x/web-interface/search/type'
            params = {
                'search_key': term,
                'page': page,
                'pagesize': 20,
                'order': 'totalrank',
                'duration': 0,
                'platform': 'web',
                'websearch': 1,
                'category_id': 0,
                'refresh': 1
            }
            
            resp = session.get(url, params=params, timeout=15)
            print(f'  Page {page}: {resp.status_code}')
            
            if resp.status_code == 200:
                try:
                    data = resp.json()
                    if data.get('code') == 0:
                        result = data.get('data', {})
                        if 'result' in result:
                            videos = result['result']
                            print(f'    Found {len(videos)} videos')
                            for v in videos:
                                if isinstance(v, dict) and v.get('type') == 'video':
                                    vid = {
                                        'title': re.sub(r'<[^>]+>', '', v.get('title', '')),
                                        'author': v.get('author', ''),
                                        'bvid': v.get('bvid', ''),
                                        'aid': v.get('aid', ''),
                                        'play': v.get('play', '0'),
                                        'like': v.get('like', '0'),
                                        'duration': v.get('duration', ''),
                                        'tag': term
                                    }
                                    all_results.append(vid)
                    elif data.get('code') == -412:
                        print(f'    Blocked! Waiting...')
                        time.sleep(5)
                except json.JSONDecodeError:
                    print(f'    Invalid JSON response')
            time.sleep(1)
        except Exception as e:
            print(f'    Error: {e}')
    
    time.sleep(2)

# Deduplicate by bvid
seen = set()
unique = []
for v in all_results:
    if v['bvid'] and v['bvid'] not in seen:
        seen.add(v['bvid'])
        unique.append(v)

print(f'\n=== Total: {len(all_results)}, Unique: {len(unique)} ===')

# Save raw results
with open('E:/workspace/content-hunter/data/bilibili_ai_raw.json', 'w', encoding='utf-8') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)
print('Saved raw results')

# Now fetch detailed info for each unique video
print('\n=== Fetching detailed info ===')
detailed = []
for i, v in enumerate(unique[:100]):  # Limit to 100
    try:
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={v['bvid']}"
        resp = session.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('code') == 0:
                detail = data.get('data', {})
                stat = detail.get('stat', {})
                detailed.append({
                    'title': detail.get('title', ''),
                    'author': detail.get('owner', {}).get('name', ''),
                    'bvid': v['bvid'],
                    'aid': detail.get('aid', ''),
                    'play': stat.get('view', 0),
                    'like': stat.get('like', 0),
                    'coin': stat.get('coin', 0),
                    'favorite': stat.get('favorite', 0),
                    'share': stat.get('share', 0),
                    'danmaku': stat.get('danmaku', 0),
                    'duration': detail.get('duration', 0),
                    'tname': detail.get('tname', ''),
                    'desc': detail.get('desc', '')[:200],
                    'tag': v['tag']
                })
                print(f"  {i+1}. {detail.get('title', '')[:40]} | Play: {stat.get('view', 0)}")
        time.sleep(0.3)
    except Exception as e:
        print(f'  Error fetching {v["bvid"]}: {e}')

print(f'\n=== Detailed results: {len(detailed)} ===')

# Save detailed results
with open('E:/workspace/content-hunter/data/bilibili_ai_detailed.json', 'w', encoding='utf-8') as f:
    json.dump(detailed, f, ensure_ascii=False, indent=2)
print('Saved detailed results')
