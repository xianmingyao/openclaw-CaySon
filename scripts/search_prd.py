#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

headers = {'User-Agent': 'Mozilla/5.0'}
queries = [
    'prd write skill product manager',
    'prd-write skill claude code',
    'product manager prd github',
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
                print(f'    URL: {item.get("html_url")}')
                print(f'    Desc: {item.get("description", "N/A")[:100]}')
    except Exception as e:
        print(f'Error for {q}: {e}')
