# -*- coding: utf-8 -*-
import json
from pathlib import Path

kb_dir = Path('E:/workspace/knowledge-base')
state_file = kb_dir / '.sync_state.json'

data = json.loads(state_file.read_text(encoding='utf-8'))
synced = data.get('synced', {})
failed = data.get('failed', {})

print('Total synced:', len(synced))
print('Total failed:', len(failed))
print()
print('First 5 synced docs:')
for name, info in list(synced.items())[:5]:
    print(f'  {name[:40]}:')
    print(f'    Doc ID: {info.get("doc_id", "N/A")}')
    print(f'    URL: {info.get("url", "N/A")}')
