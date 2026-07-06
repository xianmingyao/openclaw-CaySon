import requests
import re
import json

url = 'https://www.iesdouyin.com/share/video/7631355926130245561/'
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
}
r = requests.get(url, headers=headers)
text = r.text

# 提取标题
title_match = re.search(r'<title>(.*?)</title>', text)
if title_match:
    print('Title:', title_match.group(1))

# 提取meta描述
desc_match = re.search(r'<meta name="description" content="(.*?)"', text)
if desc_match:
    print('Description:', desc_match.group(1))

# 提取__NEXT_DATA__
next_data = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', text)
if next_data:
    print('NEXT_DATA found, length:', len(next_data.group(1)))
    try:
        data = json.loads(next_data.group(1))
        print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
    except:
        print('Failed to parse JSON')
else:
    print('No NEXT_DATA found')
    
# 提取RENDER_DATA
render_data = re.search(r'"RENDER_DATA":"([^"]+)"', text)
if render_data:
    print('RENDER_DATA found')
    import urllib.parse
    decoded = urllib.parse.unquote(render_data.group(1))
    print(decoded[:2000])
