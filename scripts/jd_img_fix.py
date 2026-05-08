# -*- coding: utf-8 -*-
"""Download JD images - fixed URLs"""
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

# URLs from previous extraction (with fixed format)
urls = [
    'https://m.360buyimg.com/babel/jfs/t20280325/271775/31/10007/27242/67e38079F58005eb1/6d37122c78081a71.png',
    'https://m.360buyimg.com/babel/jfs/t20280325/273776/10/10183/23096/67e38096F54fc1376/77824f6e892b0e37.png',
    'https://m.360buyimg.com/babel/jfs/t20280325/274855/26/10306/22911/67e3810eF61f64f09/a2b7cad75b8a55c3.png',
    'https://img1.360buyimg.com/da/jfs/t1/104009/20/18514/63913/5e94f1a7Ef66e61f6/5c41baf664c71c25.png',
    'https://img1.360buyimg.com/da/jfs/t1/145452/11/32722/25680/638e8de5E724da719/db04e73061486621.jpg',
    'https://img1.360buyimg.com/da/jfs/t1/166214/35/52548/21261/673566bcF2d699506/3cf055832a72ae50.jpg',
    'https://img1.360buyimg.com/da/jfs/t1/189920/37/52041/23631/6735340dFf54bc646/e959f46df93a0ded.jpg',
    'https://img1.360buyimg.com/da/jfs/t1/196523/26/46349/25738/66563c09F7778f810/d12e7ecc41df548b.jpg',
    'https://img1.360buyimg.com/da/jfs/t1/217376/7/46883/39885/67287e4fF5192dfff/f69cb8c3ff2e0605.jpg',
    'https://img1.360buyimg.com/da/jfs/t1/256149/29/28191/57513/67c8c02cFf9718b97/cfe47295fec475c9.jpg',
]

print(f'Downloading {len(urls)} images...\n')

downloaded = []
for i, url in enumerate(urls):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            size = len(data)
            
            if size < 10000:
                print(f'[SKIP {i+1}] Too small: {size} bytes')
                continue
            
            ext = 'png' if '.png' in url.lower() else 'jpg'
            filename = f'product_{i+1:02d}.{ext}'
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(data)
            
            downloaded.append(filename)
            print(f'[OK {i+1}] {filename} ({size//1024}KB)')
    except Exception as e:
        print(f'[FAIL {i+1}] {str(e)[:60]}')

print(f'\n=== Result ===')
print(f'Downloaded: {len(downloaded)} images')
print(f'Location: {output_dir}')

if downloaded:
    print(f'\nFiles:')
    for f in downloaded:
        print(f'  - {f}')
