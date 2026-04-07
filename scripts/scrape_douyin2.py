import urllib.request
import urllib.parse
import json
import re
import time
import os

def search_douyin_v2(keyword, page=1):
    """Try alternative Douyin search API"""
    # Try the search suggest API first for IDs
    url = f"https://www.douyin.com/aweme/v1/web/search/item/?keyword={urllib.parse.quote(keyword)}&count=20&offset={(page-1)*20}&search_source=tab_search&query_correct_type=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Referer": "https://www.douyin.com",
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"Status: {data.get('status_code')}, Data length: {len(data.get('item_list', []))}")
            return data.get('item_list', [])
    except Exception as e:
        print(f"Error: {e}")
        return []

# Test with one keyword
print("Testing Douyin search API...")
results = search_douyin_v2("人工智能", page=1)
print(f"Got {len(results)} results")
if results:
    for r in results[:3]:
        print(f"  - {r.get('desc', '')[:50]} | Aid: {r.get('aweme_id', '')}")
