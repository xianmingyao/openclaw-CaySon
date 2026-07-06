# -*- coding: utf-8 -*-
"""JD B5440 Product Image Scraper"""
import urllib.request
import re
import os
import ssl

# Skip SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

output_dir = r'E:\workspace\downloads\jd_b5440'
os.makedirs(output_dir, exist_ok=True)

# Try multiple approaches to get product images

# Method 1: Try to get images from the mobile product page
urls_to_try = [
    ('Mobile Page', 'https://item.m.jd.com/product/16793098028.html'),
    ('PC Page', 'https://item.jd.com/16793098028.html'),
    ('Search API', 'https://dd.shop.jd.com/api/detail?skuId=16793098028&source=item_detail'),
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

for name, url in urls_to_try:
    print(f'\n=== Trying {name}: {url[:60]}... ===')
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            print(f'HTML length: {len(html)}')
            
            # Search for image URLs
            patterns = [
                r'https?://[^"\'<>\s]*360buyimg[^"\'<>\s]*\.jpg',
                r'//img\d+\.360buyimg\.com/[^"\'<>\s]+',
                r'"src"\s*:\s*"([^"]+)"',
                r'"imageUrl"\s*:\s*"([^"]+)"',
            ]
            
            found = set()
            for pat in patterns:
                matches = re.findall(pat, html)
                for m in matches:
                    if any(x in m for x in ['n0', 'n1', 'n2', 'img']) and 'logo' not in m.lower():
                        if m.startswith('//'):
                            m = 'https:' + m
                        if m not in found and len(m) < 300:
                            found.add(m)
            
            print(f'Found {len(found)} image URLs')
            for i, f in enumerate(found):
                print(f'{i+1}. {f[:120]}')
    except Exception as e:
        print(f'Error: {e}')

# Method 2: Try to download a known JD product image pattern
print('\n\n=== Trying direct image download ===')
# JD product images often follow patterns like:
# https://img10.360buyimg.com/popSchemas/jfs/t1/xxx.jpg
# https://img14.360buyimg.com/n1/jfs/t1/xxx.jpg

# Try the product directly
img_urls = [
    'https://img10.360buyimg.com/popSchemas/jfs/t1/XXX.jpg',
]

# Let's also try to find images from a search
try:
    search_url = 'https://search.jd.com/Search?keyword=%E5%85%AC%E7%89%9B%20B5440&enc=utf-8'
    req = urllib.request.Request(search_url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f'Search page HTML length: {len(html)}')
        
        # Find image URLs
        img_matches = re.findall(r'//img\d+\.360buyimg\.com/n\d+/[^"\'<>]+\.jpg', html)
        print(f'Found {len(img_matches)} product images from search')
        for i, img in enumerate(set(img_matches[:10])):
            print(f'{i+1}. https:{img}')
except Exception as e:
    print(f'Search error: {e}')

print('\n\n=== Summary ===')
print('JD product pages use dynamic loading, so static scraping is limited.')
print('The best approach is to:')
print('1. Use a logged-in browser session')
print('2. Use the mobile app API')
print('3. Manually download/screenshot the images')
