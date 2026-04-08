import requests
import json

# Try Bilibili trending API
url = 'https://api.bilibili.com/x/web-interface/ranking/v2'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.bilibili.com'
}

try:
    resp = requests.get(url, headers=headers, timeout=10)
    print(f'Status: {resp.status_code}')
    data = resp.json()
    print(f'Code: {data.get("code")}')
    if data.get('data'):
        print(f'Number of videos: {len(data["data"]["list"])}')
        # Filter for AI related
        ai_keywords = ['AI', '人工智能', 'ChatGPT', 'GPT', '机器学习', '深度学习', '神经网络']
        ai_videos = []
        all_videos = []
        for v in data['data']['list']:
            title = v.get('title', '')
            stat = v.get('stat', {})
            video_info = {
                'title': title,
                'author': v.get('owner', {}).get('name', ''),
                'aid': v.get('aid'),
                'bvid': v.get('bvid'),
                'play': stat.get('view', 0),
                'like': stat.get('like', 0),
                'duration': v.get('duration', 0)
            }
            all_videos.append(video_info)
            if any(kw in title for kw in ai_keywords):
                ai_videos.append(video_info)
        
        print(f'AI related videos in trending: {len(ai_videos)}')
        for v in ai_videos[:5]:
            print(f"  - {v['title']} by {v['author']} | Play: {v['play']}")
        
        # Save all videos for reference
        with open('E:/workspace/content-hunter/data/bilibili_all_trending.json', 'w', encoding='utf-8') as f:
            json.dump(all_videos, f, ensure_ascii=False, indent=2)
        print(f'Saved {len(all_videos)} trending videos')
        
except Exception as e:
    print(f'Error: {e}')
