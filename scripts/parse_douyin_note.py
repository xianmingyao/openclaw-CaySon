import requests
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

note_id = '7629737675951705353'
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
}
url = f'https://www.iesdouyin.com/share/note/{note_id}/'
print('URL:', url)

r = requests.get(url, headers=headers)
text = r.text
print('Page length:', len(text))

# 提取描述
desc_patterns = [
    r'"desc":\s*"([^"]+)"',
    r'"description":\s*"([^"]+)"',
    r'"text":\s*"([^"]+)"',
]
for pattern in desc_patterns:
    matches = re.findall(pattern, text)
    if matches:
        print(f'\nFound via {pattern}:')
        for m in matches[:3]:
            if len(m) > 20:
                print(f'  {m[:300]}')

# 提取图文内容
content_match = re.search(r'"content":\s*"([^"]+)"', text)
if content_match:
    print('\n=== 图文内容 ===')
    print(content_match.group(1)[:500])

# 提取hashtags
hashtags = re.findall(r'#([^"\s]{2,30})', text)
print('\n=== Hashtags ===')
print(list(set(hashtags))[:20])

# 从_RENDER_DATA提取
render_data = re.search(r'window\.__INIT_PROPS__\s*=\s*([^;]+);', text)
if render_data:
    print('\n=== RENDER_DATA ===')
    print(render_data.group(1)[:500])
