import requests
import json
import time

# Bilibili search API
url = 'https://api.bilibili.com/x/web-interface/search/type'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://search.bilibili.com',
    'Cookie': ''  # Add cookie if available
}

search_terms = ['AI人工智能', 'ChatGPT', 'GPT-4', '机器学习', '深度学习', '神经网络']
results = []

for term in search_terms:
    print(f'\nSearching for: {term}')
    for page in range(1, 4):  # 3 pages per term = ~60 results per term
        params = {
            'search_key': term,
            'page': page,
            'pagesize': 20,
            'order': 'totalrank',
            'duration': 0,
            'platform': 'web',
            'websearch': 1
        }
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            print(f'  Page {page}: Status {resp.status_code}')
            if resp.status_code == 200:
                content = resp.text
                if content.startswith('{'):
                    data = json.loads(content)
                    if data.get('code') == 0:
                        result_list = data.get('data', {}).get('result', [])
                        print(f'    Found {len(result_list)} results')
                        for item in result_list:
                            if item.get('type') == 'video':
                                results.append({
                                    'title': item.get('title', '').replace('<em class="keyword">', '').replace('</em>', ''),
                                    'author': item.get('author', ''),
                                    'aid': item.get('aid', ''),
                                    'bvid': item.get('bvid', ''),
                                    'play': item.get('play', '0'),
                                    'video_review': item.get('video_review', '0'),
                                    'like': item.get('like', '0'),
                                    'duration': item.get('duration', ''),
                                    'tag': term
                                })
                time.sleep(0.3)
        except Exception as e:
            print(f'  Error on page {page}: {e}')
    time.sleep(0.5)

print(f'\nTotal AI videos collected: {len(results)}')

# Deduplicate by bvid
seen = set()
deduped = []
for v in results:
    if v['bvid'] not in seen:
        seen.add(v['bvid'])
        deduped.append(v)

print(f'After dedup: {len(deduped)}')

# Save
with open('E:/workspace/content-hunter/data/bilibili_ai_raw.json', 'w', encoding='utf-8') as f:
    json.dump(deduped, f, ensure_ascii=False, indent=2)
print('Saved to bilibili_ai_raw.json')
