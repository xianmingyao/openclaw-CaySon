import json
from pathlib import Path
import sys
sys.path.insert(0, 'E:/workspace/graphify/graphify')

from networkx.readwrite import json_graph

# Load graph.json
json_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(json_path, 'r', encoding='utf-8') as f:
    graph = json.load(f)

# Find Chinese nodes BEFORE conversion
chinese_before = set()
for node in graph.get('nodes', []):
    label = node.get('label', '')
    if any('\u4e00' <= c <= '\u9fff' for c in label):
        chinese_before.add(label)

print(f"Chinese nodes BEFORE conversion: {len(chinese_before)}")

# Convert to NetworkX
graph_fixed = dict(graph)
graph_fixed['edges'] = graph_fixed.pop('links')

G = json_graph.node_link_graph(graph_fixed)

print(f"\nNetworkX graph: {G.number_of_nodes()} nodes")

# Find Chinese nodes AFTER conversion
chinese_after = set()
for node_id in G.nodes():
    data = G.nodes[node_id]
    label = data.get('label', node_id)
    if any('\u4e00' <= c <= '\u9fff' for c in label):
        chinese_after.add(label)

print(f"Chinese nodes AFTER conversion: {len(chinese_after)}")

# Find missing
missing = chinese_before - chinese_after
if missing:
    print(f"\nMissing: {missing}")
