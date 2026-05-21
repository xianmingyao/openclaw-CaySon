#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

headers = {'User-Agent': 'Mozilla/5.0'}
# Search for hermes-agent main project
url = 'https://api.github.com/search/repositories?q=hermes+agent&sort=stars&per_page=10'
r = requests.get(url, timeout=15, headers=headers)
data = r.json()
for item in data.get('items', [])[:10]:
    print(f'{item["full_name"]}: {item.get("stargazers_count",0)} stars')
    print(f'  URL: {item.get("html_url")}')
    print(f'  Desc: {item.get("description")}')
    print()
