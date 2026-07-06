#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Verify the UTF-8 bytes for line 214

line_214_bytes = b'\xe7\xad\x96\xe7\x95\xa5\xef\xbc\x88\xe4\xbc\x98\xe5\x85\x88\xe7\xba\xa7\xe4\xbb\x8e\xe9\xab\x98\xe5\x88\xb0\xe4\xbd\x8e\xef\xbc\x89\xef\xbc\x9a'

print("UTF-8 decoding test:")
try:
    decoded = line_214_bytes.decode('utf-8')
    print(f"  Decoded: {decoded}")
    print(f"  Code points: {[hex(ord(c)) for c in decoded]}")
except Exception as e:
    print(f"  Error: {e}")

# Now read from file
with open(r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py', 'rb') as f:
    lines = f.read().split(b'\n')

file_line214 = lines[213]
print(f"\nFile line 214 ({len(file_line214)} bytes):")
print(f"  Bytes: {file_line214}")
print(f"  Hex: {file_line214.hex()}")

print(f"\nComparing:")
print(f"  Expected bytes: {line_214_bytes.hex()}")
print(f"  File bytes:    {file_line214.hex()}")
print(f"  Match: {line_214_bytes == file_line214}")
