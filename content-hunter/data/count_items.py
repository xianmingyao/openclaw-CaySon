# -*- coding: utf-8 -*-
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

for fname in [r'E:\workspace\content-hunter\data\bilibili.md', r'E:\workspace\content-hunter\data\douyin.md']:
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()
        # Match "第123条" pattern
        matches = re.findall(ur'[\u7b2c]([0-9]+)[\u6761]', content)
        if matches:
            nums = [int(x) for x in matches]
            print('%s: count=%d max=%d' % (fname.split('\\')[-1], len(nums), max(nums)))
        else:
            print('%s: 0 items' % fname.split('\\')[-1])
    except Exception as e:
        print('Error: %s' % e)
