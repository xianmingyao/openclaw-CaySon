"""Dump routers audit global findings"""
import json, sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== global_findings ===')
for k, v in data.get('global_findings', {}).items():
    if isinstance(v, list):
        if len(v) > 5 and isinstance(v[0], str):
            print(f'  {k} ({len(v)}): {v[:5]} ...')
        else:
            print(f'  {k} ({len(v)}): {v}')
    else:
        print(f'  {k}: {str(v)[:300]}')
