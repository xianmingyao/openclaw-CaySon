# -*- coding: utf-8 -*-
import urllib.request
import re
import os

url = 'https://item.jd.com/16793098028.html'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.jd.com/'
}

output_dir = r'E:\workspace\downloads\jd_b5440'
os.makedirs(output_dir, exist_ok=True)

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        html = response.read().decode('utf-8', errors='ignore')
        
        # Look for image URLs in various JD formats
        # Pattern 1: n0 (original), n1 (small), etc
        patterns = [
            r'//img\d+\.360buyimg\.com/n0/[^"\'<>]+\.jpg',
            r'//img\d+\.360buyimg\.com/n1/[^"\'<>]+\.jpg',
            r'//img\d+\.360buyimg\.com/n2/[^"\'<>]+\.jpg',
            r'src="//img\d+\.360buyimg\.com/[^"\'<>]+\.jpg"',
            r'data-url="//img\d+\.360buyimg\.com/[^"\'<>]+\.jpg"',
        ]
        
        all_imgs = set()
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for m in matches:
                if 'logo' not in m.lower() and 'banner' not in m.lower():
                    all_imgs.add(m)
        
        print(f'Found {len(all_imgs)} unique images')
        
        # Try to find main product image
        for img in list(all_imgs)[:5]:
            print(f'  {img}')
        
        # Download first few images
        downloaded = []
        for i, img_url in enumerate(list(all_imgs)[:5]):
            if img_url.startswith('//'):
                full_url = 'https:' + img_url
            elif img_url.startswith('src="//'):
                full_url = 'https:' + img_url.replace('src="', '').replace('"', '')
            elif img_url.startswith('data-url="//'):
                full_url = 'https:' + img_url.replace('data-url="', '').replace('"', '')
            else:
                full_url = img_url
                
            try:
                img_req = urllib.request.Request(full_url, headers=headers)
                with urllib.request.urlopen(img_req, timeout=10) as img_resp:
                    img_data = img_resp.read()
                    if len(img_data) > 5000:  # Only save if > 5KB (real image)
                        ext = full_url.split('.')[-1]
                        if len(ext) > 4:
                            ext = 'jpg'
                        filename = f'product_img_{i+1}.{ext}'
                        filepath = os.path.join(output_dir, filename)
                        with open(filepath, 'wb') as f:
                            f.write(img_data)
                        downloaded.append(filename)
                        print(f'Downloaded: {filename} ({len(img_data)} bytes)')
            except Exception as e:
                print(f'Failed: {full_url[:80]}... - {e}')
        
        print(f'\nTotal downloaded: {len(downloaded)} images')
        
except Exception as e:
    print(f'Error: {e}')
