# -*- coding: utf-8 -*-
import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Search for specific projects mentioned in the video
projects = [
    ('RuView', 'ruvnet/RuView'),
    ('deer-flow', 'bytedance/deer-flow'),
    ('mem0', 'mem0ai/mem0'),
    ('cherry-studio', 'CherryHQ/cherry-studio'),
    ('cc-switch', 'farion1231/cc-switch'),
    ('AstrBot', 'AstrBotDevs/AstrBot'),
    ('haystack', 'deepset-ai/haystack'),
    ('OpenClaw', 'openclaw/openclaw'),
    ('hermes-agent', 'NousResearch/hermes-agent'),
    ('context-engineering', 'coleam00/context-engineering-intro'),
    ('opencode', 'opencode-cli/opencode'),
    ('goose', 'dotshado/goose'),
    ('gpt-computer', 'U-Hir0/gpt-computer'),
    ('anything-llm', 'Mintplex-Labs/anything-llm'),
    ('winrt', 'nicksh8/winrt'),
]

results = []

for name, repo in projects:
    try:
        r = requests.get(f'https://api.github.com/repos/{repo}', 
                        headers={'Accept': 'application/vnd.github.v3+json'}, 
                        timeout=10)
        if r.status_code == 200:
            data = r.json()
            results.append({
                'name': name,
                'full_name': data['full_name'],
                'stars': data['stargazers_count'],
                'forks': data['forks_count'],
                'description': data.get('description', '')
            })
            print(f"[OK] {name}: {data['stargazers_count']} stars")
        else:
            print(f"[FAIL] {name}: {r.status_code}")
    except Exception as e:
        print(f"[ERROR] {name}: {str(e)[:50]}")

# Save results
with open('E:/workspace/temp_trending.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nSaved {len(results)} projects to temp_trending.json")
