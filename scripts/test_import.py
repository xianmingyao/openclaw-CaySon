#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts')

# Force UTF-8 mode
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    import run_skill
    print('Import successful!')
except SyntaxError as e:
    print(f'SyntaxError: {e}')
    print(f'File: {e.filename}')
    print(f'Line: {e.lineno}')
    print(f'Offset: {e.offset}')
    
    # Read the problematic line
    with open(e.filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if e.lineno <= len(lines):
            print(f'Problematic line: {repr(lines[e.lineno-1])}')
