# -*- coding: utf-8 -*-
"""Download all JD product images from opencli URLs"""
import urllib.request
import re
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

output_dir = r'E:\workspace\downloads\jd_b5440'
os.makedirs(output_dir, exist_ok=True)

# All AVIF image URLs from opencli jd item
avif_urls = [
    "https://img10.360buyimg.com/pcpubliccms/s228x228_jfs/t1/431120/35/7726/114808/69fcda3eF578005b2/0083320320370ab9.jpg.avif",
    "https://img10.360buyimg.com/pcpubliccms/s228x228_jfs/t1/289066/38/17547/47714/68b7a9e1F077999b9/bda2e6fb92bf15d6.jpg.avif",
    "https://img10.360buyimg.com/pcpubliccms/s228x228_jfs/t1/325368/16/15219/28312/68b7a9e2F47f11792/e251ae892f6052d0.jpg.avif",
    "https://img10.360buyimg.com/pcpubliccms/s228x228_jfs/t1/324086/30/10653/26667/68ac0765Fc6909372/78b47036058d1035.jpg.avif",
    "https://img10.360buyimg.com/pcpubliccms/s228x228_jfs/t1/334200/11/8397/32345/68b7a9e3F6055c0f4/92d504e465b473c0.jpg.avif",
    "https://img10.360buyimg.com/pcpubliccms/s228x228_jfs/t1/289923/39/14071/27147/68b7a9e4Fd27770d0/b84b3f12dc9ddba9.jpg.avif",
    "https://img10.360buyimg.com/pcpubliccms/s228x228_jfs/t1/329224/25/8349/14481/68b7a9f5F2dacc59a/a2b5772ffd41b743.jpg.avif",
    "https://img10.360buyimg.com/pcpubliccms/s228x228_jfs/t1/348364/12/847/18025/68be36adF649d07ae/37bd35eac821f52b.jpg.avif",
    "https://img10.360buyimg.com/pcpubliccms/s228x228_jfs/t1/286864/34/19523/15494/68be36aeF3c44c415/86f735eaa4c0a0b9.jpg.avif",
    "https://img10.360buyimg.com/pcpubliccms/s228x228_jfs/t1/338253/12/8302/18326/68be36aeF78f7476d/deb51985dda64a57.jpg.avif",
    # This one has larger size
    "https://img10.360buyimg.com/pcpubliccms/s1440x1440_jfs/t1/325368/16/15219/28312/68b7a9e2F47f11792/e251ae892f6052d0.jpg",
]

# s48x48 URLs - these are small icons, skip them
# s1440x1440 is the largest size available

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://item.jd.com/',
}

print(f'Processing {len(avif_urls)} images...\n')

# Convert AVIF URLs to larger JPG URLs
def convert_to_large_jpg(avif_url):
    # s228x228 -> s800x800 for larger images
    url = avif_url.replace('s228x228', 's800x800')
    url = url.replace('.jpg.avif', '.jpg')
    return url

downloaded = []
failed = []

for i, avif_url in enumerate(avif_urls):
    # Try larger version first
    large_url = convert_to_large_jpg(avif_url)
    
    try:
        req = urllib.request.Request(large_url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read()
            size = len(data)
            
            if size < 10000:
                raise Exception(f"Too small: {size}")
            
            filename = f'b5440_{i+1:02d}.jpg'
            with open(os.path.join(output_dir, filename), 'wb') as f:
                f.write(data)
            
            downloaded.append(filename)
            print(f'[OK {i+1}] {filename} ({size//1024}KB)')
            
    except Exception as e:
        # Try original AVIF
        try:
            req = urllib.request.Request(avif_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = resp.read()
                size = len(data)
                
                if size > 10000:
                    filename = f'b5440_{i+1:02d}.avif'
                    with open(os.path.join(output_dir, filename), 'wb') as f:
                        f.write(data)
                    downloaded.append(filename)
                    print(f'[OK {i+1}] {filename} ({size//1024}KB) - AVIF')
                    continue
        except:
            pass
        
        failed.append((i+1, str(e)[:40]))
        print(f'[FAIL {i+1}] {str(e)[:40]}')

print(f'\n=== Result ===')
print(f'Downloaded: {len(downloaded)} images')
print(f'Failed: {len(failed)} images')
print(f'Location: {output_dir}')

# List files
files = os.listdir(output_dir)
print(f'\nTotal files in directory: {len(files)}')
