#!/usr/bin/env python
# -*- coding: utf-8 -*-
with open(r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py', 'rb') as f:
    content = f.read()

lines = content.split(b'\n')
line214 = lines[213]  # 0-indexed

# Decode as UTF-8
decoded = line214.decode('utf-8')

print(f'Line 214 decoded: {repr(decoded)}')
print(f'Line 214 characters:')
for i, c in enumerate(decoded):
    print(f'  {i}: {repr(c)} (U+{ord(c):04X})')

# Check position 6
if len(decoded) > 6:
    char = decoded[6]
    print(f'\nCharacter at position 6: {repr(char)} (U+{ord(char):04X})')
    print(f'Is it U+FF08? {ord(char) == 0xFF08}')
