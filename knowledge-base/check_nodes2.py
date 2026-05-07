import json
from pathlib import Path

# Check graph.json for Chinese nodes
json_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(json_path, 'r', encoding='utf-8') as f:
    graph = json.load(f)

print(f"Nodes in graph.json: {len(graph.get('nodes', []))}")

# Find nodes with Chinese
chinese_nodes = []
for node in graph.get('nodes', []):
    label = node.get('label', '')
    if any('\u4e00' <= c <= '\u9fff' for c in label):
        chinese_nodes.append(node)
        if len(chinese_nodes) <= 5:
            print(f"Chinese node: {label} (community: {node.get('community')})")

print(f"\nTotal Chinese nodes: {len(chinese_nodes)}")

# Now check if these are in the HTML
html_path = Path('E:/workspace/knowledge-base/graphify-out/graph.html')
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Search for the Chinese label in HTML
for node in chinese_nodes[:3]:
    label = node.get('label', '')
    if label in html_content:
        print(f"Found '{label}' in HTML")
    else:
        print(f"NOT found '{label}' in HTML")
