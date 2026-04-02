#!/usr/bin/env python3
import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
}

# Try VentureBeat AI section
url = 'https://venturebeat.com/category/ai/'
r = requests.get(url, headers=headers, timeout=10)
print('VB Status:', r.status_code)

# Try to find article links and titles - simplified pattern
links = re.findall(r'href="(https://venturebeat.com/[^"]+)"[^>]*>([^<]+)<', r.text)
print('Found links:', len(links))
for url, title in links[:10]:
    clean = re.sub('<[^>]+>', '', title).strip()
    if clean and len(clean) > 10:
        print('  -', clean[:80])

# Try The Verge
print('\n--- The Verge ---')
url2 = 'https://www.theverge.com/ai-artificial-intelligence'
r2 = requests.get(url2, headers=headers, timeout=10)
print('Status:', r2.status_code)
# Look for article titles in different patterns
titles = re.findall(r'class="[^"]*headline[^"]*"[^>]*>([^<]+)<', r2.text)
for t in titles[:5]:
    clean = re.sub('<[^>]+>', '', t).strip()
    if clean and len(clean) > 10:
        print('  -', clean[:80])
