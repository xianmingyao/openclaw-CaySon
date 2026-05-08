# -*- coding: utf-8 -*-
"""Extract JD images - try escaped URLs"""
import urllib.request
import re
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

output_dir = r'E:\workspace\downloads\jd_b5440'
os.makedirs(output_dir, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://item.jd.com/',
}

url = 'https://item.jd.com/16793098028.html'
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

# Search for any image URLs with 360buyimg
img_matches = re.findall(r'(https?://[^"\'<>\s]*360buyimg[^"\'<>\s]*)', html)
img_matches += re.findall(r'((?:https?://)?(?:m\.)?img\d*\.360buyimg\.com[^"\'<>\s]*)', html)

print(f'Found {len(img_matches)} raw image URLs')

# Clean and deduplicate
clean_imgs = set()
for img in img_matches:
    # Unescape
    img = img.replace('\\/', '/').replace('\\"', '"')
    if len(img) < 250 and ('product' in img.lower() or 'jfs' in img.lower() or 'babel' in img.lower()):
        if not img.startswith('http'):
            img = 'https:' + img
        clean_imgs.add(img)

print(f'Cleaned to {len(clean_imgs)} images')

# Show all
for i, img in enumerate(sorted(clean_imgs)):
    print(f'{i+1}. {img[:120]}')

# Download first 5
print('\n--- Downloading ---')
downloaded = []
for i, img_url in enumerate(list(clean_imgs)[:8]):
    try:
        req = urllib.request.Request(img_url, headers={'Referer': 'https://item.jd.com/'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read()
            if len(data) < 20000:
                print(f'[SKIP {i+1}] Too small: {len(data)}')
                continue
            
            ext = 'jpg'
            if '.png' in img_url.lower(): ext = 'png'
            elif '.gif' in img_url.lower(): ext = 'gif'
            
            filename = f'jd_img_{i+1}.{ext}'
            with open(os.path.join(output_dir, filename), 'wb') as f:
                f.write(data)
            
            downloaded.append(filename)
            print(f'[OK {i+1}] {filename} ({len(data)//1024}KB)')
    except Exception as e:
        print(f'[FAIL {i+1}] {str(e)[:50]}')

print(f'\nDownloaded: {len(downloaded)}')
