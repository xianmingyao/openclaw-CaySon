import json
from pathlib import Path

graph_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(graph_path, 'r', encoding='utf-8') as f:
    g = json.load(f)

# Check links format
links = g.get('links', [])
print(f"Total links: {len(links)}")

# Find any links without 'target'
missing_target = [l for l in links if 'target' not in l]
missing_source = [l for l in links if 'source' not in l]

print(f"Links missing 'target': {len(missing_target)}")
print(f"Links missing 'source': {len(missing_source)}")

if missing_target:
    print(f"\nSample missing target: {missing_target[0]}")
if missing_source:
    print(f"\nSample missing source: {missing_source[0]}")

# Check if any link has different field names
if links:
    sample = links[0]
    print(f"\nSample link keys: {list(sample.keys())}")
