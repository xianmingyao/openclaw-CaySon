import urllib.request
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# 搜索5月的AI新闻
url = 'https://news.google.com/rss/search?q=AI+May+2025&hl=en-US&gl=US&ceid=US:en'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    resp = urllib.request.urlopen(req, context=ctx, timeout=15)
    content = resp.read().decode('utf-8', errors='ignore')
    items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
    for item in items[:15]:
        title = re.search(r'<title>(.*?)</title>', item)
        pubdate = re.search(r'<pubDate>(.*?)</pubDate>', item)
        if title and ('Gemini' in title.group(1) or 'Sakana' in title.group(1) or 'MiniCPM' in title.group(1) or 'Veo' in title.group(1) or 'Thinking Machines' in title.group(1)):
            print(f"{pubdate.group(1) if pubdate else 'No date'}: {title.group(1)}")
except Exception as e:
    print(f'Error: {e}')
