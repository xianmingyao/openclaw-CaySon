#!/usr/bin/env python
# -*- coding: utf-8 -*-
with open(r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py', 'rb') as f:
    content = f.read()

# Search for product_data.get patterns
import re

# Find all product_data.get calls
pattern = b'product_data\\.get\\([^)]+\\)'
matches = list(re.finditer(pattern, content))

print(f'Found {len(matches)} product_data.get calls')

for i, m in enumerate(matches[:20]):
    print(f'\nMatch {i+1} at position {m.start()}:')
    print(f'  {m.group()[:100]}')
    
    # Try to decode
    try:
        decoded = m.group().decode('utf-8')
        print(f'  Decoded: {decoded[:100]}')
    except:
        print('  Decode error')
