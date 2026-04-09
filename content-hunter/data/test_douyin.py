#!/usr/bin/env python3
import requests, json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.douyin.com/',
}

# Try the hot search list endpoint
url = 'https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383'
try:
    r = requests.get(url, headers=headers, timeout=8)
    data = r.json()
    print(f'status_code={data.get("status_code")}')
    word_list = data.get('word_list') or []
    print(f'word_list len: {len(word_list)}')
    if word_list:
        for word in word_list[:5]:
            print(f"  #{word.get('word', '')} - 热度:{word.get('hot_value', 0)}")
except Exception as e:
    print(f'Error: {e}')

# Try the search API with correct params
print("\n--- Search API ---")
url2 = 'https://www.douyin.com/aweme/v1/web/search/item/?keyword=AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&count=10&cursor=0&need_filter_settings=1&list_type=11&source=normal_search&search_source=normal_search&query_correct_type=1&aid=6383'
try:
    r = requests.get(url2, headers=headers, timeout=8)
    data = r.json()
    print(f'status_code={data.get("status_code")}')
    al = data.get('aweme_list') or []
    print(f'aweme_list len: {len(al)}')
    for item in al[:3]:
        desc = (item.get('desc') or '')[:80]
        author = (item.get('author') or {}).get('nickname', '?')
        digg = (item.get('statistics') or {}).get('digg_count', 0)
        tags = [(h or {}).get('hashtag_name', '') for h in (item.get('text_extra') or []) if (h or {}).get('hashtag_name')]
        print(f"  desc: {desc}")
        print(f"  author: {author}, likes: {digg}, tags: {tags}")
        print()
except Exception as e:
    print(f'Error: {e}')
