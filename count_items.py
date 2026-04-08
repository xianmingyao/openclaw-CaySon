# -*- coding: utf-8 -*-
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

for fname in [r'E:\workspace\content-hunter\data\bilibili.md', r'E:\workspace\content-hunter\data\douyin.md']:
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    # Match "第123条" using byte-safe regex
    pattern = re.compile(r'\u7b2c(\d+)\u6761')
    matches = pattern.findall(content)
    if matches:
        nums = [int(x) for x in matches]
        print('%s: %d items, last #%d' % (fname.split('\\')[-1], len(nums), max(nums)))
    else:
        print('%s: 0 items' % fname.split('\\')[-1])
