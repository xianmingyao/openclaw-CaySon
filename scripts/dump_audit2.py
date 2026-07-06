"""Dump audit JSON - v2 with correct field names"""
import json, sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = json.load(f)

if 'function_issues' in data:
    sev_filter = sys.argv[2] if len(sys.argv) > 2 else None
    for x in data['function_issues']:
        for issue in x.get('issues', []):
            if sev_filter and issue.get('severity') != sev_filter:
                continue
            print('=' * 80)
            sev = issue.get('severity', '?').upper()
            t = issue.get('type', '?')
            print(f'[{sev}] {x["file"]}::{x["function"]}  -- {t}')
            print(f'  {issue.get("desc", "")[:400]}')
            print()
elif 'findings' in data:
    for x in data['findings']:
        print('=' * 80)
        sev = x.get('severity', '?').upper()
        print(f'[{sev}] {x.get("title", x.get("name", "?"))}')
        if 'file' in x:
            print(f'  File: {x["file"]}:{x.get("line", "?")}')
        if 'description' in x:
            print(f'  Desc: {x["description"][:300]}')
        print()
