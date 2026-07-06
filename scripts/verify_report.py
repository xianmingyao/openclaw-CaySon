# -*- coding: utf-8 -*-
import os
p = r'E:\workspace\GEO-Platform-系统诊断与优化建议.md'
size = os.path.getsize(p)
content = open(p, 'r', encoding='utf-8').read()
lines = len(content.splitlines())
print(f'File: {size} bytes, {lines} lines')
print(f'U+FFFD: {content.count(chr(0xFFFD))}')
print('=== First 300 chars ===')
print(content[:300])
print('=== Last 500 chars ===')
print(content[-500:])
