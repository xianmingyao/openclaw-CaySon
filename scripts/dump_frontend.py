"""Dump frontend audit JSON"""
import json, sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== top_5_critical_issues ===')
for x in data.get('top_5_critical_issues', []):
    print(f'--- Rank {x.get("rank")} ---')
    print(f'  Title:  {x.get("title")}')
    if x.get('impact'):
        print(f'  Impact: {x["impact"][:300]}')
    if x.get('fix'):
        print(f'  Fix:    {x["fix"][:300]}')
    if x.get('files'):
        print(f'  Files:  {", ".join(x["files"])}')
    print()

print('=== recommendations (top 10) ===')
for x in data.get('recommendations', [])[:10]:
    if isinstance(x, dict):
        print(f'- {x.get("title", x.get("name", "?"))}')
        for k, v in x.items():
            if k not in ('title', 'name'):
                print(f'    {k}: {str(v)[:200]}')
    else:
        print(f'- {x}')
    print()

print('=== global_findings ===')
for k, v in data.get('global_findings', {}).items():
    if isinstance(v, list):
        print(f'  {k}: {len(v)} items')
    elif isinstance(v, dict):
        print(f'  {k}: {len(v)} keys')
    else:
        print(f'  {k}: {str(v)[:100]}')
