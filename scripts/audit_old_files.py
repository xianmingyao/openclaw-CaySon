"""Audit all >30-day-old memory files for consolidation status."""
import os
import re
from datetime import datetime, timedelta

memory_dir = 'E:\\workspace\\memory'
today = datetime(2026, 6, 23)
threshold = today - timedelta(days=30)

all_files = sorted(os.listdir(memory_dir))
date_files = [f for f in all_files if re.match(r'^2026-\d{2}-\d{2}\.md$', f)]

print(f'Total dated memory files: {len(date_files)}')
print(f'Today: {today.date()}, threshold (>30d): files before {threshold.date()}')
print('=' * 80)

unmarked = []
old_files = []
for f in date_files:
    # Parse filename date
    m = re.match(r'^2026-(\d{2})-(\d{2})\.md$', f)
    if not m:
        continue
    file_date = datetime(2026, int(m.group(1)), int(m.group(2)))
    is_old = file_date < threshold
    
    path = os.path.join(memory_dir, f)
    with open(path, 'rb') as fp:
        data = fp.read()
    has_bom = data.startswith(b'\xef\xbb\xbf')
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        # Try GBK fallback
        try:
            text = data.decode('gbk')
        except:
            text = data.decode('utf-8', errors='replace')
    first_line = text.split('\n')[0] if text else '<EMPTY>'
    is_marked = 'consolidated to MEMORY.md' in first_line
    
    status = '✅' if is_marked else '❌'
    bom = 'BOM!' if has_bom else '     '
    
    if is_old:
        old_files.append(f)
        if not is_marked:
            unmarked.append(f)
        print(f'{status} {bom} {f} | first_line: {first_line[:70]}')
    else:
        if is_marked:
            print(f'M  {bom} {f} | (recent, marked) | first_line: {first_line[:70]}')
        else:
            print(f'   {bom} {f} | (recent, unmarked)')

print('=' * 80)
print(f'Old files (>30d): {len(old_files)}')
print(f'Unmarked old files: {len(unmarked)}')
if unmarked:
    print('Unmarked list:')
    for f in unmarked:
        print(f'  - {f}')