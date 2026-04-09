"""
Douyin AI Tech Scraper - Batch 101-200
Tries mobile WAP version and various workarounds
"""
import requests
import json
import re
from urllib.parse import quote

headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Referer": "https://www.douyin.com/",
    "Accept": "application/json, text/plain, */*",
}

def try_douyin_api():
    """Try various Douyin API endpoints"""
    apis = [
        # Search API
        "https://www.douyin.com/aweme/v1/web/search/item/?keyword=AI%E6%8A%80%E6%9C%AF&count=30&offset=0",
        # Hot list API
        "https://www.douyin.com/aweme/v1/web/hot/search/list/?count=50",
        # Fake referer
    ]
    
    for url in apis:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            print(f"URL: {url[:60]}")
            print(f"Status: {resp.status_code}")
            print(f"Content: {resp.text[:200]}")
            print("---")
        except Exception as e:
            print(f"Error: {e}")

def try_douyin_search():
    """Try Douyin search API"""
    url = "https://www.douyin.com/aweme/v1/web/search/item/"
    params = {
        "keyword": "AI%E6%8A%80%E6%9C%AF",
        "count": 30,
        "offset": 0,
        "device_platform": "webapp",
        "aid": 6383,
        "channel": "channel_pc_web",
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"Search status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
    except Exception as e:
        print(f"Search error: {e}")

def try_mobile_douyin():
    """Try mobile.douyin.com"""
    url = "https://m.douyin.com/search/AI%E6%8A%80%E6%9C%AF"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Mobile status: {resp.status_code}")
        print(f"URL: {resp.url}")
        # Look for video data in HTML
        patterns = [
            r'"aweme_id":"(\d+)"',
            r'"desc":"([^"]+)"',
            r'"author":{"nickname":"([^"]+)"',
        ]
        for pat in patterns:
            matches = re.findall(pat, resp.text)
            if matches:
                print(f"Pattern {pat[:30]}: {len(matches)} matches")
                print(f"  First 3: {matches[:3]}")
    except Exception as e:
        print(f"Mobile error: {e}")

if __name__ == "__main__":
    print("Testing Douyin APIs...")
    try_douyin_api()
    print("\n---")
    try_douyin_search()
    print("\n---")
    try_mobile_douyin()
