import requests
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0'}
skills = ['capcut-video-editor', 'free-ai-video-editing', 'capcut-ai-video-editor']

for s in skills:
    print(f'\n=== {s} ===')
    r = requests.get(f'https://clawhub.ai/skills/{s}', headers=headers, timeout=10)
    title = re.search(r'<title>(.*?)</title>', r.text)
    desc = re.search(r'meta name="description" content="(.*?)"', r.text)
    if title:
        print(f'Title: {title.group(1)}')
    if desc:
        print(f'Desc: {desc.group(1)[:200]}')
