#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

file_path = r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py'

with open(file_path, 'rb') as f:
    data = f.read()

print(f"File size: {len(data)} bytes")

# Find any non-UTF-8 sequences
i = 0
errors = []
while i < len(data):
    # Check if byte is ASCII
    if data[i] < 0x80:
        i += 1
        continue
    
    # Check for 2-byte UTF-8
    if data[i] >= 0xc0 and data[i] <= 0xdf:
        if i + 1 < len(data) and data[i+1] >= 0x80 and data[i+1] <= 0xbf:
            i += 2
            continue
        else:
            errors.append((i, f"Invalid 2-byte UTF-8 start: {data[i]:02x}"))
            i += 1
            continue
    
    # Check for 3-byte UTF-8
    if data[i] >= 0xe0 and data[i] <= 0xef:
        if i + 2 < len(data) and all(data[i+j] >= 0x80 and data[i+j] <= 0xbf for j in [1, 2]):
            i += 3
            continue
        elif i + 2 >= len(data):
            errors.append((i, f"Truncated 3-byte UTF-8 at end: {data[i]:02x}"))
            break
        else:
            errors.append((i, f"Invalid 3-byte UTF-8: {data[i]:02x} {data[i+1] if i+1 < len(data) else '??':02x} {data[i+2] if i+2 < len(data) else '??':02x}"))
            i += 1
            continue
    
    # Check for 4-byte UTF-8
    if data[i] >= 0xf0 and data[i] <= 0xf7:
        if i + 3 < len(data) and all(data[i+j] >= 0x80 and data[i+j] <= 0xbf for j in [1, 2, 3]):
            i += 4
            continue
        else:
            errors.append((i, f"Invalid 4-byte UTF-8"))
            i += 1
            continue
    
    # Invalid byte
    errors.append((i, f"Invalid byte: {data[i]:02x}"))
    i += 1

if errors:
    print(f"Found {len(errors)} encoding errors:")
    for pos, msg in errors[:10]:
        ctx = data[max(0,pos-10):pos+10]
        print(f"  Pos {pos}: {msg}")
        print(f"    Context: {ctx}")
        print(f"    Hex: {ctx.hex()}")
else:
    print("File is valid UTF-8 (checked all bytes)")
