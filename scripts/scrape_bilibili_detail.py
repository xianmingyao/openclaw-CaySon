import urllib.request
import urllib.parse
import json
import re
import time
import os

def clean_title(title):
    return re.sub(r'<[^>]+>', '', title)

def get_video_detail(bvid):
    """Get detailed info for a specific video"""
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": f"https://www.bilibili.com/video/{bvid}",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('code') == 0:
                d = data.get('data', {})
                stat = d.get('stat', {})
                return {
                    'bvid': bvid,
                    'title': d.get('title', ''),
                    'owner': d.get('owner', {}).get('name', ''),
                    'face': d.get('owner', {}).get('face', ''),
                    'view': stat.get('view', '0'),
                    'danmaku': stat.get('danmaku', '0'),
                    'like': stat.get('like', '0'),
                    'coin': stat.get('coin', '0'),
                    'favorite': stat.get('favorite', '0'),
                    'duration': d.get('duration', 0),
                    'desc': d.get('desc', ''),
                    'tname': d.get('tname', ''),
                    'pubdate': d.get('pubdate', 0),
                    'aid': d.get('aid', 0),
                    'url': f"https://www.bilibili.com/video/{bvid}"
                }
            else:
                return None
    except Exception as e:
        print(f"Error getting detail for {bvid}: {e}")
        return None

# Load search results
data_dir = r'E:\workspace\content-hunter-data\data'
os.makedirs(data_dir, exist_ok=True)

with open(os.path.join(data_dir, 'bilibili_search_raw.json'), 'r', encoding='utf-8') as f:
    videos = json.load(f)

print(f"Loaded {len(videos)} videos from search results")

# Sort by play count and take top 100
sorted_videos = sorted(videos, key=lambda x: int(x.get('play', 0) or 0), reverse=True)
top_videos = sorted_videos[:100]

print(f"Fetching details for top {len(top_videos)} videos...")

# Get details for each video
detailed = []
for i, v in enumerate(top_videos):
    bvid = v['bvid']
    detail = get_video_detail(bvid)
    if detail:
        detail['search_keyword'] = v.get('keyword', '')
        detailed.append(detail)
        if (i+1) % 10 == 0:
            print(f"  Fetched {i+1}/{len(top_videos)} details...")
    else:
        # Fallback to search data if detail fails
        v['url'] = f"https://www.bilibili.com/video/{bvid}"
        v['like'] = '0'
        v['danmaku'] = '0'
        v['coin'] = '0'
        v['favorite'] = '0'
        v['detail_fetched'] = False
        detailed.append(v)
    time.sleep(0.3)

print(f"\nGot detailed data for {len(detailed)} videos")

# Format duration
def fmt_duration(seconds):
    if isinstance(seconds, int):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m}:{s:02d}"
    return str(seconds)

# Build markdown content
lines = []
lines.append("# B站 AI技术热门内容")
lines.append("")
lines.append(f"> 抓取时间：2026-04-07 16:30 | 数据来源：B站搜索 | 关键词：AI大模型/人工智能/AI教程等 | 数量：{len(detailed)}条")
lines.append("")
lines.append("---")
lines.append("")

for i, v in enumerate(detailed):
    duration = fmt_duration(v.get('duration', 0))
    title = v.get('title', v.get('raw_title', ''))
    author = v.get('owner', v.get('author', ''))
    view = v.get('view', '0')
    danmaku = v.get('danmaku', '0')
    like = v.get('like', '0')
    coin = v.get('coin', '0')
    fav = v.get('favorite', '0')
    url = v.get('url', f"https://www.bilibili.com/video/{v.get('bvid', '')}")
    desc = v.get('desc', '')[:200]
    
    lines.append(f"### 第{i+1}条 / Item #{i+1}")
    lines.append(f"- 标题 / Title: {title}")
    lines.append(f"- UP主 / UP: {author}")
    lines.append(f"- 播放 / Views: {view}")
    lines.append(f"- 弹幕 / Danmaku: {danmaku}")
    lines.append(f"- 点赞 / Likes: {like}")
    lines.append(f"- 投币 / Coins: {coin}")
    lines.append(f"- 收藏 / Favs: {fav}")
    lines.append(f"- 时长 / Duration: {duration}")
    lines.append(f"- 话题 / Tags: {v.get('tname', '')} / {v.get('search_keyword', '')}")
    lines.append(f"- 内容总结 / Summary: {desc if desc else '暂无描述'}")
    lines.append(f"- 链接 / URL: {url}")
    lines.append("")

# Write to file (APPEND mode)
output_path = os.path.join(data_dir, 'bilibili.md')
with open(output_path, 'a', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print(f"\nBILIBILI DATA APPENDED to: {output_path}")
print(f"Total records appended: {len(detailed)}")

# Also save detailed data as JSON for reference
detail_path = os.path.join(data_dir, 'bilibili_detail.json')
with open(detail_path, 'w', encoding='utf-8') as f:
    json.dump(detailed, f, ensure_ascii=False, indent=2)
print(f"Detail JSON saved: {detail_path}")
