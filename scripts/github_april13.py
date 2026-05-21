#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

headers = {'User-Agent': 'Mozilla/5.0'}

# Search GitHub trending - look for projects created around April 13, 2026
# or search for specific keywords from the video
queries = [
    'open-hands agent',
    'vgpt v0',
    'deepseek v3 agent',
    'github trending april 2026',
]

for q in queries:
    url = f'https://api.github.com/search/repositories?q={requests.utils.quote(q)}&sort=stars&per_page=5'
    try:
        r = requests.get(url, timeout=15, headers=headers)
        if r.status_code == 200:
            data = r.json()
            print(f'\nQuery: {q}')
            for item in data.get('items', [])[:3]:
                print(f'  - {item["full_name"]}: {item.get("stargazers_count",0)} stars')
                print(f'    {item.get("html_url")}')
                print(f'    {item.get("description","N/A")[:80]}')
    except Exception as e:
        print(f'Error for {q}: {e}')
