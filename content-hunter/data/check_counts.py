import os, re
import sys
sys.stdout.reconfigure(encoding='utf-8')

for fname in ['douyin.md', 'bilibili.md']:
    fpath = os.path.join('.', fname)
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        count = len(re.findall(r'^### 第\d+条', content, re.MULTILINE))
        lines = content.count('\n') + 1
        # print first 3 lines as ascii-safe
        first_lines = content.split('\n')[:3]
        print(f'{fname}: {count} items, {lines} lines')
    else:
        print(f'{fname}: NOT FOUND, will create')
