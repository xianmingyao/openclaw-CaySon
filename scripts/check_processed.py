import json
from pathlib import Path

processed_file = Path('E:/workspace/knowledge-base/.processed_files.json')
processed = json.loads(processed_file.read_text(encoding='utf-8'))
print(f'Entries in processed: {len(processed)}')

# Check keys
for k, v in list(processed.items())[:5]:
    print(f'Key: {repr(k)}')
    print(f'  processed: {v.get("processed")}')
    print(f'  hash: {v.get("hash")}')
    print()

# Now check what the script sees
RAW_DIR = Path('E:/workspace/knowledge-base/raw')
for ext in ['.md', '.txt', '.pdf', '.html']:
    count = 0
    for filepath in RAW_DIR.rglob(f'*{ext}'):
        if filepath.is_file():
            key = str(filepath)
            if key in processed:
                count += 1
    print(f'{ext}: {count} files in processed')
