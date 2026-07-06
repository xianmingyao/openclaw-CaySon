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

# Check first file
test_file = Path('E:/workspace/knowledge-base/raw/README.md')
key = str(test_file)
print(f'Key for README.md: {repr(key)}')
print(f'Key in processed: {key in processed}')
if key in processed:
    print(f'  stored hash: {processed[key]["hash"]}')
    print(f'  current hash: {get_file_hash(test_file)}')
    print(f'  match: {processed[key]["hash"] == get_file_hash(test_file)}')
