#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""深挖 GitHub一周热点110期 - 使用网页抓取"""
import requests
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/vnd.github.v3+json"
}

repos = [
    ("ultraworkers", "claw-code"),
    ("MemPalace", "mempalace"),
    ("JuliusBrussee", "caveman"),
    ("nexu-io", "open-design"),
    ("h4ckf0r0day", "obscura"),
]

print("=" * 60)
print("GitHub一周热点110期（2026-04-01）深挖")
print("=" * 60)

for owner, repo in repos:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    try:
        r = requests.get(url, timeout=20, headers=HEADERS)
        if r.status_code == 200:
            data = r.json()
            print(f"\n【{owner}/{repo}】")
            print(f"  ⭐ Stars: {data.get('stargazers_count', 0):,}")
            print(f"  🍴 Forks: {data.get('forks_count', 0):,}")
            print(f"  💻 Lang: {data.get('language', 'N/A')}")
            print(f"  📝 Desc: {data.get('description', 'N/A')}")
            print(f"  🔗 URL: {data.get('html_url', 'N/A')}")
            print(f"  📦 License: {data.get('license', {}).get('spdx_id', 'N/A')}")
            print(f"  🏷️ Topics: {', '.join(data.get('topics', [])[:5]) or 'N/A'}")
        elif r.status_code == 403:
            print(f"\n【{owner}/{repo}】 ⚠️ Rate limited")
        else:
            print(f"\n【{owner}/{repo}】 Error: {r.status_code}")
    except Exception as e:
        print(f"\n【{owner}/{repo}】 Exception: {type(e).__name__}")
