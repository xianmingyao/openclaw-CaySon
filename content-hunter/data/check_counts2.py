import re
for fname in ['douyin.md', 'bilibili.md']:
    path = 'E:/workspace/content-hunter/data/' + fname
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    matches = re.findall(r'第(\d+)条', content)
    nums = [int(x) for x in matches]
    print(f'{fname}: {len(nums)} occurrences, max#={max(nums)}')
    # count duplicates
    from collections import Counter
    c = Counter(nums)
    dups = {k:v for k,v in c.items() if v > 1}
    if dups:
        print(f'  duplicates: {len(dups)} numbers appear more than once')
        print(f'  sample dups: {list(dups.items())[:5]}')
    # distribution
    bins = {}
    for n in nums:
        bucket = (n // 100) * 100
        bins[bucket] = bins.get(bucket, 0) + 1
    for k in sorted(bins.keys()):
        print(f'  #{k}-{k+99}: {bins[k]} items')
