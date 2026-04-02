#!/usr/bin/env python3
import requests
import re
import urllib.parse

# Search for AI agent related content
queries = [
    'trillion AI agents software development',
    'AI agent scale automation software lifecycle',
    'autonomous AI agents software engineering future',
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
}

for query in queries:
    print(f"\n{'='*50}")
    print(f"Query: {query}")
    print('='*50)
    
    # Try Bing international
    url = 'https://www.bing.com/search?q=' + urllib.parse.quote(query)
    try:
        r = requests.get(url, headers=headers, timeout=10)
        # Extract titles
        titles = re.findall(r'<h2[^>]*><a[^>]*>([^<]+)</a>', r.text)
        for t in titles[:5]:
            clean = re.sub('<[^>]+>', '', t)
            if clean.strip():
                print(f"  - {clean.strip()}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Try another source
    url2 = 'https://news.ycombinator.com/search?q=' + urllib.parse.quote(query)
    try:
        r2 = requests.get(url2, headers=headers, timeout=10)
        titles2 = re.findall(r'<a[^>]*class="titlelink"[^>]*>([^<]+)</a>', r2.text)
        for t in titles2[:3]:
            print(f"  [HN] {t.strip()}")
    except Exception as e:
        print(f"  HN Error: {e}")
