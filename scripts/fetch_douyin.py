import requests
import re

url = 'https://v.douyin.com/qNLdCNgOIs4/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    r = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
    print('Final URL:', r.url)
    print('Status:', r.status_code)
    
    # Try to extract title
    title_match = re.search(r'<title>(.*?)</title>', r.text)
    if title_match:
        print('Title:', title_match.group(1))
    
    # Look for video info
    if 'video' in r.text.lower():
        print('Found video content')
    
    # Print first 2000 chars
    print('\n--- Page Content (first 2000 chars) ---')
    print(r.text[:2000])
except Exception as e:
    print('Error:', e)
