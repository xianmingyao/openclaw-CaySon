#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

headers = {'User-Agent': 'Mozilla/5.0'}

# Search for more projects
projects_to_check = [
    ('narendra', 'vgpt'),
    ('deepseek-ai', 'deepseek-v3'),
    ('01-ai', 'yayi'),
    ('QwenLM', 'qwen3'),
]

for owner, repo in projects_to_check:
    url = f'https://api.github.com/repos/{owner}/{repo}'
    try:
        r = requests.get(url, timeout=10, headers=headers)
        if r.status_code == 200:
            d = r.json()
            print(f'{d["full_name"]}: {d.get("stargazers_count",0)} stars')
            print(f'  Desc: {d.get("description","N/A")[:100]}')
            print()
    except Exception as e:
        print(f'Error {owner}/{repo}: {e}')
