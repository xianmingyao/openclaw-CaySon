import requests
import re
import json
import urllib.parse
import sys
sys.stdout.reconfigure(encoding='utf-8')

url = 'https://www.iesdouyin.com/share/video/7631355926130245561/'
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
}
r = requests.get(url, headers=headers)
text = r.text

# 查找视频描述
desc_patterns = [
    r'"desc":\s*"([^"]+)"',
    r'"description":\s*"([^"]+)"',
    r'"text":\s*"([^"]+)"',
    r'"title":\s*"([^"]+)"',
]
for pattern in desc_patterns:
    matches = re.findall(pattern, text)
    if matches:
        print(f'\nFound from pattern {pattern}:')
        for m in matches[:5]:
            try:
                print(f'  {m[:300]}')
            except:
                pass

# 从_ROUTER_DATA里提取更多信息
router_data = re.search(r'window\._ROUTER_DATA\s*=\s*(\{.*?\});\s*$', text, re.MULTILINE | re.DOTALL)
if router_data:
    raw = router_data.group(1)
    print(f'\nROUTER_DATA length: {len(raw)}')
    print(f'First 1000 chars: {raw[:1000]}')
    
# 查找subtitle或caption
subtitle = re.search(r'"subtitle":\s*"([^"]+)"', text)
if subtitle:
    print(f'\nSubtitle: {subtitle.group(1)[:500]}')

# 查找hashtag
hashtags = re.findall(r'#([^"\s]+)', text)
if hashtags:
    print(f'\nHashtags found: {hashtags[:20]}')
