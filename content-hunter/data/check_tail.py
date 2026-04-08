import os, re
import sys
sys.stdout.reconfigure(encoding='utf-8')

for fname in ['douyin.md', 'bilibili.md']:
    fpath = os.path.join('.', fname)
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        count = len(re.findall(r'^### 第\d+条', content, re.MULTILINE))
        lines = content.split('\n')
        print(f'\n{fname}:')
        print(f'  Total items: {count}')
        print(f'  Last 10 lines:')
        for l in lines[-10:]:
            print(f'    {repr(l[:100])}')
    else:
        print(f'{fname}: NOT FOUND')
