#!/usr/bin/env python
from pathlib import Path
import re

WIKI_DIR = Path('wiki')
pages = []
for md_file in WIKI_DIR.rglob('*.md'):
    if md_file.name not in ['index.md', 'log.md']:
        pages.append({
            'name': md_file.stem,
            'path': str(md_file),
            'rel_path': str(md_file.relative_to(WIKI_DIR))
        })

print(f'Total pages: {len(pages)}')

query = 'Alchemy'
query_lower = query.lower()

results = []
for p in pages:
    # Check name
    if query_lower in p['name'].lower():
        results.append(p['name'])
        continue
    # Check content
    try:
        content = Path(p['path']).read_text(encoding='utf-8')
        if query_lower in content.lower():
            results.append(p['name'] + ' (content match)')
    except:
        pass

print(f'\nResults for "{query}":')
for r in results[:10]:
    print(f'  - {r}')
