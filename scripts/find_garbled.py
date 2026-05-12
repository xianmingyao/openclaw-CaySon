# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = 'E:/workspace/knowledge-base/wiki/概念/企业AI本体Ontology-从工具到Agent的关键.md'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
print(f"Total lines: {len(lines)}")

garbled = []
for i, line in enumerate(lines):
    if '�' in line:
        garbled.append((i+1, line))

print(f"\nGarbled lines ({len(garbled)}):")
for linenum, line in garbled:
    print(f"Line {linenum}: {repr(line[:100])}")
