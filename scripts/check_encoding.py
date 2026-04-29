#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys

file_path = r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py'

with open(file_path, 'rb') as f:
    data = f.read()

print(f"File size: {len(data)} bytes")

# Try to decode and find error position
pos = 0
block_size = 1000
while pos < len(data):
    chunk = data[pos:pos+block_size]
    try:
        chunk.decode('utf-8')
    except UnicodeDecodeError as e:
        print(f"Error at pos {pos + e.start}: {e}")
        ctx_start = max(0, pos + e.start - 20)
        ctx_end = min(len(data), pos + e.start + 20)
        print(f"Context bytes: {data[ctx_start:ctx_end]}")
        print(f"Context hex: {data[ctx_start:ctx_end].hex()}")
        break
    pos += block_size
else:
    print("File is valid UTF-8")
