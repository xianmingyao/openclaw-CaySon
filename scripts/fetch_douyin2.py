import requests
import re

url = 'https://v.douyin.com/ks3RmYybKOs/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    r = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
    print('Final URL:', r.url)
    print('Status:', r.status_code)
    
    # Extract video ID
    video_id_match = re.search(r'/video/(\d+)', r.url)
    if video_id_match:
        print('Video ID:', video_id_match.group(1))
    
    # Print first 3000 chars
    print('\n--- Page Content ---')
    print(r.text[:3000])
except Exception as e:
    print('Error:', e)
