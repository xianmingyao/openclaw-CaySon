#!/usr/bin/env python
"""Use Apify REST API to run TikTok/Douyin scraper."""

import urllib.request
import urllib.parse
import json
import os
import re
import time
from datetime import datetime

APIFY_TOKEN = os.environ.get('APIFY_TOKEN', '')
DATA_DIR = os.path.expanduser("~/.openclaw/workspace/content-hunter/data")
DOUYIN_FILE = os.path.join(DATA_DIR, "douyin.md")

def run_apify_actor(actor_id, input_data):
    """Run an Apify actor via REST API and return results."""
    url = f"https://api.apify.com/v2/acts/{actor_id}/runs"
    data = json.dumps(input_data).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('Authorization', f'Bearer {APIFY_TOKEN}')
    req.add_header('Content-Type', 'application/json')
    
    with urllib.request.urlopen(req, timeout=30) as r:
        result = json.loads(r.read().decode('utf-8'))
        run_id = result['data']['id']
        print(f"  Started run: {run_id}")
        return run_id

def get_run_result(run_id, actor_id, max_wait=180):
    """Wait for run to complete and return dataset."""
    start = time.time()
    while time.time() - start < max_wait:
        time.sleep(5)
        # Check status
        status_url = f"https://api.apify.com/v2/acts/{actor_id}/runs/{run_id}"
        req = urllib.request.Request(status_url, method='GET')
        req.add_header('Authorization', f'Bearer {APIFY_TOKEN}')
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                status_data = json.loads(r.read().decode('utf-8'))
                status = status_data['data'].get('status', '')
                print(f"  Status: {status}")
                if status == 'SUCCEEDED':
                    # Get dataset
                    dataset_id = status_data['data'].get('defaultDatasetId')
                    if dataset_id:
                        items_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
                        req2 = urllib.request.Request(items_url, method='GET')
                        req2.add_header('Authorization', f'Bearer {APIFY_TOKEN}')
                        with urllib.request.urlopen(req2, timeout=30) as r2:
                            items = json.loads(r2.read().decode('utf-8'))
                            return items
                    return []
                elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                    print(f"  Run failed: {status}")
                    return []
        except Exception as e:
            print(f"  Error checking status: {e}")
    print("  Timeout waiting for result")
    return []

def search_tiktok_actor(keywords):
    """Run TikTok scraper for given keywords."""
    all_items = []
    actor_id = "clockworks/tiktok-scraper"
    
    for kw in keywords:
        print(f"\n  Searching TikTok for: {kw}")
        input_data = {
            "searchQueries": [kw],
            "searchType": "hashtag",
            "maxItems": 30,
        }
        try:
            run_id = run_apify_actor(actor_id, input_data)
            items = get_run_result(run_id, actor_id, max_wait=120)
            print(f"  Got {len(items)} items")
            all_items.extend(items)
        except Exception as e:
            print(f"  Error: {e}")
    
    return all_items

def search_tiktok_keyword(keywords):
    """Use keyword search instead of hashtag."""
    all_items = []
    actor_id = "clockworks/tiktok-scraper"
    
    for kw in keywords:
        print(f"\n  Searching TikTok for keyword: {kw}")
        input_data = {
            "searchQueries": [kw],
            "searchType": "keyword",
            "maxItems": 30,
        }
        try:
            run_id = run_apify_actor(actor_id, input_data)
            items = get_run_result(run_id, actor_id, max_wait=120)
            print(f"  Got {len(items)} items")
            all_items.extend(items)
        except Exception as e:
            print(f"  Error: {e}")
    
    return all_items

def append_douyin_to_file(items, start_num):
    """Append items to Douyin markdown file."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    with open(DOUYIN_FILE, 'a', encoding='utf-8') as f:
        if start_num == 1:
            f.write(f"# 抖音 AI技术热门内容\n\n")
            f.write(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for i, item in enumerate(items):
            num = start_num + i
            title = (item.get('desc') or item.get('title') or item.get('text') or '暂无标题')[:200]
            author = item.get('authorMeta', {}).get('name', '') or item.get('author', {}).get('nickname', '未知')
            video_id = item.get('id', item.get('aweme_id', ''))
            stats = item.get('stats', item.get('statistics', {})) or {}
            digg = stats.get('diggCount', stats.get('digg_count', 0))
            comment = stats.get('commentCount', stats.get('comment_count', 0))
            share = stats.get('shareCount', stats.get('share_count', 0))
            play = stats.get('playCount', stats.get('play_count', 0))
            tag = item.get('hashtagNames', item.get('tag', []))
            if isinstance(tag, list) and tag:
                tag_str = ' '.join(f'#{t}' for t in tag[:5])
            else:
                tag_str = '#AI'
            
            f.write(f"### 第{num}条\n")
            f.write(f"- 标题 / Title: {title}\n")
            f.write(f"- 作者 / Author: @{author}\n")
            f.write(f"- 抖音ID: {video_id}\n")
            f.write(f"- 点赞 / Likes: {digg}\n")
            f.write(f"- 评论 / Comments: {comment}\n")
            f.write(f"- 分享 / Shares: {share}\n")
            f.write(f"- 播放 / Plays: {play}\n")
            f.write(f"- 话题 / Tags: {tag_str}\n")
            f.write(f"- 内容总结 / Summary: {title}\n\n")
    
    return len(items)

def get_existing_count():
    if not os.path.exists(DOUYIN_FILE):
        return 0
    with open(DOUYIN_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.findall(r'### 第(\d+)条', content)
        if matches:
            return max(int(m) for m in matches)
    return 0

if __name__ == "__main__":
    print("=" * 60)
    print("Apify TikTok Scraper (for Douyin AI content)")
    print("=" * 60)
    
    if not APIFY_TOKEN:
        print("ERROR: APIFY_TOKEN not found in environment")
        exit(1)
    
    keywords = ["AI technology", "artificial intelligence", "ChatGPT", "LLM", "AIGC", "AI tools", "AI generator"]
    
    print(f"\nSearching with {len(keywords)} keywords...")
    items = search_tiktok_keyword(keywords)
    
    print(f"\nTotal items from TikTok: {len(items)}")
    
    if items:
        existing = get_existing_count()
        new_start = existing + 1
        n = append_douyin_to_file(items, new_start)
        print(f"\nAppended {n} items to {DOUYIN_FILE}")
    
    final = get_existing_count()
    print(f"Final count: {final}")
