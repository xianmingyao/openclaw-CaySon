#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

headers = {'User-Agent': 'Mozilla/5.0'}
queries = [
    'hermes 184 specialists',
    'hermes multi agent 184',
    'hermes swarm 184',
]

for q in queries:
    url = f'https://api.github.com/search/repositories?q={requests.utils.quote(q)}&sort=stars&per_page=5'
    try:
        r = requests.get(url, timeout=15, headers=headers)
        if r.status_code == 200:
            data = r.json()
            print(f'\nQuery: {q}')
            for item in data.get('items', [])[:3]:
                print(f'  - {item["full_name"]}: {item.get("description", "N/A")[:80]}')
                print(f'    Stars: {item.get("stargazers_count", 0)} | URL: {item.get("html_url", "N/A")}')
    except Exception as e:
        print(f'Error for {q}: {e}')
