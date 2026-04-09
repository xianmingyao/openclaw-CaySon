"""
Douyin WAP/Mobile scraper - Try to get AI content without login
"""
import requests
import json
import re
from datetime import datetime

mobile_headers = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "https://www.douyin.com/",
}

def try_wap_search():
    """Try Douyin WAP search"""
    keywords = ["AI%E6%8A%80%E6%9C%AF", "DeepSeek", "ChatGPT"]
    for kw in keywords:
        url = f"https://m.douyin.com/search/{kw}"
        try:
            resp = requests.get(url, headers=mobile_headers, timeout=10, allow_redirects=True)
            print(f"WAP {kw}: status={resp.status_code}, url={resp.url}")
            print(f"Content length: {len(resp.text)}")
            if resp.status_code == 200:
                # Look for video data
                if "aweme" in resp.text or "video" in resp.text:
                    print("Found video data!")
                    # Extract some data
                    titles = re.findall(r'"desc":"([^"]+)"', resp.text)
                    authors = re.findall(r'"nickname":"([^"]+)"', resp.text)
                    print(f"Titles found: {len(titles)}")
                    for t in titles[:3]:
                        print(f"  {t}")
        except Exception as e:
            print(f"WAP error: {e}")

def try_pc_web_no_login():
    """Try PC web without login"""
    # Try the Douyin explore/discover page
    url = "https://www.douyin.com/explore"
    try:
        resp = requests.get(url, headers=mobile_headers, timeout=10)
        print(f"Explore: status={resp.status_code}")
        # Try to find video data
        titles = re.findall(r'"desc":"([^"]+)"', resp.text)
        print(f"Titles found: {len(titles)}")
        for t in titles[:5]:
            print(f"  {t[:80]}")
    except Exception as e:
        print(f"Explore error: {e}")

def try_douyin_api_v2():
    """Try different API endpoints"""
    # Try the recommend feed
    apis = [
        "https://www.douyin.com/aweme/v1/web/tab/feed/?device_platform=webapp&aid=6383&channel=channel_pc_web&count=20",
        "https://www.douyin.com/aweme/v1/web/hot/search/list/?device_platform=webapp&aid=6383&channel=channel_pc_web&count=30",
    ]
    
    for url in apis:
        try:
            resp = requests.get(url, headers=mobile_headers, timeout=10)
            print(f"API: {url[40:80]}... -> {resp.status_code}")
            if resp.status_code == 200 and resp.text:
                try:
                    data = resp.json()
                    print(f"  Code: {data.get('status_code', 'N/A')}")
                    if "aweme_list" in str(data):
                        aweme_list = data.get("aweme_list", [])
                        print(f"  aweme_list: {len(aweme_list)}")
                        if aweme_list:
                            for a in aweme_list[:3]:
                                print(f"    - {a.get('desc','')[:50]}")
                    elif "word_list" in str(data):
                        word_list = data.get("data", {}).get("word_list", [])
                        print(f"  word_list: {len(word_list)}")
                except:
                    print(f"  Not JSON, first 100 chars: {resp.text[:100]}")
        except Exception as e:
            print(f"API error: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("Testing Douyin access methods")
    print("=" * 50)
    try_wap_search()
    print("\n---")
    try_pc_web_no_login()
    print("\n---")
    try_douyin_api_v2()
