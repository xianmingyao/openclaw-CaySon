"""Dump db audit JSON - v2"""
import json, sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = json.load(f)

mode = sys.argv[2] if len(sys.argv) > 2 else 'migration_issues'
sev_filter = sys.argv[3] if len(sys.argv) > 3 else None

items = data.get(mode, [])

for m in items:
    if sev_filter and m.get('severity') != sev_filter:
        continue
    print('=' * 80)
    sev = str(m.get('severity', '?')).upper()
    print(f'[{sev}] {m.get("file", m.get("migration", "?"))}')
    if 'issue' in m:
        print(f'  Issue: {m["issue"]}')
    if 'description' in m:
        print(f'  Desc:  {m["description"]}')
    if 'recommendation' in m:
        print(f'  Fix:   {m["recommendation"]}')
    print()
