import requests
import sys
sys.stdout.reconfigure(encoding='utf-8')

projects = ['chrome-devtools-mcp', 'Claude-Code-Game-Studios', 't3code', 'craft-agents-oss', 'evolver']

headers = {'User-Agent': 'Mozilla/5.0'}
for name in projects:
    r = requests.get(f'https://api.github.com/search/repositories?q={name}', headers=headers, timeout=10)
    if r.status_code == 200:
        data = r.json()
        if data.get('total_count', 0) > 0:
            item = data['items'][0]
            print(f'{name}: {item["stargazers_count"]} stars')
            print(f'  {item["description"]}')
            print(f'  {item["html_url"]}')
            print()
        else:
            print(f'{name}: NOT FOUND')
            print()
    else:
        print(f'{name}: HTTP {r.status_code}')
