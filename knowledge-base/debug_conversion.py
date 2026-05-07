import json
from pathlib import Path
import sys
sys.path.insert(0, 'E:/workspace/graphify/graphify')

from networkx.readwrite import json_graph

# Load graph.json
json_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(json_path, 'r', encoding='utf-8') as f:
    graph = json.load(f)

# Get Chinese node IDs from original
chinese_nodes_orig = {}
for node in graph.get('nodes', []):
    label = node.get('label', '')
    if any('\u4e00' <= c <= '\u9fff' for c in label):
        chinese_nodes_orig[node['id']] = label

print(f"Chinese nodes in JSON: {len(chinese_nodes_orig)}")

# Convert to NetworkX
graph_fixed = dict(graph)
graph_fixed['edges'] = graph_fixed.pop('links')
G = json_graph.node_link_graph(graph_fixed)

print(f"Nodes in NetworkX: {G.number_of_nodes()}")

# Check which Chinese nodes are in NetworkX
chinese_in_nx = {}
for node_id, label in chinese_nodes_orig.items():
    if node_id in G.nodes():
        chinese_in_nx[node_id] = label

print(f"Chinese nodes in NetworkX: {len(chinese_in_nx)}")

# Find missing
missing_ids = set(chinese_nodes_orig.keys()) - set(G.nodes())
print(f"\nMissing node IDs: {missing_ids}")

# Check if missing nodes have any special property
for node_id in missing_ids:
    # Find the original node
    for n in graph['nodes']:
        if n['id'] == node_id:
            print(f"Missing: {node_id} -> {n}")
            break
