#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""修复 run_skill.py 的编码问题"""

import os

file_path = r'E:\workspace\skills\jingmai-putaway\jingmai-cli\resources\jingmai_product_publish\scripts\run_skill.py'

# 读取文件（忽略编码错误）
with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# 替换已知的损坏字符
replacements = {
    '�?': ': ',
    '�?': ': ',
    '�?': '的',
    '（避�?': '（避免 ',
    'DeprecationWarning)�?': 'DeprecationWarning) 的',
}

for old, new in replacements.items():
    content = content.replace(old, new)

# 写回文件
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"已修复 {file_path}")
print(f"文件大小: {os.path.getsize(file_path)} bytes")
