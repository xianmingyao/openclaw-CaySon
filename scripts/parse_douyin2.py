import requests
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://v.douyin.com/cKBtnLl3iAA/'
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
}
r = requests.get(url, headers=headers, allow_redirects=True)
print('Final URL:', r.url)

# 提取视频ID
video_id = re.search(r'/video/(\d+)/', r.url)
if video_id:
    vid = video_id.group(1)
    print('Video ID:', vid)
    
    # 获取页面内容
    page_url = f'https://www.iesdouyin.com/share/video/{vid}/'
    page_r = requests.get(page_url, headers=headers)
    text = page_r.text
    
    # 提取描述
    desc_patterns = [
        r'"desc":\s*"([^"]+)"',
        r'"description":\s*"([^"]+)"',
    ]
    for pattern in desc_patterns:
        desc_match = re.search(pattern, text)
        if desc_match:
            print('\n=== 视频描述 ===')
            print(desc_match.group(1))
            break
    
    # 提取hashtags
    hashtags = re.findall(r'#([^"\s]+)', text)
    unique_hashtags = list(set(hashtags))
    # 过滤掉无关的
    meaningful = [h for h in unique_hashtags if len(h) > 2 and not h.startswith('ff') and not h.startswith('f4')]
    print('\n=== Hashtags ===')
    print(meaningful[:20])
