import json
from pathlib import Path

# Check the new HTML for correct UTF-8 encoding
html_path = Path('E:/workspace/knowledge-base/graphify-out/graph.html')

# Read as binary to check encoding
with open(html_path, 'rb') as f:
    raw = f.read()

print(f"File size: {len(raw) / 1024 / 1024:.2f} MB")

# Check for BOM
if raw.startswith(b'\xef\xbb\xbf'):
    print("UTF-8 BOM found")
elif raw.startswith(b'\xff\xfe'):
    print("UTF-16 LE BOM found")
else:
    print("No BOM - using UTF-8 without BOM")

# Decode as UTF-8
try:
    content = raw.decode('utf-8')
    print("UTF-8 decode: SUCCESS")
    
    # Check for Chinese characters
    chinese_found = False
    for i, c in enumerate(content):
        if '\u4e00' <= c <= '\u9fff':
            if not chinese_found:
                print(f"First Chinese char at position {i}: '{c}'")
                chinese_found = True
    
    if not chinese_found:
        print("No Chinese characters found")
    else:
        # Find a node with Chinese name
        idx = content.find('知识')
        if idx >= 0:
            print(f"\nFound '知识' at {idx}: ...{content[idx-20:idx+30]}...")
        
except UnicodeDecodeError as e:
    print(f"UTF-8 decode FAILED: {e}")
    
    # Try latin1
    content = raw.decode('latin1')
    print("Latin1 decode: SUCCESS (but may have mojibake)")
