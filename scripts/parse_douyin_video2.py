import requests
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/tZ7t3JYmYME/'
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
}
r = requests.get(url, headers=headers, allow_redirects=True)
print('Final URL:', r.url)

# 提取ID
video_id_match = re.search(r'/video/(\d+)/', r.url)
note_id_match = re.search(r'/note/(\d+)/', r.url)

if video_id_match:
    vid = video_id_match.group(1)
    print('Video ID:', vid)
    page_url = f'https://www.iesdouyin.com/share/video/{vid}/'
elif note_id_match:
    vid = note_id_match.group(1)
    print('Note ID:', vid)
    page_url = f'https://www.iesdouyin.com/share/note/{vid}/'
else:
    print('Could not extract ID')
    page_url = r.url

page_r = requests.get(page_url, headers=headers)
text = page_r.text

# 提取描述
desc_patterns = [
    r'"desc":\s*"([^"]+)"',
    r'"description":\s*"([^"]+)"',
    r'"text":\s*"([^"]+)"',
]
for pattern in desc_patterns:
    matches = re.findall(pattern, text)
    for m in matches:
        if len(m) > 30:
            print('\n=== 视频描述 ===')
            print(m)
            break

# 提取hashtags
hashtags = re.findall(r'#([^"\s]{2,30})', text)
meaningful = [h for h in set(hashtags) if len(h) > 2 and not h.startswith('f')]
if meaningful:
    print('\n=== Hashtags ===')
    print(meaningful[:15])
