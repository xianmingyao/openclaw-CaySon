#!/usr/bin/env python3
import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
}

# Get more headlines from VentureBeat about AI agents
print('=== VentureBeat AI Agents Headlines ===')
url = 'https://venturebeat.com/category/ai/'
r = requests.get(url, headers=headers, timeout=10)

text = re.sub(r'<script[^>]*>.*?</script>', '', r.text, flags=re.DOTALL)
text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)

h2s = re.findall(r'<h2[^>]*>(.*?)</h2>', text, flags=re.DOTALL)
for h in h2s[:15]:
    clean = re.sub('&#[xX][0-9a-fA-F]+;', '', h)
    clean = re.sub('<[^>]+>', '', clean).strip()
    if len(clean) > 15:
        print(f'  - {clean}')

# Also check for specific AI agent content
print('\n=== Ars Technica AI ===')
url2 = 'https://arstechnica.com/ai/'
r2 = requests.get(url2, headers=headers, timeout=10)

text2 = re.sub(r'<script[^>]*>.*?</script>', '', r2.text, flags=re.DOTALL)
text2 = re.sub(r'<style[^>]*>.*?</style>', '', text2, flags=re.DOTALL)

h2s2 = re.findall(r'<h2[^>]*>(.*?)</h2>', text2, flags=re.DOTALL)
for h in h2s2[:10]:
    clean = re.sub('&#[xX][0-9a-fA-F]+;', '', h)
    clean = re.sub('<[^>]+>', '', clean).strip()
    if len(clean) > 15:
        print(f'  - {clean}')

# Search for agent-related articles
print('\n=== Related Search: AI Agent Scale ===')
url3 = 'https://www.bing.com/search?q=AI+agent+trillion+scale+software+development'
r3 = requests.get(url3, headers=headers, timeout=10)
# Extract snippet-like content
snippets = re.findall(r'<p[^>]*>([^<]{50,})</p>', r3.text)
for s in snippets[:5]:
    clean = re.sub('<[^>]+>', '', s).strip()
    if clean:
        print(f'  - {clean[:150]}...')
