import requests, re

r = requests.get('https://www.aitop100.cn/assets/aivloglist-afe2276a.js', headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
content = r.text[:8000]
# Search for API endpoints
urls = re.findall(r'[\'"](/api/[^\'"]+|https?://[^\s\'"]+)[\'"]', content)
for u in urls[:20]:
    print(u)
print('---')
calls = re.findall(r'(?:fetch|axios\.get|request|get)\([\'"]([^\'"]+)[\'"]', content)
for c in calls[:10]:
    print('call:', c)
