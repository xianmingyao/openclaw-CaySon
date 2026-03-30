import requests
import json

# Search for the models mentioned in the video
queries = [
    ("Voxtral TTS", "mistral"),
    ("Uni-1 Luma", "luma-ai"),
    ("DaVinci Magihuman", "video generation"),
    ("TurboQuant Google", "compression"),
    ("Cohere Transcribe", "cohere"),
]

for name, query in queries:
    print(f"\n=== {name} ===")
    try:
        r = requests.get('https://api.github.com/search/repositories', params={
            'q': f'{query}',
            'sort': 'stars',
            'order': 'desc'
        }, timeout=10)
        data = r.json()
        for i in data.get('items', [])[:3]:
            if query.lower() in i['description'].lower() or query.lower() in i['full_name'].lower():
                print(f"  {i['full_name']} [{i['stargazers_count']}]")
                print(f"    {i['description']}")
                print(f"    URL: {i['html_url']}")
    except Exception as e:
        print(f"  Error: {e}")
