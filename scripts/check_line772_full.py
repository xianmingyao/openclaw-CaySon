#!/usr/bin/env python
# -*- coding: utf-8 -*-
with open(r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py', 'rb') as f:
    lines = f.read().split(b'\n')

print('Total lines:', len(lines))

if len(lines) >= 772:
    line772 = lines[771]  # 0-indexed
    print('Line 772 full:')
    print('  Bytes:', line772)
    print('  Hex:', line772.hex())
    
    # Try to decode full line
    try:
        decoded = line772.decode('utf-8')
        print('  Decoded:', decoded)
    except Exception as e:
        print('  Decode error:', e)
    
    # Analyze the string issue
    print('\nAnalyzing string:')
    # Find "unit": product_data.get(
    idx = line772.find(b'"unit": product_data.get(')
    if idx >= 0:
        rest = line772[idx + len(b'"unit": product_data.get('):]
        print('  After get(:', repr(rest))
        
        # Count quotes
        print('  Quote count:', rest.count(b'"'))
        
        # Check for unterminated string
        # The pattern should be: "key", "default")
        # But it looks like it ends with: "的), instead of "的"),
