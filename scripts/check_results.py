# -*- coding: utf-8 -*-
import json
from pathlib import Path
import sys
sys.stdout.reconfigure(encoding='utf-8')

result_file = Path('E:/workspace/scripts/notion_sync_results.json')
content = result_file.read_text(encoding='utf-8', errors='ignore')
data = json.loads(content)

print('Total processed:', len(data['results']))
print('Success:', data['success'])
print('Failed:', data['failed'])

print()
print('Failed files:')
for r in data['results']:
    if not r['success']:
        title = r['title'][:30] if r['title'] else 'Unknown'
        error = str(r['error'])[:50] if r['error'] else 'Unknown'
        print(f'  - {title}: {error}')
