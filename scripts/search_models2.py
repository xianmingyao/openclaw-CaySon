import requests
import json

# More specific searches
queries = [
    ("Voxtral TTS", "voxtral"),
    ("Uni-1 Luma", "luma photon"),
    ("DaVinci Magihuman", "magihuman"),
    ("Cohere Transcribe", "cohere-transcribe"),
    ("TurboQuant", "turboquant google"),
]

headers = {"Accept": "application/vnd.github.v3+json"}

for name, query in queries:
    print(f"\n=== {name} ===")
    try:
        r = requests.get('https://api.github.com/search/repositories', 
            params={'q': query, 'sort': 'stars', 'per_page': 3},
            headers=headers, timeout=15)
        data = r.json()
        for i in data.get('items', [])[:2]:
            stars = i['stargazers_count']
            desc = i['description'] or ""
            # Skip if description is unrelated
            print(f"  {i['full_name']} [stars:{stars}]")
            print(f"    {desc[:100]}")
            print(f"    {i['html_url']}")
    except Exception as e:
        print(f"  Error: {e}")
