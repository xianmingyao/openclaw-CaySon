import json
with open('E:/workspace/knowledge-base/graphify-out/graph.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
print(f'Nodes: {len(d.get("nodes", []))}')
print(f'Edges: {len(d.get("edges", []))}')
print(f'Hyperedges: {len(d.get("hyperedges", []))}')
