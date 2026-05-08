# -*- coding: utf-8 -*-
"""JD Product Image Fetcher via API"""
import urllib.request
import json
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

# Try JD image API
api_urls = [
    'https://p.3.cn/prices/mgets?skuIds=J_16793098028&ext=11111111&pin=',
    'https://soft.3.cn/prices/mgets?skuIds=J_16793098028&source=pc',
    'https://item.jd.com/16793098028.html',
]

for url in api_urls:
    print(f'\n=== Fetching: {url[:60]}... ===')
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read().decode('utf-8', errors='ignore')
            print(f'Response length: {len(data)}')
            
            # Look for image URLs
            img_patterns = [
                r'https?://[^"\'<>\s]*360buyimg[^"\'<>\s]*\.(jpg|jpeg|png|gif)',
                r'//img\d+\.360buyimg\.com/[^"\'<>\s]+\.(jpg|jpeg|png)',
                r'"imageUrl"\s*:\s*"([^"]+)"',
                r'"src"\s*:\s*"([^"]*img[^"]+)"',
            ]
            
            found = set()
            for pat in img_patterns:
                matches = re.findall(pat, data)
                for m in matches:
                    if 'logo' not in m.lower() and 'banner' not in m.lower() and len(m) < 500:
                        if m.startswith('//'):
                            m = 'https:' + m
                        found.add(m)
            
            print(f'Found {len(found)} image URLs')
            for i, f in enumerate(list(found)[:15]):
                print(f'{i+1}. {f[:120]}')
    except Exception as e:
        print(f'Error: {e}')

# Try JD search API for this product
print('\n\n=== Trying JD Search ===')
search_url = 'https://search.jd.com/Search?keyword=%E5%85%AC%E7%89%9B%20B5440%20%E6%8F%92%E5%BA%A7&enc=utf-8&qrst=1&rt=1&stop=1&vt=1'
try:
    req = urllib.request.Request(search_url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Find image URLs in search results
        img_pattern = r'//img\d+\.360buyimg\.com/n\d+/[^"\'<>]+\.jpg'
        imgs = re.findall(img_pattern, html)
        
        # Download first 5
        downloaded = 0
        for i, img in enumerate(set(imgs[:10])):
            full_url = 'https:' + img if img.startswith('//') else img
            try:
                img_req = urllib.request.Request(full_url, headers=headers)
                with urllib.request.urlopen(img_req, timeout=8) as img_resp:
                    img_data = img_resp.read()
                    if len(img_data) > 20000:  # Only real images
                        filename = f'search_img_{i+1}.jpg'
                        with open(os.path.join(output_dir, filename), 'wb') as f:
                            f.write(img_data)
                        downloaded += 1
                        print(f'Downloaded: {filename} ({len(img_data)} bytes)')
            except:
                pass
        
        print(f'\nDownloaded {downloaded} images from search')
except Exception as e:
    print(f'Search error: {e}')

print(f'\n\nImages saved to: {output_dir}')
