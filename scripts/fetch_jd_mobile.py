# -*- coding: utf-8 -*-
import urllib.request
import re
import json
import os

url = 'https://item.m.jd.com/product/16793098028.html'
headers = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

output_dir = r'E:\workspace\downloads\jd_b5440'
os.makedirs(output_dir, exist_ok=True)

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        html = response.read().decode('utf-8', errors='ignore')
        
        print(f'HTML length: {len(html)}')
        
        # Look for image URLs in various patterns
        # JD mobile uses image URLs like: //img10.360buyimg.com/n1/s546x546_jfs/...
        patterns = [
            r'//img\d+\.360buyimg\.com/n\d+/[^"\'<>\s]+\.jpg',
            r'//img\d+\.360buyimg\.com/n\d+/[^"\'<>\s]+\.jpeg',
            r'"imageUrl"\s*:\s*"([^"]+)"',
            r'"src"\s*:\s*"([^"]*360buyimg[^"]+)"',
            r'"uri"\s*:\s*"([^"]+)"',
            r'"mediumImageUrl"\s*:\s*"([^"]+)"',
            r'"smallImageUrl"\s*:\s*"([^"]+)"',
        ]
        
        all_urls = set()
        for pattern in patterns:
            matches = re.findall(pattern, html)
            for m in matches:
                if 'logo' not in m.lower() and 'banner' not in m.lower():
                    if m not in all_urls:
                        all_urls.add(m)
                        print(f'Found: {m[:100]}')
        
        print(f'\nTotal unique URLs: {len(all_urls)}')
        
        # Download first few images
        downloaded = []
        for i, img_url in enumerate(list(all_urls)[:5]):
            if img_url.startswith('//'):
                full_url = 'https:' + img_url
            elif not img_url.startswith('http'):
                full_url = 'https://' + img_url
            else:
                full_url = img_url
                
            try:
                img_req = urllib.request.Request(full_url, headers=headers)
                with urllib.request.urlopen(img_req, timeout=10) as img_resp:
                    img_data = img_resp.read()
                    if len(img_data) > 10000:  # Only save if > 10KB
                        filename = f'jd_img_{i+1}.jpg'
                        filepath = os.path.join(output_dir, filename)
                        with open(filepath, 'wb') as f:
                            f.write(img_data)
                        downloaded.append(filename)
                        print(f'Downloaded: {filename} ({len(img_data)} bytes)')
            except Exception as e:
                print(f'Failed: {full_url[:80]} - {e}')
        
        print(f'\nTotal downloaded: {len(downloaded)} images')
        
except Exception as e:
    print(f'Error: {e}')
