#!/usr/bin/env python
# -*- coding: utf-8 -*-
with open(r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py', 'rb') as f:
    data = f.read()
    
# Check for BOM
print(f'Has BOM: {data.startswith(b"\xef\xbb\xbf")}')

# Check line 214 in detail
lines = data.split(b'\n')
line214 = lines[213]  # 0-indexed
print(f'Line 214 bytes: {line214}')
print(f'Line 214 decoded: {line214.decode("utf-8")}')

# Check for invalid characters
for i, b in enumerate(line214):
    if b == 0xff or (b >= 0xfe and b <= 0xff):
        print(f'Invalid byte at position {i}: 0x{b:02x}')
