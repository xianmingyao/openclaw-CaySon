"""Dump audit JSON to readable text"""
import json, sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = json.load(f)

if 'function_issues' in data:
    issues = data['function_issues']
    sev_filter = sys.argv[2] if len(sys.argv) > 2 else None
    for x in issues:
        if sev_filter and x.get('severity') != sev_filter:
            continue
        print('=' * 80)
        f_ = x.get('file', '?')
        ln = x.get('line', '?')
        fn = x.get('function', '?')
        sev = x.get('severity', '?').upper()
        title = x.get('title', '?')
        print(f'[{sev}] {f_}:{ln}  {fn}')
        print(f'  Title: {title}')
        if 'description' in x:
            print(f'  Desc: {x["description"][:300]}')
        if 'recommendation' in x:
            print(f'  Fix: {x["recommendation"][:300]}')
        print()
elif 'findings' in data:
    for x in data['findings']:
        print('=' * 80)
        sev = x.get('severity', '?').upper()
        title = x.get('title', '?')
        print(f'[{sev}] {title}')
        if 'file' in x:
            print(f'  File: {x["file"]}:{x.get("line", "?")}')
        if 'description' in x:
            print(f'  Desc: {x["description"][:300]}')
        if 'recommendation' in x:
            print(f'  Fix: {x["recommendation"][:300]}')
        print()
