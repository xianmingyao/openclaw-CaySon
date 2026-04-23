import json
with open(r'E:\workspace\scripts\magma_memory\magma_graph.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
print('Nodes in graph:', len(d.get('nodes', {})))
print('Edges in graph:', len(d.get('edges', {})))
