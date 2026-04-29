#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import sys

file_path = r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py'

with open(file_path, 'rb') as f:
    source = f.read()

try:
    tree = ast.parse(source)
    print('Parsing successful!')
except SyntaxError as e:
    print(f'SyntaxError at line {e.lineno}, offset {e.offset}')
    print(f'Error message: {e.msg}')
    
    # Get the problematic line
    lines = source.split(b'\n')
    if e.lineno and e.lineno <= len(lines):
        problem_line = lines[e.lineno - 1]
        print(f'Problematic line bytes: {problem_line}')
        print(f'Problematic line decoded: {problem_line.decode("utf-8", errors="replace")}')
        
        if e.offset:
            # Show character at offset
            decoded_line = problem_line.decode('utf-8', errors='replace')
            if e.offset <= len(decoded_line):
                char = decoded_line[e.offset - 1]
                print(f'Character at offset {e.offset}: {repr(char)} = U+{ord(char):04X}')
