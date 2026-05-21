#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

headers = {'User-Agent': 'Mozilla/5.0'}

# Search for openhands and trending projects
projects = [
    ('open-hands', 'openhands'),
    ('All-Hands-AI', 'OpenHands'),
    ('narendra', 'vgpt'),
    ('deepseek', 'deepseek-agent'),
]

for owner, repo in projects:
    url = f'https://api.github.com/repos/{owner}/{repo}'
    try:
        r = requests.get(url, timeout=10, headers=headers)
        if r.status_code == 200:
            d = r.json()
            print(f'{d["full_name"]}: {d.get("stargazers_count",0)} stars')
            print(f'  URL: {d.get("html_url")}')
            print(f'  Desc: {d.get("description","N/A")[:100]}')
            print()
    except:
        pass
