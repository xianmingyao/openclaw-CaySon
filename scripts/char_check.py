#!/usr/bin/env python
# -*- coding: utf-8 -*-
with open(r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py', 'rb') as f:
    content = f.read()

lines = content.split(b'\n')
line214 = lines[213]  # 0-indexed

# Check if EF BB BF BOM exists
print(f'Has BOM: {content[:3] == b"\xef\xbb\xbf"}')
print(f'File starts with: {content[:20]}')

# Decode line 214
decoded = line214.decode('utf-8')
print(f'Line 214: {repr(decoded)}')

# The character at position 6 should be U+FF08 (fullwidth left parenthesis)
char6 = decoded[6]
print(f'Char 6: {repr(char6)} = U+{ord(char6):04X}')

# What SHOULD be at position 6?
# "策略（优先级于高到低）："
# Position 0-3: spaces
# Position 4-5: 策略 (U+7B56, U+7565)
# Position 6: （ (U+FF08)
expected = "策略（优先级于高到低）："
print(f'Expected: {repr(expected)}')
print(f'Expected chars 4-15: {[hex(ord(c)) for c in expected[4:15]]}')
