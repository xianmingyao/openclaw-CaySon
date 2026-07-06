import requests
import re

# Search for OpenCode+Skill video
search_url = "https://www.douyin.com/search/OpenCode+Skill"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    r = requests.get(search_url, headers=headers, timeout=10)
    print('Status:', r.status_code)
    print('URL:', r.url)
    
    # Look for video links
    video_ids = re.findall(r'/video/(\d+)', r.text)
    print('Video IDs found:', set(video_ids)[:5])
except Exception as e:
    print('Error:', e)
