# -*- coding: utf-8 -*-
import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def get_rank(rid=None, type_val=None):
    url = 'https://api.bilibili.com/x/web-interface/ranking/v2?'
    params = []
    if rid:
        params.append(f'rid={rid}')
    if type_val:
        params.append(f'type={type_val}')
    url += '&'.join(params) if params else 'type=all'
    print(f"URL: {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
    return data['data']['list']

# 测试不同分类
print("=== 知识区 (rid=36) ===")
items = get_rank(rid='36')
for i, it in enumerate(items[:15]):
    print(f"{i+1}. {it['title']}")

print()
print("=== 全站 (type=all) ===")
items2 = get_rank()
for i, it in enumerate(items2[:5]):
    print(f"{i+1}. {it['title']}")
