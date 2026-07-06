"""Dump db audit JSON"""
import json, sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = json.load(f)

mode = sys.argv[2] if len(sys.argv) > 2 else 'migration_issues'
sev_filter = sys.argv[3] if len(sys.argv) > 3 else None

items = data.get(mode, [])
if not items and 'findings' in data:
    items = data['findings']

for m in items:
    if sev_filter and m.get('severity') != sev_filter:
        continue
    print('=' * 80)
    sev = str(m.get('severity', '?')).upper()
    title = m.get('title', m.get('type', '?'))
    src = m.get('migration', m.get('file', m.get('table', '?')))
    print(f'[{sev}] {src}  -- {title}')
    if 'description' in m:
        print(f'  Desc: {m["description"][:300]}')
    if 'recommendation' in m:
        print(f'  Fix:  {m["recommendation"][:300]}')
    print()
