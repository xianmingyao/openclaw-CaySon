import urllib.request
import json

url = 'https://www.douyin.com/aweme/v1/web/hot/search/list/?keyword=AI%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD&count=20&offset=0&device_platform=webapp&aid=6383&channel=channel_pc_web&search_channel=aweme_video_web&enable_history=1&source=normal_search&pc_client_type=1&version_code=190500&version_name=19.5.0&cookie_enabled=true&screen_width=1920&screen_height=1080&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=120.0.0.0'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.douyin.com/',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

req = urllib.request.Request(url, headers=headers)
try:
    resp = urllib.request.urlopen(req, timeout=15)
    data = json.loads(resp.read().decode('utf-8'))
    print(f"Status: {data.get('status_code')}")
    if data.get('status_code') == 0:
        word_list = data.get('data', {}).get('word_list', [])
        print(f"Found {len(word_list)} items")
        for i, item in enumerate(word_list[:5]):
            print(f"  {i+1}. {item.get('word', '')} - hot_value={item.get('hot_value', 0)}")
    else:
        print(f"Error: {data}")
except Exception as e:
    print(f"Error: {e}")
