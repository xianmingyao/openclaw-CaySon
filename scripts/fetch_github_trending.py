import requests
import json

# Search for trending AI/Agent projects
queries = [
    'openclaw AI agent',
    'claude-code assistant',
    'AI agent memory',
    'weekly github trending 2026'
]

for q in queries:
    r = requests.get('https://api.github.com/search/repositories', params={
        'q': q,
        'sort': 'stars',
        'order': 'desc',
        'per_page': 3
    }, headers={'Accept': 'application/vnd.github.v3+json'})
    
    if r.status_code == 200:
        print(f"\n=== {q} ===")
        for i in r.json().get('items', [])[:3]:
            print(f"  {i['full_name']} [{i['stargazers_count']}]")
            desc = i.get('description', '')
            if desc:
                print(f"    {desc[:100]}")
    else:
        print(f"\n=== {q} === Rate limited or error: {r.status_code}")
