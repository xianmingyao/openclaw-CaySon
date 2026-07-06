# -*- coding: utf-8 -*-
import urllib.request
import re
import os

url = 'https://item.jd.com/16793098028.html'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
req = urllib.request.Request(url, headers=headers)

output_dir = r'E:\workspace\downloads\jd_b5440'
os.makedirs(output_dir, exist_ok=True)

try:
    with urllib.request.urlopen(req, timeout=15) as response:
        html = response.read().decode('utf-8', errors='ignore')
        
        # Find image URLs (JD uses img\d+.360buyimg.com)
        img_pattern = r'//img\d+\.360buyimg\.com/n\d+/[^<>"\']+\.(jpg|jpeg|png|gif)'
        imgs = re.findall(img_pattern, html)
        
        # Find preview images
        preview_pattern = r'//img\d+\.360buyimg\.com/n0/[^<>"\']+\.(jpg|jpeg|png|gif)'
        previews = re.findall(preview_pattern, html)
        
        print(f'Found {len(imgs)} product images')
        print(f'Found {len(previews)} preview images')
        
        # Download preview images (main product images)
        downloaded = []
        for i, img_url in enumerate(set(previews[:10])):
            full_url = 'https:' + img_url
            try:
                img_req = urllib.request.Request(full_url, headers=headers)
                with urllib.request.urlopen(img_req, timeout=15) as img_resp:
                    img_data = img_resp.read()
                    ext = img_url.split('.')[-1]
                    filename = f'preview_{i+1}.{ext}'
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(img_data)
                    downloaded.append(filename)
                    print(f'Downloaded: {filename}')
            except Exception as e:
                print(f'Failed to download {full_url}: {e}')
        
        print(f'\nTotal downloaded: {len(downloaded)} images')
        print(f'Saved to: {output_dir}')
        
except Exception as e:
    print(f'Error: {e}')
