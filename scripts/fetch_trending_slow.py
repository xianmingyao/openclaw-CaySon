# -*- coding: utf-8 -*-
import requests
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

GITHUB_TOKEN = os.environ.get("GITHUBTOKEN", "")
headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# Detailed rate limit check
r = requests.get("https://api.github.com/rate_limit", headers=headers)
print(f"Rate limit status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"  Core limit: {data['resources']['core']['remaining']}/{data['resources']['core']['limit']}")
    print(f"  Search limit: {data['resources']['search']['remaining']}/{data['resources']['search']['limit']}")

# Test with Bearer token format
GITHUB_TOKEN2 = os.environ.get("GITHUBTOKEN", "")
headers2 = {"Authorization": f"Bearer {GITHUB_TOKEN2}"} if GITHUB_TOKEN2 else {}
r2 = requests.get("https://api.github.com/repos/affaan-m/everything-claude-code", headers=headers2)
print(f"\nBearer token test: {r2.status_code}")
if r2.status_code == 200:
    data = r2.json()
    print(f"  Stars: {data['stargazers_count']}")
elif r2.status_code == 403:
    print(f"  Error: {r2.json()}")
