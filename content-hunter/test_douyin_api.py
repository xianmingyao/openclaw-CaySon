#!/usr/bin/env python3
import urllib.request, urllib.parse, json, sys

keyword = 'AI人工智能'
encoded_kw = urllib.parse.quote(keyword)

url = f'https://www.douyin.com/aweme/v1/web/search/item/?keyword={encoded_kw}&count=20&offset=0&device_platform=webapp&aid=6383&channel=channel_pc_web&pc_client_type=1&version_code=190600&cookie_enabled=true&screen_width=1920&screen_height=1080&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=120.0.0.0'

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
    
    status = data.get('status_code', -1)
    aweme_list = data.get('aweme_list') or []
    data_list = data.get('data') or []
    
    print(f'status_code: {status}')
    print(f'aweme_list: {len(aweme_list)}')
    print(f'data: {len(data_list)}')
    print(f'has_more: {data.get("has_more")}')
    
    if aweme_list:
        print('\nFirst 3:')
        for a in aweme_list[:3]:
            desc = a.get('desc', '')
            author = a.get('author', {}).get('nickname', '')
            digg = a.get('statistics', {}).get('digg_count', 0)
            print(f'  [{digg}赞] {desc[:60]} - {author}')
    elif data_list:
        print('\ndata[0] sample:')
        item = data_list[0]
        if isinstance(item, dict):
            print('  keys:', list(item.keys())[:10])
            desc = item.get('aweme_info', {}).get('desc', '') or item.get('desc', '')
            print('  desc:', desc[:60])
    
    # Save raw
    out = r'E:\workspace\content-hunter\data\douyin_api_test.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'\nSaved to {out}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
