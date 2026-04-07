import urllib.request, urllib.parse, json

# Try the hot search list API
url = 'https://www.douyin.com/aweme/v1/web/hot/search/list/?' + urllib.parse.urlencode({
    'device_platform': 'webapp',
    'aid': '6383',
    'channel': 'channel_pc_web',
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

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.douyin.com/',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

req = urllib.request.Request(url, headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    raw = resp.read().decode('utf-8')
    data = json.loads(raw)
    print('Status:', data.get('status_code'))
    word_list = data.get('data', {}).get('word_list', [])
    print('Hot list count:', len(word_list))
    for item in word_list[:10]:
        print('  -', item.get('word', ''), '| hot:', item.get('hot_value', 0))
except Exception as e:
    print('Error:', e)
