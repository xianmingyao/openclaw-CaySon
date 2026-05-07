import json
from pathlib import Path

# Check the graph.json for correct encoding
json_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(json_path, 'r', encoding='utf-8') as f:
    graph = json.load(f)

# Find a node with Chinese characters
for node in graph.get('nodes', []):
    label = node.get('label', '')
    if any('\u4e00' <= c <= '\u9fff' for c in label):
        print(f"Node with Chinese: {label}")
        print(f"  community_name: {node.get('community_name')}")
        break

# Now check the HTML bytes
html_path = Path('E:/workspace/knowledge-base/graphify-out/graph.html')
with open(html_path, 'rb') as f:
    raw_bytes = f.read(20000)  # first 20KB

# Find the position of RAW_NODES
raw_str = raw_bytes.decode('utf-8', errors='replace')
idx = raw_str.find('Community')
if idx >= 0:
    print(f"\nFirst 'Community' in raw decode: {raw_str[idx:idx+50]}")
    
# Check what encoding was used
print(f"\nFirst 100 bytes (hex): {raw_bytes[:100].hex()}")
print(f"\nFirst 100 bytes (latin1 decode): {raw_bytes[:100].decode('latin1')}")
