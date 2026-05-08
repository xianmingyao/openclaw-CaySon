# -*- coding: utf-8 -*-
import urllib.request
import json
import re
import os

# JD product API - often returns image info
api_urls = [
    'https://p.3.cn/prices/mgets?skuIds=J_16793098028',
    'https://api.m.jd.com/client.action?functionId=pcDetailQuery&skuId=16793098028',
    'https://item.jd.com/ajax/getStoresInfo.aspx?id=16793098028',
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://item.jd.com/',
    'Accept': 'application/json, text/plain, */*',
}

output_dir = r'E:\workspace\downloads\jd_b5440'
os.makedirs(output_dir, exist_ok=True)

# Try to fetch from different sources
for api_url in api_urls:
    print(f'\nTrying: {api_url[:80]}...')
    try:
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read().decode('utf-8', errors='ignore')
            print(f'Response length: {len(data)}')
            if len(data) < 5000:
                print(f'Data: {data[:500]}')
            
            # Look for image URLs
            img_pattern = r'//img\d+\.360buyimg\.com/[^\s"\'<>]+'
            imgs = re.findall(img_pattern, data)
            if imgs:
                print(f'Found {len(imgs)} image URLs')
                for img in imgs[:10]:
                    print(f'  {img}')
    except Exception as e:
        print(f'Error: {e}')

# Also try to fetch the main product page with different approach
print('\n\nTrying main product page with full headers...')
main_url = 'https://item.jd.com/16793098028.html'
try:
    req = urllib.request.Request(main_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
    })
    with urllib.request.urlopen(req, timeout=15) as response:
        html = response.read().decode('utf-8', errors='ignore')
        
        # Try to find image URLs
        patterns = [
            r'"src"\s*:\s*"([^"]*img\d+\.360buyimg[^"]+)"',
            r'"src_n0"\s*:\s*"([^"]+)"',
            r'"imagePath"\s*:\s*"([^"]+)"',
            r'src="([^"]*16793098028[^"]*)"',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html)
            if matches:
                print(f'\nPattern {pattern[:50]}... found {len(matches)} matches:')
                for m in matches[:5]:
                    print(f'  {m[:100]}')
                    
except Exception as e:
    print(f'Error: {e}')
