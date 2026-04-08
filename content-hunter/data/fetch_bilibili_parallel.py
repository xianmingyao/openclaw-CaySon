import subprocess
import json
import concurrent.futures
import sys

# All BVIDs collected from search
bvids = [
    # AI人工智能 tutorials
    "BV1ZC9FBhE5U", "BV1KXf1BDEcV", "BV1x8zvYmE7G", "BV1mPq8BQEJF", "BV1wCPmzPEmr",
    # ChatGPT tutorials  
    "BV1Yus6exEoQ", "BV1Cb48eSEY6", "BV1C5HJzcEVz", "BV1gJgqzhEzk", "BV1wE8jzgE7T",
    "BV1DPt7zDEHo", "BV1aqwgeLEwe", "BV1Z54ZzGEDb", "BV1xE421M774", "BV1z1NXeDEpU",
    # More AI
    "BV1eqBMBCERb", "BV1VVfvBqEjz", "BV1X8DvBjEQ1", "BV1RBf4B7EaP",
    # Additional from other searches
    "BV1DWf5BuEhJ",
]

def fetch_video(bvid):
    url = f"https://www.bilibili.com/video/{bvid}"
    try:
        result = subprocess.run(
            ['yt-dlp', '--dump-json', '--no-download', '--socket-timeout', '60', url],
            capture_output=True, text=True, timeout=90
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            return {
                'title': data.get('title', ''),
                'author': data.get('uploader', ''),
                'bvid': bvid,
                'view': data.get('view_count', 0),
                'like': data.get('like_count', 0),
                'coin': data.get('coin_count', 0),
                'favorite': data.get('favorite_count', 0),
                'share': data.get('share_count', 0),
                'danmaku': data.get('comment_count', 0),
                'duration': data.get('duration', 0),
                'description': data.get('description', '')[:300],
                'tags': data.get('tags', [])[:10] if isinstance(data.get('tags'), list) else [],
                'upload_date': data.get('upload_date', ''),
                'url': url
            }
    except Exception as e:
        return {'bvid': bvid, 'error': str(e)}
    return None

print(f"Fetching {len(bvids)} videos...")
results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    future_to_bvid = {executor.submit(fetch_video, bvid): bvid for bvid in bvids}
    for i, future in enumerate(concurrent.futures.as_completed(future_to_bvid)):
        bvid = future_to_bvid[future]
        try:
            result = future.result()
            if result and 'error' not in result:
                results.append(result)
                print(f"[{i+1}/{len(bvids)}] OK: {result['title'][:40]}")
            elif result and 'error' in result:
                print(f"[{i+1}/{len(bvids)}] FAIL: {bvid} - {result['error'][:50]}")
            else:
                print(f"[{i+1}/{len(bvids)}] SKIP: {bvid}")
        except Exception as e:
            print(f"[{i+1}/{len(bvids)}] ERROR: {bvid} - {e}")

print(f"\n=== Total successful: {len(results)} ===")

# Deduplicate by bvid
seen = set()
unique = []
for v in results:
    if v.get('bvid') not in seen:
        seen.add(v.get('bvid'))
        unique.append(v)

print(f"=== Unique: {len(unique)} ===")

with open('E:/workspace/content-hunter/data/bilibili_ai_all.json', 'w', encoding='utf-8') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)
print("Saved to bilibili_ai_all.json")

# Also save to markdown format
with open('E:/workspace/content-hunter/data/bilibili.md', 'w', encoding='utf-8') as f:
    f.write("# B站 AI技术热门内容\n\n")
    f.write(f"抓取时间: 2026-04-08\n\n")
    f.write(f"共 {len(unique)} 条内容\n\n---\n\n")
    for i, v in enumerate(unique, 1):
        f.write(f"### 第{i}条\n")
        f.write(f"- 标题: {v.get('title', 'N/A')}\n")
        f.write(f"- UP主: {v.get('author', 'N/A')}\n")
        f.write(f"- 播放: {v.get('view', 0)}\n")
        f.write(f"- 点赞: {v.get('like', 0)}\n")
        f.write(f"- 投币: {v.get('coin', 0)}\n")
        f.write(f"- 收藏: {v.get('favorite', 0)}\n")
        f.write(f"- 弹幕: {v.get('danmaku', 0)}\n")
        tags = v.get('tags', [])
        if tags:
            f.write(f"- 话题: {' '.join(['#'+t for t in tags[:5]])}\n")
        f.write(f"- 内容总结: {v.get('description', '')[:200]}...\n")
        f.write(f"- 链接: {v.get('url', '')}\n\n")

print("Saved markdown to bilibili.md")
