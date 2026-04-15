import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

# Search for architecture diagram tools on GitHub
searches = [
    ('mermaid', 'Mermaid diagrams'),
    ('draw.io', 'Draw.io'),
    ('architecture diagram ai', 'AI architecture diagram tools'),
    ('excalidraw', 'Excalidraw'),
]

for query, label in searches:
    url = f"https://github.com/search?q={query.replace(' ', '+')}&type=repositories&s=stars"
    try:
        r = requests.get(url, headers=headers, timeout=15)
        repos = re.findall(r'<h3[^>]*><a[^>]*href="/([^"]+)"[^>]*>([^<]+)</a>', r.text)
        print(f"\n=== {label} ===")
        for repo, name in repos[:3]:
            print(f"  {name} - https://github.com/{repo}")
    except Exception as e:
        print(f"Error: {e}")
