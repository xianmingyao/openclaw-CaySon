"""Dump db audit recommendations"""
import json, sys

with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = json.load(f)

for m in data['recommendations']:
    print(f'P{m["priority"]} [{m.get("severity","?")}] {m.get("title","?")}')
    if m.get('effort_hours'):
        print(f'    预计工时: {m["effort_hours"]}h')
    if m.get('rationale'):
        print(f'    {m["rationale"][:300]}')
    if m.get('sql_example'):
        print(f'    SQL: {m["sql_example"][:300]}')
    print()
