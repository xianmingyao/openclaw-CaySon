import re, os
d = r'E:\workspace\content-hunter\data'
for fname in ['douyin.md', 'bilibili.md']:
    fpath = os.path.join(d, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    nums = re.findall(r'^### 第(\d+)条', content, re.MULTILINE)
    if nums:
        nums_int = [int(n) for n in nums]
        print(f'{fname}: {len(nums_int)}条, 范围1-{max(nums_int)}')
    items = re.split(r'^### 第', content, flags=re.MULTILINE)
    if len(items) > 1:
        last = items[-1]
        lines = last.strip().split('\n')
        print(f'  最后一条: {lines[0]}')
