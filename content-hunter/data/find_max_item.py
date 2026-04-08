import os, re
import sys
sys.stdout.reconfigure(encoding='utf-8')

for fname in ['douyin.md', 'bilibili.md']:
    fpath = os.path.join('.', fname)
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        # Find all item numbers
        nums = re.findall(r'^### 第(\d+)条', content, re.MULTILINE)
        nums = [int(n) for n in nums]
        if nums:
            print(f'{fname}: min={min(nums)}, max={max(nums)}, unique_count={len(set(nums))}, total_matches={len(nums)}')
        else:
            print(f'{fname}: NO items found')
    else:
        print(f'{fname}: NOT FOUND')
