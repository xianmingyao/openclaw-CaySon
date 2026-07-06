import json
from pathlib import Path
from collections import defaultdict

# Load graph.json
graph_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(graph_path, 'r', encoding='utf-8') as f:
    g = json.load(f)

print(f"graph.json keys: {list(g.keys())}")
print(f"nodes: {len(g.get('nodes', []))}")
print(f"edges: {len(g.get('edges', []))}")
print(f"hyperedges: {len(g.get('hyperedges', []))}")

# Check cache for edges
cache_dir = Path('E:/workspace/knowledge-base/graphify-out/graphify-out/cache')
all_files = list(cache_dir.glob('*.json'))

# Collect all edges from cache
all_edges = []
for f in all_files:
    with open(f, 'r', encoding='utf-8') as fp:
        try:
            d = json.load(fp)
            all_edges.extend(d.get('edges', []))
        except:
            pass

print(f"\nTotal edges from cache: {len(all_edges)}")
if all_edges:
    print(f"Sample edge from cache: {all_edges[0]}")
