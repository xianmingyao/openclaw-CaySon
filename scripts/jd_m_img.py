# -*- coding: utf-8 -*-
"""Extract and download JD mobile product images"""
import urllib.request
import re
import os
import json
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

output_dir = r'E:\workspace\downloads\jd_b5440'
os.makedirs(output_dir, exist_ok=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

url = 'https://item.m.jd.com/product/16793098028.html'
print(f'Fetching: {url}')

req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

print(f'HTML length: {len(html)}')

# Look for image URLs in various JD mobile formats
patterns = [
    # Direct image URLs
    r'https?://[^"\'<>\s]*m\.360buyimg\.com[^"\'<>\s]*\.(jpg|jpeg|png|gif)',
    r'//m\.360buyimg\.com/[^"\'<>\s]+\.(jpg|jpeg|png|gif)',
    # JSON image data
    r'"imageUrl"\s*:\s*"([^"]+)"',
    r'"src"\s*:\s*"([^"]*360buyimg[^"]+)"',
    r'"uri"\s*:\s*"([^"]+)"',
    r'"mediumImageUrl"\s*:\s*"([^"]+)"',
    r'"smallImageUrl"\s*:\s*"([^"]+)"',
    # Various JD image CDN patterns
    r'//img\d+\.360buyimg\.com/[^"\'<>\s]+\.(jpg|jpeg|png)',
]

found = set()
for pat in patterns:
    matches = re.findall(pat, html)
    for m in matches:
        if 'logo' not in m.lower() and 'banner' not in m.lower() and 'icon' not in m.lower():
            if m.startswith('//'):
                m = 'https:' + m
            if m.startswith('"') and m.endswith('"'):
                m = m.strip('"')
            if len(m) < 300 and 'http' in m:
                found.add(m)

print(f'\nFound {len(found)} unique image URLs')

# Try to download first 10
downloaded = []
for i, img_url in enumerate(list(found)[:10]):
    try:
        req = urllib.request.Request(img_url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://item.m.jd.com/'
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            
            if len(data) < 10000:
                print(f'[SKIP {i+1}] Too small: {len(data)} bytes')
                continue
            
            ext = 'jpg'
            if '.png' in img_url.lower():
                ext = 'png'
            elif '.gif' in img_url.lower():
                ext = 'gif'
            
            filename = f'mobile_img_{i+1:02d}.{ext}'
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(data)
            
            downloaded.append(filename)
            print(f'[OK {i+1}] {filename} ({len(data)//1024}KB)')
            
    except Exception as e:
        print(f'[FAIL {i+1}] {str(e)[:50]}')

print(f'\nDownloaded {len(downloaded)} images')
print(f'Location: {output_dir}')
