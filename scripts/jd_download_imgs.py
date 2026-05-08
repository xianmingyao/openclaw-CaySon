# -*- coding: utf-8 -*-
"""Download JD B5440 Product Images"""
import urllib.request
import re
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

output_dir = r'E:\workspace\downloads\jd_b5440'
os.makedirs(output_dir, exist_ok=True)

# Clean URLs extracted from JD page
raw_urls = [
    "https://img14.360buyimg.com/imagetools/jfs/t1/26577/33/22983/2322/66cc2351F2ef728a4/c0dcf30b31a65169.png",
    "https://img10.360buyimg.com/imagetools/jfs/t1/231301/22/25764/350/66d13f7cF939a0236/582b896f1eefdbc8.png",
    "https://img13.360buyimg.com/imagetools/jfs/t1/78165/1/28972/293/66d13f7bF366459f6/ccc78435369c55f1.png",
    "https://img12.360buyimg.com/imagetools/jfs/t1/90075/15/45774/323/66d13f7dF22e7951a/45d57a26b924d416.png",
    "https://img11.360buyimg.com/imagetools/jfs/t1/237297/11/24156/285/66d13f7dF72f9ce96/895285b6d3152e8c.png",
    "https://img11.360buyimg.com/imagetools/jfs/t1/111399/20/47797/1626/66cecde5Fb4ab8613/931a837d74ace63e.png",
    "https://img12.360buyimg.com/imagetools/jfs/t1/242395/34/16729/259/66d13f7bF0d8cc517/d0b621d6a5d57409.png",
    "https://img13.360buyimg.com/imagetools/jfs/t1/57896/27/28003/327/66d13f7bFfb6b714e/99e43fc125413c2d.png",
    "https://img10.360buyimg.com/imagetools/jfs/t1/49480/29/26553/562/66d13f7eFa1218f0b/b2e47cdae98f0879.png",
    "https://img13.360buyimg.com/imagetools/jfs/t1/236205/4/26259/315/66d13f7bFa6179f46/01e945d3bae87a8d.png",
    "https://img10.360buyimg.com/imagetools/jfs/t1/211722/38/13035/9322/6215e10cEa9918ac1/7f8686ee76e42123.png",
    "https://img13.360buyimg.com/imagetools/jfs/t1/57285/32/26773/372/66d13f7dFd5e7f8fa/c97b8634e410fd2f.png",
    "https://img13.360buyimg.com/imagetools/jfs/t1/89890/2/48950/379/66d13f7eFf9e73676/7183b7ebb5f0f6f7.png",
    "https://img10.360buyimg.com/imagetools/jfs/t1/244153/36/17482/7629/66cc2352F27b6b8b3/f88f5a03278dd6d5.png",
    "https://img11.360buyimg.com/imagetools/jfs/t1/3045/1/25061/4916/66cc2352Fd1520cfc/07606706723455b1.png",
    "https://img14.360buyimg.com/imagetools/jfs/t1/188604/23/47813/2205/66e3b4b9F53e58b3e/5a8b00e7c764a9ba.png",
    "https://img12.360buyimg.com/imagetools/jfs/t1/5590/18/22998/4490/66cc2352Fc05f25b6/f2677cf1a21ef0d4.png",
    "https://img13.360buyimg.com/imagetools/jfs/t1/234786/29/25832/7172/66cc2352F183e6d2e/f96b1f420b0309af.png",
    "https://img10.360buyimg.com/imagetools/jfs/t1/154257/31/33291/1399/66cecde5F91d18706/83c9b2d5c3b9b99a.png",
    "https://img13.360buyimg.com/imagetools/jfs/t1/5483/29/26319/345/66d13f7cFa42c4968/b4e804da707192d9.png",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://item.jd.com/',
}

print(f'Attempting to download {len(raw_urls)} images...\n')

downloaded = []
failed = []

for i, url in enumerate(raw_urls):
    # Clean URL
    url = url.replace('\\/', '/')
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            
            if len(data) < 5000:
                print(f'[SKIP {i+1}] Too small ({len(data)} bytes): {url[-50:]}')
                continue
            
            # Determine extension
            if '.png' in url.lower():
                ext = 'png'
            elif '.gif' in url.lower():
                ext = 'gif'
            else:
                ext = 'jpg'
            
            filename = f'product_img_{i+1:02d}.{ext}'
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(data)
            
            downloaded.append(filename)
            print(f'[OK {i+1}] {filename} ({len(data)} bytes)')
            
    except Exception as e:
        failed.append((i+1, url, str(e)[:50]))
        print(f'[FAIL {i+1}] {str(e)[:50]} - {url[-50:]}')

print(f'\n=== Download Summary ===')
print(f'Success: {len(downloaded)} images')
print(f'Failed: {len(failed)} images')
print(f'Saved to: {output_dir}')

if downloaded:
    print(f'\nDownloaded files:')
    for f in downloaded[:10]:
        print(f'  - {f}')
    if len(downloaded) > 10:
        print(f'  ... and {len(downloaded) - 10} more')
