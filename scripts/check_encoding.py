# -*- coding: utf-8 -*-
import codecs

filepath = 'E:/workspace/knowledge-base/wiki/概念/企业AI本体Ontology-从工具到Agent的关键.md'

# Read the file
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the garbled section
lines = content.split('\n')
print(f"Total lines: {len(lines)}")

# Find lines with garbled characters (Replacement Character �)
garbled = []
for i, line in enumerate(lines):
    if '�' in line:
        garbled.append((i+1, line[:80]))

print(f"\nGarbled lines ({len(garbled)}):")
for linenum, line in garbled[:20]:
    print(f"  Line {linenum}: {line}")
