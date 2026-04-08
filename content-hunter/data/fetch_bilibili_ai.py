import subprocess
import json
import re

bvids = [
    "BV1ZC9FBhE5U",
    "BV1KXf1BDEcV", 
    "BV1x8zvYmE7G",
    "BV1mPq8BQEJF",
    "BV1wCPmzPEmr",
    "BV1DWf5BuEhJ",
    "BV1eqBMBCERb",
    "BV1VVfvBqEjz",
    "BV1X8DvBjEQ1",
    "BV1RBf4B7EaP"
]

results = []

for bvid in bvids:
    url = f"https://www.bilibili.com/video/{bvid}"
    print(f"\nFetching: {bvid}")
    try:
        # Use yt-dlp to get JSON info
        result = subprocess.run([
            'yt-dlp', '--dump-json', '--no-download', url
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            info = {
                'title': data.get('title', ''),
                'author': data.get('uploader', ''),
                'bvid': bvid,
                'aid': data.get('id', ''),
                'view': data.get('view_count', 0),
                'like': data.get('like_count', 0),
                'coin': data.get('coin_count', 0),
                'favorite': data.get('favorite_count', 0),
                'share': data.get('share_count', 0),
                'danmaku': data.get('comment_count', 0),
                'duration': data.get('duration', 0),
                'description': data.get('description', '')[:300],
                'tags': data.get('tags', [])[:10],
                'upload_date': data.get('upload_date', ''),
                'url': url
            }
            results.append(info)
            print(f"  Title: {info['title'][:50]}")
            print(f"  Author: {info['author']}")
            print(f"  Views: {info['view']}, Likes: {info['like']}")
        else:
            print(f"  Error: {result.stderr[:200] if result.stderr else 'No output'}")
    except Exception as e:
        print(f"  Exception: {e}")

print(f"\n\n=== Total videos fetched: {len(results)} ===")

# Save results
with open('E:/workspace/content-hunter/data/bilibili_ai_batch1.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("Saved to bilibili_ai_batch1.json")
