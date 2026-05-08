# -*- coding: utf-8 -*-
"""Download JD product images from opencli URLs"""
import urllib.request
import re
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

output_dir = r'E:\workspace\downloads\jd_b5440'
os.makedirs(output_dir, exist_ok=True)

# AVIF images from opencli jd item command
avif_urls = [
    "https://img10.360buyimg.com/pcpubliccms/s228x228_jfs/t1/431120/35/7726/114808/69fcda3eF578005b2/0083320320370ab9.jpg.avif",
    "https://img10.360buyimg.com/pcpubliccms/s228x228_jfs/t1/289066/38/17547/47714/68b7a9e1F077999b9/bda2e6fb92bf15d6.jpg.avif",
    "https://img10.360buyimg.com/pcpubliccms/s228x228_jfs/t1/325368/16/15219/28312/68b7a9e2F47f11792/e251ae892f6052d0.jpg.avif",
    "https://img10.360buyimg.com/pcpubliccms/s228x228_jfs/t1/324086/30/10653/26667/68ac0765Fc6909372/78b47036058d1035.jpg.avif",
    "https://img10.360buyimg.com/pcpubliccms/s228x228_jfs/t1/334200/11/8397/32345/68b7a9e3F6055c0f4/92d504e465b473c0.jpg.avif",
]

# Try to get larger versions - replace s228x228 with s800x800 or n1
larger_urls = []
for url in avif_urls:
    # Replace size prefix to get larger images
    larger_url = re.sub(r's228x228', 's800x800', url)
    larger_url = larger_url.replace('.jpg.avif', '.jpg')
    larger_urls.append(larger_url)

print(f'Downloading {len(larger_urls)} larger images...\n')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://item.jd.com/',
}

downloaded = []
for i, url in enumerate(larger_urls):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            size = len(data)
            
            if size < 10000:
                print(f'[SKIP {i+1}] Too small: {size} bytes')
                # Try original AVIF
                try:
                    req = urllib.request.Request(avif_urls[i], headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        data = resp.read()
                        size = len(data)
                        if size > 10000:
                            filename = f'product_{i+1:02d}.avif'
                            with open(os.path.join(output_dir, filename), 'wb') as f:
                                f.write(data)
                            downloaded.append(filename)
                            print(f'[OK {i+1}] {filename} ({size//1024}KB) - AVIF format')
                            continue
                except:
                    pass
                continue
            
            filename = f'product_{i+1:02d}.jpg'
            with open(os.path.join(output_dir, filename), 'wb') as f:
                f.write(data)
            
            downloaded.append(filename)
            print(f'[OK {i+1}] {filename} ({size//1024}KB)')
            
    except Exception as e:
        print(f'[FAIL {i+1}] {str(e)[:50]}')

print(f'\n=== Result ===')
print(f'Downloaded: {len(downloaded)} images')
print(f'Location: {output_dir}')
