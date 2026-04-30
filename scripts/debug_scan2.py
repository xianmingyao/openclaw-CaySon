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

new_files = []
for ext in ['.md', '.txt', '.pdf', '.html']:
    for filepath in RAW_DIR.rglob(f'*{ext}'):
        if filepath.is_file():
            file_hash = get_file_hash(filepath)
            key = str(filepath)
            if key not in processed or processed[key]['hash'] != file_hash:
                new_files.append(filepath)
                print(f'NEW: {key} (hash={file_hash[:8]}...)')

print(f'\nTotal new files found: {len(new_files)}')
