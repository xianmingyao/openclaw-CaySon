import json
from pathlib import Path

# Load graph.json
json_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(json_path, 'r', encoding='utf-8') as f:
    graph = json.load(f)

# Find Chinese nodes in graph.json
chinese_labels = set()
for node in graph.get('nodes', []):
    label = node.get('label', '')
    if any('\u4e00' <= c <= '\u9fff' for c in label):
        chinese_labels.add(label)

print(f"Chinese nodes in graph.json: {len(chinese_labels)}")

# Check if these labels are in the HTML
html_path = Path('E:/workspace/knowledge-base/graphify-out/graph.html')
html_content = html_path.read_text(encoding='utf-8')

found = 0
not_found = 0
for label in chinese_labels:
    if label in html_content:
        found += 1
    else:
        not_found += 1
        if not_found <= 3:
            print(f"NOT in HTML: {repr(label)}")

print(f"\nFound in HTML: {found}")
print(f"NOT in HTML: {not_found}")

# Check a specific Chinese label more closely
for label in list(chinese_labels)[:3]:
    print(f"\nLabel: {repr(label)}")
    print(f"  In JSON: {label in str(graph.get('nodes', []))}")
