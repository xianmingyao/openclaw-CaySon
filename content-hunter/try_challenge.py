import urllib.request, urllib.parse, json, random, time

# Strategy: Get AI-related challenge topics, then get videos from those topics
# Try the challenge search API
results = []

# 1. Try to search for AI-related challenges
challenge_url = 'https://www.douyin.com/aweme/v1/web/challenge/search/?' + urllib.parse.urlencode({
    'keyword': 'AI',
    'count': '20',
    'offset': '0',
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

print('=== Trying challenge search API ===')
req = urllib.request.Request(challenge_url, headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    raw = resp.read().decode('utf-8')
    data = json.loads(raw)
    print('Status:', data.get('status_code'))
    print('Has more:', data.get('has_more', 0))
    challenge_list = data.get('challenge_list', []) or data.get('data', [])
    print('Challenge count:', len(challenge_list))
    for c in challenge_list[:5]:
        print('  -', c.get('challenge_name', ''), '| videos:', c.get('video_count', c.get('stat', {}).get('video_count', '?')))
except Exception as e:
    print('Challenge API Error:', e)

# 2. Try the sug API (search suggestions/typeahead)
print('\n=== Trying sug API ===')
sug_url = 'https://www.douyin.com/aweme/v1/web/search/sug/?' + urllib.parse.urlencode({
    'keyword': 'AI人工智能',
    'count': '10',
    'device_platform': 'webapp',
    'aid': '6383',
    'version_code': '190600',
})

req2 = urllib.request.Request(sug_url, headers=headers)
try:
    resp2 = urllib.request.urlopen(req2, timeout=15)
    raw2 = resp2.read().decode('utf-8')
    data2 = json.loads(raw2)
    print('Status:', data2.get('status_code'))
    sug_list = data2.get('sug_list', []) or data2.get('data', [])
    print('Sug count:', len(sug_list))
    for s in sug_list[:10]:
        print('  -', s if isinstance(s, str) else s.get('value', ''))
except Exception as e:
    print('Sug API Error:', e)

# 3. Try getting videos from a specific challenge
print('\n=== Trying challenge video list API ===')
# Use the AI相关 challenge
challenge_ids = ['AI', 'ai', '人工智能', 'AI技术', 'chatgpt', '大模型']
for cid in challenge_ids[:2]:
    video_url = 'https://www.douyin.com/aweme/v1/web/challenge/info/?' + urllib.parse.urlencode({
        'challenge_id': cid,
        'device_platform': 'webapp',
        'aid': '6383',
        'version_code': '190600',
    })
    req3 = urllib.request.Request(video_url, headers=headers)
    try:
        resp3 = urllib.request.urlopen(req3, timeout=15)
        raw3 = resp3.read().decode('utf-8')
        data3 = json.loads(raw3)
        print(f'Challenge {cid}: status={data3.get("status_code")}, data={str(data3)[:200]}')
    except Exception as e:
        print(f'Challenge {cid} Error:', e)
    time.sleep(0.5)
