"""Verify consolidation markers in memory files."""
import os

files = [
    '2026-04-14.md', '2026-04-16.md', '2026-04-18.md', '2026-04-21.md', '2026-04-22.md',
    '2026-05-05.md', '2026-05-06.md', '2026-05-07.md', '2026-05-08.md', '2026-05-09.md',
    '2026-05-10.md', '2026-05-11.md', '2026-05-12.md', '2026-05-13.md', '2026-05-14.md', '2026-05-15.md'
]

for f in files:
    path = f'E:\\workspace\\memory\\{f}'
    if not os.path.exists(path):
        print(f'MISSING: {f}')
        continue
    with open(path, 'rb') as fp:
        data = fp.read()
    has_bom = data.startswith(b'\xef\xbb\xbf')
    text = data.decode('utf-8')
    lines = text.split('\n')
    line1 = lines[0][:80] if lines else '<EMPTY>'
    line2 = lines[1][:80] if len(lines) > 1 else '<EOF>'
    print(f'{f}: BOM={has_bom} | line1=[{line1}] | line2=[{line2}]')