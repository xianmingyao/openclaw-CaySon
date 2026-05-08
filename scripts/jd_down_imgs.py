# -*- coding: utf-8 -*-
"""Download JD Product Images"""
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

# URLs found from JD page (cleaned)
img_urls = [
    'https://m.360buyimg.com/babel/jfs/t1/144093/37/19883/83175/5fe407c2E1b76b792/68ed75dabb686375.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/245477/19/25250/137555/004e5401F967d88df/e8080506451ff133.gif',
    'https://m.360buyimg.com/babel/jfs/t1/120972/34/22737/59798/61f5468aEcfcd30bd/3e4c9f12dac8e80b.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/151220/8/11617/61079/5fdff6baE0a6f9504/2dbfdebc8fd79483.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/142076/21/16719/81798/5fc755a4E765768a0/3e35cebd45e72fcf.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/116864/1/21079/53025/61ff9962E196a5844/c1b0bcc5845ad614.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/160199/26/187/69636/5fea04ceE5abe2994/d12a85889d01cd15.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/160427/8/216/44383/5fea8b3cEa4deb858/fe57a084e88526f3.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/158239/17/80/59624/5fe980daEc6af0098/0b6bcc0f5587720c.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/152823/26/12012/68654/5fe97bc9E430fb6b1/3f7f6bcef1350531.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/144331/15/16230/75371/5fc4e20cEce63f6cb/0148abea8250fc3b.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/154709/15/12170/50231/5fe9a329E1e52a010/370be07713e5124c.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/6851/13/21644/93283/61f50444Eebe6975f/03dee49c7825b83d.png',
    'https://m.360buyimg.com/babel/jfs/t1/94432/11/20795/78385/62012655Ed228f0b7/367cca04c2aa3077.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/87414/17/21797/50526/62010949E99c1a828/71dc7e61d06f9a36.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/155218/21/11512/71383/5fe5532cE2e68cd5a/d6a736a88863c103.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/151690/5/12181/71606/5fe9bf3bE80b775d9/d67be1ff0b8fa2a6.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/153447/39/11074/46465/5fe2e757E465bdd19/a3db919bd4cd1490.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/154590/23/10967/74195/5fe2df62E45a142d9/883e4bda6f5cd278.jpg',
    'https://m.360buyimg.com/babel/jfs/t1/129709/30/17733/53433/5fc20ebaE16d5e08d/bba7d0a8e8e7fb10.jpg',
]

print(f'Downloading {len(img_urls)} images...\n')

downloaded = []
failed = []

for i, url in enumerate(img_urls):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            
            # Skip small files (icons, buttons, etc.)
            if len(data) < 15000:
                print(f'[SKIP {i+1}] Too small ({len(data)} bytes)')
                continue
            
            # Determine extension
            if '.png' in url.lower():
                ext = 'png'
            elif '.gif' in url.lower():
                ext = 'gif'
            else:
                ext = 'jpg'
            
            filename = f'product_{i+1:02d}.{ext}'
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(data)
            
            downloaded.append(filename)
            print(f'[OK {i+1}] {filename} ({len(data)//1024}KB)')
            
    except Exception as e:
        failed.append((i+1, str(e)[:50]))
        print(f'[FAIL {i+1}] {str(e)[:40]}')

print(f'\n=== Result ===')
print(f'Downloaded: {len(downloaded)} images')
print(f'Failed: {len(failed)} images')
print(f'Location: {output_dir}')

# List downloaded files
if downloaded:
    print(f'\nDownloaded files:')
    for f in downloaded:
        print(f'  - {f}')
