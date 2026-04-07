import json

with open(r'C:\Users\Administrator\.openclaw\workspace\content-hunter\data\bilibili_search_raw.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'Total: {len(data)} videos')
for i, v in enumerate(data[:10]):
    print(f'{i+1}. {v["title"][:60]} | {v["author"]} | {v["play"]}播放 | kw:{v["keyword"]}')
