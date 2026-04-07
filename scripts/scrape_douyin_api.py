import urllib.request
import urllib.parse
import json
import re
import time
import os

def search_douyin(keyword, offset=0, count=20):
    """Search Douyin videos via web API"""
    url = f"https://www.douyin.com/aweme/v1/web/general/search/single/?keyword={urllib.parse.quote(keyword)}&search_source=normal_search&query_correct_type=1&is_filter_search=0&from_group_id=&offset={offset}&count={count}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com",
        "Cookie": ""
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('status_code') == 0:
                return data.get('data', [])
            else:
                print(f"Douyin API error: {data.get('status_msg', 'unknown')}")
                return []
    except Exception as e:
        print(f"Request error: {e}")
        return []

def get_video_detail(aid):
    """Get video detail from Douyin"""
    url = f"https://www.iesdouyin.com/share/video/{aid}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8')
            # Try to extract JSON data from HTML
            match = re.search(r'window\._ROUTER_DATA\s*=\s*(\{.*?\});', html, re.DOTALL)
            if match:
                return json.loads(match.group(1))
    except Exception as e:
        print(f"Detail error for {aid}: {e}")
    return {}

keywords = [
    'AI人工智能', 'ChatGPT', 'AI大模型', 'AI工具', 'AIGC',
    'LLM大模型', 'AI教程', 'AI应用', 'AI科技', 'AI智能',
    'GPT教程', 'AI绘图', '文生图', 'AI Agent', 'AI智能体'
]

all_videos = {}
seen_ids = set()

print(f"Searching Douyin for AI content...")
for kw in keywords:
    print(f"\nSearching: {kw}")
    for offset in [0, 20, 40]:
        results = search_douyin(kw, offset=offset, count=20)
        print(f"  offset={offset}: got {len(results)} results")
        for r in results:
            aid = r.get('aweme_id', '')
            if aid and aid not in seen_ids:
                seen_ids.add(aid)
                desc = r.get('desc', '')
                author = r.get('author', {}).get('nickname', '') if isinstance(r.get('author'), dict) else str(r.get('author', ''))
                digg_count = r.get('statistics', {}).get('digg_count', '0') if isinstance(r.get('statistics'), dict) else '0'
                all_videos[aid] = {
                    'aid': aid,
                    'title': desc,
                    'author': author,
                    'digg_count': digg_count,
                    'keyword': kw,
                    'url': f"https://www.douyin.com/video/{aid}"
                }
        time.sleep(1)

print(f"\nTotal unique Douyin videos: {len(all_videos)}")

# Sort by digg_count (likes) and take top 100
sorted_videos = sorted(all_videos.values(), key=lambda x: int(x.get('digg_count', 0) or 0), reverse=True)
top_100 = sorted_videos[:100]

# Build markdown content
lines = []
lines.append("# 抖音 AI技术热门内容")
lines.append("")
lines.append(f"> 抓取时间：2026-04-07 16:30 | 数据来源：抖音搜索 | 关键词：AI人工智能/ChatGPT等 | 数量：{len(top_100)}条")
lines.append("")
lines.append("---")
lines.append("")

for i, v in enumerate(top_100):
    lines.append(f"### 第{i+1}条 / Item #{i+1}")
    lines.append(f"- 标题 / Title: {v['title']}")
    lines.append(f"- 作者 / Author: @{v['author']}")
    lines.append(f"- 点赞 / Likes: {v['digg_count']}")
    lines.append(f"- 话题 / Tags: {v['keyword']}")
    lines.append(f"- 内容总结 / Summary: {v['title'][:200]}")
    lines.append(f"- 链接 / URL: {v['url']}")
    lines.append("")

# Write to file (APPEND mode)
data_dir = r'E:\workspace\content-hunter-data\data'
output_path = os.path.join(data_dir, 'douyin.md')
with open(output_path, 'a', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print(f"\nDOUYIN DATA APPENDED to: {output_path}")
print(f"Total records: {len(top_100)}")

# Save raw JSON
raw_path = os.path.join(data_dir, 'douyin_search_raw.json')
with open(raw_path, 'w', encoding='utf-8') as f:
    json.dump(top_100, f, ensure_ascii=False, indent=2)
print(f"Raw JSON saved: {raw_path}")
