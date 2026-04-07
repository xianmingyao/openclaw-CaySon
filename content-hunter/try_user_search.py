import urllib.request, urllib.parse, json, time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.douyin.com/',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

# Try user search API
print('=== User Search API ===')
url = 'https://www.douyin.com/aweme/v1/web/search/user/?' + urllib.parse.urlencode({
    'keyword': 'AI',
    'count': '20',
    'offset': '0',
    'device_platform': 'webapp',
    'aid': '6383',
    'channel': 'channel_pc_web',
    'search_channel': 'aweme_user_web',
    'sort_type': '0',
    'publish_time': '0',
    'source': 'normal_search',
    'pc_client_type': '1',
    'version_code': '190600',
    'version_name': '19.6.0',
})

req = urllib.request.Request(url, headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    raw = resp.read().decode('utf-8')
    data = json.loads(raw)
    print('Status:', data.get('status_code'))
    print('Has more:', data.get('has_more', 0))
    user_list = data.get('user_list', []) or data.get('data', [])
    print('User count:', len(user_list))
    for u in user_list[:3]:
        print('  -', u.get('user_info', {}).get('nickname', ''))
except Exception as e:
    print('Error:', e)

# Try the video search with different sort order
print('\n=== Video Search by likes ===')
url2 = 'https://www.douyin.com/aweme/v1/web/search/item/?' + urllib.parse.urlencode({
    'keyword': 'AI',
    'count': '20',
    'offset': '0',
    'device_platform': 'webapp',
    'aid': '6383',
    'channel': 'channel_pc_web',
    'search_channel': 'aweme_video_web',
    'sort_type': '2',  # Sort by likes
    'publish_time': '0',
    'source': 'normal_search',
    'pc_client_type': '1',
    'version_code': '190600',
    'version_name': '19.6.0',
    'cookie_enabled': 'true',
    'screen_width': '1920',
    'screen_height': '1080',
    'browser_language': 'zh-CN',
    'browser_platform': 'Win32',
    'browser_name': 'Chrome',
    'browser_version': '120.0.0.0',
})

req2 = urllib.request.Request(url2, headers=headers)
try:
    resp2 = urllib.request.urlopen(req2, timeout=15)
    raw2 = resp2.read().decode('utf-8')
    data2 = json.loads(raw2)
    print('Status:', data2.get('status_code'))
    print('Has more:', data2.get('has_more', 0))
    items = data2.get('data', [])
    print('Items count:', len(items))
    for item in items[:3]:
        aweme = item.get('aweme_info', {}) or item
        print('  -', aweme.get('desc', '')[:50])
except Exception as e:
    print('Error:', e)
