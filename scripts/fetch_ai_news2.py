#!/usr/bin/env python3
import requests
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml',
}

# Try to get content from various AI news sources
sources = [
    ('VentureBeat AI', 'https://venturebeat.com/category/ai/'),
    ('The Verge AI', 'https://www.theverge.com/ai-artificial-intelligence'),
    ('Ars Technica AI', 'https://arstechnica.com/ai/'),
    ('MIT Tech Review AI', 'https://www.technologyreview.com/topic/artificial-intelligence/'),
]

for name, url in sources:
    print(f'\n=== {name} ===')
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f'Status: {r.status_code}, Length: {len(r.text)}')
        
        # Try to extract meaningful text
        # Remove scripts and styles
        text = re.sub(r'<script[^>]*>.*?</script>', '', r.text, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        
        # Find all headings
        h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', text, flags=re.DOTALL)
        for h in h2s[:5]:
            clean = re.sub('<[^>]+>', '', h).strip()
            if len(clean) > 15:
                print(f'  [H2] {clean[:100]}')
        
        # Find paragraphs
        ps = re.findall(r'<p[^>]*>(.*?)</p>', text, flags=re.DOTALL)
        for p in ps[:3]:
            clean = re.sub('<[^>]+>', '', p).strip()
            if len(clean) > 50:
                print(f'  [P] {clean[:100]}')
                break
        
    except Exception as e:
        print(f'Error: {e}')
