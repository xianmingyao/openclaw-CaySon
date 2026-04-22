import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 搜索OpenClaw相关Skills
queries = [
    'OpenClaw Skills 剪映 视频剪辑',
    'OpenClaw 电商自动化 小龙虾',
    'claw小龙虾 自动化',
]

for q in queries:
    r = requests.get(f'https://api.github.com/search/repositories?q={q}&sort=stars&per_page=5', 
                     headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    data = r.json()
    print(f'\n=== {q} ===')
    print(f'Found: {data.get("total_count", 0)} repos')
    for item in data.get('items', [])[:3]:
        print(f'  {item["full_name"]}: {item["stargazers_count"]} stars')
        print(f'    {item.get("description", "N/A")}')
