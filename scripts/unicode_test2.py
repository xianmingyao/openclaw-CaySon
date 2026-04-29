#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts')

# Just try to compile the file
import py_compile
try:
    py_compile.compile(r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py', doraise=True)
    print('Compilation successful!')
except py_compile.PyCompileError as e:
    print(f'Compilation failed: {e}')
    
    # Extract the problematic line
    with open(r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py', 'rb') as f:
        content = f.read()
    
    # Find line 214
    lines = content.split(b'\n')
    if len(lines) >= 214:
        line = lines[213]  # 0-indexed
        print(f'Line 214 raw bytes: {line}')
        print(f'Line 214 hex: {line.hex()}')
        
        # Try to decode each multi-byte sequence
        i = 0
        while i < len(line):
            b = line[i]
            if b < 0x80:
                print(f'  ASCII: {chr(b)}')
                i += 1
            elif b >= 0xc0 and b <= 0xdf:
                print(f'  2-byte: {[hex(line[i+j]) for j in range(2)]}')
                i += 2
            elif b >= 0xe0 and b <= 0xef:
                seq = [hex(line[i+j]) for j in range(3)]
                try:
                    char = line[i:i+3].decode('utf-8')
                    print(f'  3-byte: {seq} -> {repr(char)}')
                except:
                    print(f'  3-byte: {seq} -> DECODE ERROR')
                i += 3
            else:
                print(f'  Invalid start byte: {hex(b)}')
                i += 1
