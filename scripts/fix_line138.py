#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复 run_skill.py 第138行的问题"""

file_path = r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the corrupted line
old = '            for sep in [":", "\u7684, "="]:'
new = '            for sep in [":", "="]:'

if old in content:
    content = content.replace(old, new)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed!')
else:
    print('Pattern not found, trying alternate fix...')
    # Try to find and fix the line
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'for sep in' in line and '的, ' in line:
            print(f'Found at line {i+1}: {repr(line)}')
            # Fix: remove the corrupted part
            lines[i] = line.replace(', "\u7684, "', '').replace(', "的, "', '')
            content = '\n'.join(lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed line {i+1}')
            break
    else:
        print('Could not find the problematic line')
