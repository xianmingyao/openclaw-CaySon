#!/usr/bin/env python
# -*- coding: utf-8 -*-
with open(r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py', 'rb') as f:
    lines = f.read().split(b'\n')
    
line214 = lines[213]  # 0-indexed
print(f'Line 214 raw bytes: {line214}')
print(f'Line 214 as UTF-8: {line214.decode("utf-8", errors="replace")}')

# Check the problematic position (offset 6, 0-indexed)
print(f'Byte at position 6: {hex(line214[6]) if len(line214) > 6 else "N/A"}')
print(f'Bytes 4-8: {line214[4:9]}')
