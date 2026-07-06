import json
from pathlib import Path

# Check the backup file (original graph.json before fix_links)
json_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json.bak')
with open(json_path, 'r', encoding='utf-8') as f:
    graph = json.load(f)

# Count Chinese nodes
chinese_count = 0
for node in graph.get('nodes', []):
    label = node.get('label', '')
    if any('\u4e00' <= c <= '\u9fff' for c in label):
        chinese_count += 1

print(f"Nodes in backup: {len(graph.get('nodes', []))}")
print(f"Chinese nodes in backup: {chinese_count}")

# Check if 'links' or 'edges'
if 'links' in graph:
    print(f"Edges field: 'links' ({len(graph.get('links', []))})")
elif 'edges' in graph:
    print(f"Edges field: 'edges' ({len(graph.get('edges', []))})")
