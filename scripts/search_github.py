# -*- coding: utf-8 -*-
import requests
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

GITHUB_TOKEN = os.environ.get("GITHUBTOKEN", "")
headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# Test: Fetch repos with auth
print("=== GitHub TOP20 验证 ===\n")

repos = [
    ("affaan-m/everything-claude-code", "TOP1"),
    ("bytedance/deer-flow", "TOP2"),
    ("obra/superpowers", "TOP3"),
    ("msitarzewski/agency-agents", "TOP8"),
    ("anthropic/skills", "TOP17"),
]

for repo, rank in repos:
    try:
        r = requests.get(f"https://api.github.com/repos/{repo}", headers=headers, timeout=15)
        if r.status_code == 200:
            data = r.json()
            print(f"{rank} {repo}: {data['stargazers_count']} stars")
        else:
            print(f"{rank} {repo}: ERROR {r.status_code}")
    except Exception as e:
        print(f"{rank} {repo}: ERROR {str(e)[:50]}")
