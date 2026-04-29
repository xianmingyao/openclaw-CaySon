#!/usr/bin/env python
# -*- coding: utf-8 -*-
with open(r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    
line214 = lines[213]  # 0-indexed
print(f'Line 214: {repr(line214)}')
print(f'Line 214 chars: {[hex(ord(c)) for c in line214]}')
