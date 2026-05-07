import json
from pathlib import Path

# Check graph.json structure
graph_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(graph_path, 'r', encoding='utf-8') as f:
    g = json.load(f)

print(f"graph.json nodes: {len(g.get('nodes', []))}")
print(f"graph.json edges: {len(g.get('edges', []))}")

# Sample node
if g.get('nodes'):
    print(f"\nSample node: {g['nodes'][0]}")

# Sample edge (if any)
if g.get('edges'):
    print(f"Sample edge: {g['edges'][0]}")

# Check cache files
cache_dir = Path('E:/workspace/knowledge-base/graphify-out/graphify-out/cache')
all_files = list(cache_dir.glob('*.json'))
print(f"\nCache files: {len(all_files)}")

# Sum up all nodes and edges from cache
total_nodes = 0
total_edges = 0
for f in all_files:
    with open(f, 'r', encoding='utf-8') as fp:
        try:
            d = json.load(fp)
            total_nodes += len(d.get('nodes', []))
            total_edges += len(d.get('edges', []))
        except:
            pass

print(f"Total from cache: {total_nodes} nodes, {total_edges} edges")
