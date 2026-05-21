#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

headers = {'User-Agent': 'Mozilla/5.0'}
url = 'https://api.github.com/search/repositories?q=hermes+agent+specialists&sort=stars&per_page=20'
r = requests.get(url, timeout=15, headers=headers)
data = r.json()
for item in data.get('items', [])[:15]:
    print(f'{item["full_name"]}: {item.get("stargazers_count",0)} stars')
    print(f'  URL: {item.get("html_url")}')
    print(f'  Desc: {item.get("description")}')
    print()
