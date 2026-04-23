import requests
r = requests.get('https://v.douyin.com/T7oHIOn9Rwo/', allow_redirects=True, timeout=10)
print('URL:', r.url)
