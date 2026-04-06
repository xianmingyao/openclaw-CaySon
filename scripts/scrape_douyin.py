#!/usr/bin/env python
"""Test Douyin API and scrape AI content."""

import urllib.request
import urllib.parse
import json
import gzip
import os
import re
from datetime import datetime

DATA_DIR = os.path.expanduser("~/.openclaw/workspace/content-hunter/data")
DOUYIN_FILE = os.path.join(DATA_DIR, "douyin.md")

def test_and_scrape_douyin():
    """Test Douyin API and scrape AI content."""
    keywords = ["AI技术", "人工智能", "ChatGPT", "大模型", "AIGC", "AI工具", "AI绘画", "LLM大模型", "AI编程", "AI生成"]
    all_items = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
        'Referer': 'https://www.douyin.com/',
        'Accept': 'application/json',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }

    for kw in keywords:
        try:
            encoded_kw = urllib.parse.quote(kw)
            url = f'https://www.douyin.com/aweme/v1/web/search/item/?keyword={encoded_kw}&count=20&offset=0&search_source=tab_search&channel_id=0&sort_type=0&publish_time=0&source=search_history&pc_client_type=1&version_code=190500&version_name=19.5.0'
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as r:
                raw = r.read()
                try:
                    raw = gzip.decompress(raw)
                except:
                    pass
                data = json.loads(raw.decode('utf-8'))

                # Try different paths
                aweme_list = None
                if isinstance(data, dict):
                    if 'aweme_list' in data:
                        aweme_list = data['aweme_list']
                    elif 'data' in data:
                        d = data['data']
                        if isinstance(d, list):
                            aweme_list = d
                        elif isinstance(d, dict) and 'aweme_list' in d:
                            aweme_list = d['aweme_list']
                        elif isinstance(d, dict) and 'list' in d:
                            aweme_list = d['list']

                if aweme_list and len(aweme_list) > 0:
                    for aweme in aweme_list:
                        stats = aweme.get('statistics', {}) or {}
                        author_info = aweme.get('author', {}) or {}
                        all_items.append({
                            'title': aweme.get('desc', '')[:200],
                            'author': author_info.get('nickname', '未知'),
                            'aweme_id': aweme.get('aweme_id', ''),
                            'digg_count': stats.get('digg_count', 0),
                            'comment_count': stats.get('comment_count', 0),
                            'share_count': stats.get('share_count', 0),
                            'play_count': stats.get('play_count', 0),
                            'tag': kw,
                        })
                    print(f"  '{kw}': {len(aweme_list)} items")
                else:
                    print(f"  '{kw}': no items (keys: {list(data.keys())[:5] if isinstance(data, dict) else type(data)})")

        except Exception as e:
            print(f"  '{kw}': Error - {e}")

    # Dedupe
    seen = set()
    unique_items = []
    for item in all_items:
        if item['aweme_id'] and item['aweme_id'] not in seen:
            seen.add(item['aweme_id'])
            unique_items.append(item)

    print(f"\nTotal unique items: {len(unique_items)}")
    return unique_items

def append_to_file(items, start_num):
    """Append items to Douyin markdown file."""
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(DOUYIN_FILE, 'a', encoding='utf-8') as f:
        if start_num == 1:
            f.write(f"# 抖音 AI技术热门内容\n\n")
            f.write(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        for i, item in enumerate(items):
            num = start_num + i
            title = item['title'] or '暂无标题'
            f.write(f"### 第{num}条\n")
            f.write(f"- 标题 / Title: {title}\n")
            f.write(f"- 作者 / Author: @{item['author']}\n")
            f.write(f"- 抖音ID: {item['aweme_id']}\n")
            f.write(f"- 点赞 / Likes: {item['digg_count']}\n")
            f.write(f"- 评论 / Comments: {item['comment_count']}\n")
            f.write(f"- 分享 / Shares: {item['share_count']}\n")
            f.write(f"- 播放 / Plays: {item['play_count']}\n")
            f.write(f"- 话题 / Tags: #{item['tag']}\n")
            f.write(f"- 内容总结 / Summary: {title}\n\n")

    return len(items)

def get_existing_count():
    fp = DOUYIN_FILE
    if not os.path.exists(fp):
        return 0
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.findall(r'### 第(\d+)条', content)
        if matches:
            return max(int(m) for m in matches)
    return 0

if __name__ == "__main__":
    print("=" * 60)
    print("抖音 AI技术热门内容抓取")
    print("=" * 60)

    existing = get_existing_count()
    print(f"当前已有: {existing} 条 (目标: 100)")

    print("\n正在抓取抖音...")
    items = test_and_scrape_douyin()

    if items:
        new_start = existing + 1
        n = append_to_file(items, new_start)
        print(f"\n追加写入 {n} 条新数据")

    final = get_existing_count()
    print(f"最终累计: {final} 条")
    if final >= 100:
        print("目标达成!")
    else:
        print(f"还差 {100 - final} 条")
