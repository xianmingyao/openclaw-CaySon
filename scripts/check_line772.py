#!/usr/bin/env python
# -*- coding: utf-8 -*-
with open(r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py', 'rb') as f:
    lines = f.read().split(b'\n')

print('Total lines:', len(lines))

if len(lines) >= 772:
    line772 = lines[771]  # 0-indexed
    print('Line 772 bytes:', repr(line772[:100]))
    print('Line 772 hex:', line772[:100].hex())
    
    # Try to decode
    try:
        decoded = line772.decode('utf-8')
        print('Line 772 decoded:', repr(decoded[:100]))
    except:
        print('Decode error!')
        print('Raw bytes:', line772)
