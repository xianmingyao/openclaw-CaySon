import json
from pathlib import Path

cache_dir = Path('E:/workspace/knowledge-base/graphify-out/graphify-out/cache')
all_files = sorted(cache_dir.glob('*.json'))
print(f"Total files: {len(all_files)}")

total_nodes = 0
total_edges = 0
for f in all_files[:5]:
    with open(f, 'r', encoding='utf-8') as fp:
        try:
            d = json.load(fp)
            nodes = len(d.get('nodes', []))
            edges = len(d.get('edges', []))
            total_nodes += nodes
            total_edges += edges
            print(f"{f.name}: {nodes} nodes, {edges} edges")
        except Exception as e:
            print(f"{f.name}: ERROR - {e}")

print(f"\nFirst 5 files: {total_nodes} nodes, {total_edges} edges")

# Check graph.json
graph_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(graph_path, 'r', encoding='utf-8') as f:
    g = json.load(f)
print(f"\ngraph.json: {len(g.get('nodes', []))} nodes, {len(g.get('edges', []))} edges")
