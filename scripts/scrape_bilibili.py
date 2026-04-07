import urllib.request
import urllib.parse
import json
import re
import time

def clean_title(title):
    """Remove HTML tags from title"""
    return re.sub(r'<[^>]+>', '', title)

def search_bilibili(keyword, page=1, page_size=30):
    """Search Bilibili videos by keyword"""
    url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={urllib.parse.quote(keyword)}&order=totalrank&duration=0&page={page}&page_size={page_size}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com",
        "Origin": "https://www.bilibili.com"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('code') == 0:
                return data.get('data', {}).get('result', [])
            else:
                print(f"API error: {data.get('message', 'unknown')}")
                return []
    except Exception as e:
        print(f"Request error: {e}")
        return []

def get_video_details(bvid):
    """Get detailed info for a specific video"""
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.bilibili.com"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('code') == 0:
                d = data.get('data', {})
                return {
                    'aid': d.get('aid'),
                    'bvid': d.get('bvid'),
                    'title': d.get('title', ''),
                    'owner': d.get('owner', {}).get('name', ''),
                    'view': d.get('stat', {}).get('view', '0'),
                    'danmaku': d.get('stat', {}).get('danmaku', '0'),
                    'like': d.get('stat', {}).get('like', '0'),
                    'coin': d.get('stat', {}).get('coin', '0'),
                    'favorite': d.get('stat', {}).get('favorite', '0'),
                    'duration': d.get('duration', 0),
                    'desc': d.get('desc', ''),
                    'tname': d.get('tname', ''),
                    'pubdate': d.get('pubdate', 0)
                }
    except Exception as e:
        print(f"Detail error for {bvid}: {e}")
    return {}

# Keywords to search for AI content
keywords = [
    'AI大模型', '人工智能', 'AI教程', 'ChatGPT', 'AIGC',
    'AI Agent', 'AI智能体', 'LLM', '大模型应用',
    'AI编程', 'AI绘图', '文生图', 'AI工具',
    '机器学习', '深度学习', '神经网络', 'AI技术'
]

all_videos = {}
seen_ids = set()

print(f"Searching Bilibili for AI content across {len(keywords)} keywords...")
for kw in keywords:
    print(f"\nSearching: {kw}")
    results = search_bilibili(kw, page=1, page_size=30)
    print(f"  Got {len(results)} results")
    for r in results:
        bvid = r.get('bvid', '')
        if bvid and bvid not in seen_ids:
            seen_ids.add(bvid)
            all_videos[bvid] = {
                'bvid': bvid,
                'title': clean_title(r.get('title', '')),
                'author': r.get('author', ''),
                'play': r.get('play', '0'),
                'video_duration': r.get('duration', ''),
                'description': clean_title(r.get('description', '')),
                'pubdate': r.get('pubdate', ''),
                'keyword': kw
            }
    time.sleep(0.5)

print(f"\n\nTotal unique videos collected: {len(all_videos)}")
print(f"Top 10 by plays:")
sorted_videos = sorted(all_videos.values(), key=lambda x: int(x.get('play', 0) or 0), reverse=True)
for i, v in enumerate(sorted_videos[:10]):
    print(f"  {i+1}. {v['title'][:50]} | {v['author']} | {v['play']}播放")

# Save raw search data
with open(r'C:\Users\Administrator\.openclaw\workspace\content-hunter\data\bilibili_search_raw.json', 'w', encoding='utf-8') as f:
    json.dump(list(all_videos.values()), f, ensure_ascii=False, indent=2)
print(f"\nSaved {len(all_videos)} videos to bilibili_search_raw.json")
