# -*- coding: utf-8 -*-
"""Extract JD product images - last attempt"""
import urllib.request
import re
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

output_dir = r'E:\workspace\downloads\jd_b5440'
os.makedirs(output_dir, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://item.jd.com/',
}

# Try the product page
url = 'https://item.jd.com/16793098028.html'
print(f'Fetching: {url}')

req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

print(f'HTML length: {len(html)}')

# Try multiple image patterns
patterns = [
    # JD mobile images (these are usually product images)
    r'//m\.360buyimg\.com/babel/jfs/t1/\d+/\d+/\d+/\d+/[A-Za-z0-9]+/[a-zA-Z0-9]+\.jpg',
    r'https://m\.360buyimg\.com/babel/jfs/t1/\d+/\d+/\d+/\d+/[A-Za-z0-9]+/[a-zA-Z0-9]+\.jpg',
    # n0, n1, n2 patterns (original, large, small)
    r'//img\d+\.360buyimg\.com/n0/jfs/t1/\d+/\d+/\d+/\d+/[A-Za-z0-9]+/[a-zA-Z0-9]+\.jpg',
    r'//img\d+\.360buyimg\.com/n1/jfs/t1/\d+/\d+/\d+/\d+/[A-Za-z0-9]+/[a-zA-Z0-9]+\.jpg',
    r'//img\d+\.360buyimg\.com/n2/jfs/t1/\d+/\d+/\d+/\d+/[A-Za-z0-9]+/[a-zA-Z0-9]+\.jpg',
]

all_imgs = set()
for pat in patterns:
    matches = re.findall(pat, html)
    for m in matches:
        if 'logo' not in m.lower() and 'banner' not in m.lower() and len(m) < 200:
            if not m.startswith('http'):
                m = 'https:' + m
            all_imgs.add(m)

print(f'\nFound {len(all_imgs)} image URLs')

# Show first 20
for i, img in enumerate(list(all_imgs)[:20]):
    print(f'{i+1}. {img[:100]}')

# Try to download first 5
print('\n--- Downloading ---')
downloaded = []
for i, img_url in enumerate(list(all_imgs)[:8]):
    try:
        req = urllib.request.Request(img_url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://item.jd.com/'
        })
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read()
            size = len(data)
            
            if size < 20000:
                print(f'[SKIP {i+1}] Too small: {size} bytes')
                continue
            
            filename = f'downloaded_{i+1}.jpg'
            with open(os.path.join(output_dir, filename), 'wb') as f:
                f.write(data)
            
            downloaded.append(filename)
            print(f'[OK {i+1}] {filename} ({size//1024}KB)')
    except Exception as e:
        print(f'[FAIL {i+1}] {str(e)[:40]}')

print(f'\nTotal downloaded: {len(downloaded)}')
print(f'Location: {output_dir}')
