import requests

# Search supermemory
print("=== Supermemory 相关项目 ===")
r = requests.get('https://api.github.com/search/repositories', params={
    'q': 'supermemory AI memory',
    'sort': 'stars',
    'order': 'desc'
})
data = r.json()
for i in data['items'][:3]:
    print(f"{i['full_name']} [{i['stargazers_count']}]")
    print(f"  {i['description']}")
    print()

# Search lancedb memory
print("\n=== LanceDB Memory 相关项目 ===")
r2 = requests.get('https://api.github.com/search/repositories', params={
    'q': 'lancedb memory vector AI',
    'sort': 'stars',
    'order': 'desc'
})
data2 = r2.json()
for i in data2['items'][:3]:
    print(f"{i['full_name']} [{i['stargazers_count']}]")
    print(f"  {i['description']}")
    print()
