import json
import hashlib
from pathlib import Path

def get_file_hash(filepath):
    md5 = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()
    except:
        return ""

RAW_DIR = Path('E:/workspace/knowledge-base/raw')
PROCESSED_FILE = Path('E:/workspace/knowledge-base/.processed_files.json')

processed = json.loads(PROCESSED_FILE.read_text(encoding='utf-8'))
print(f'Entries in processed: {len(processed)}')

# Count files by extension
total_by_ext = {}
in_processed_by_ext = {}
new_by_ext = {}

for ext in ['.md', '.txt', '.pdf', '.html']:
    total_by_ext[ext] = 0
    in_processed_by_ext[ext] = 0
    new_by_ext[ext] = 0

for filepath in RAW_DIR.rglob('*'):
    if filepath.is_file():
        ext = filepath.suffix.lower()
        if ext in total_by_ext:
            total_by_ext[ext] += 1
            key = str(filepath)
            if key in processed:
                in_processed_by_ext[ext] += 1
                # Check hash
                current_hash = get_file_hash(filepath)
                stored_hash = processed[key]['hash']
                if current_hash != stored_hash:
                    print(f'HASH MISMATCH: {key}')
                    print(f'  stored: {stored_hash}')
                    print(f'  current: {current_hash}')
            else:
                new_by_ext[ext] += 1

print('\nSummary:')
for ext in ['.md', '.txt', '.pdf', '.html']:
    print(f'{ext}: total={total_by_ext[ext]}, in_processed={in_processed_by_ext[ext]}, new(not in processed)={new_by_ext[ext]}')
