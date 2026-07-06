import json
from pathlib import Path

graph_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(graph_path, 'r', encoding='utf-8') as f:
    g = json.load(f)

print(f"graph.json:")
print(f"  nodes: {len(g.get('nodes', []))}")
print(f"  links: {len(g.get('links', []))}")  # NetworkX uses 'links' for edges
print(f"  hyperedges: {len(g.get('hyperedges', []))}")

if g.get('links'):
    print(f"\nSample link: {g['links'][0]}")
