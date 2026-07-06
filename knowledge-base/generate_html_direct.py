import json
from pathlib import Path
import sys
sys.path.insert(0, 'E:/workspace/graphify/graphify')

# Read the original graph.json directly
json_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(json_path, 'r', encoding='utf-8') as f:
    graph = json.load(f)

# Use the export module's to_json function to ensure proper format
from graphify.export import to_json

# Create a backup of current graph.json
import shutil
backup = Path('E:/workspace/knowledge-base/graphify-out/graph.json.backup')
shutil.copy(json_path, backup)

# Save with proper format for to_html
# to_html expects edges in 'edges' field, not 'links'
graph_fixed = dict(graph)
if 'links' in graph_fixed:
    graph_fixed['edges'] = graph_fixed.pop('links')

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(graph_fixed, f, ensure_ascii=False, indent=2)

# Now load and create NetworkX graph
from networkx.readwrite import json_graph
G = json_graph.node_link_graph(graph_fixed)

# Get communities
communities = {}
for node in graph.get('nodes', []):
    cid = node.get('community', 0)
    if cid not in communities:
        communities[cid] = []
    communities[cid].append(node.get('id'))

print(f"NetworkX graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
print(f"Communities: {len(communities)}")

# Generate HTML
output_path = 'E:/workspace/knowledge-base/graphify-out/graph.html'
import graphify.export as export_module
export_module.to_html(G, communities, output_path)

print(f"Generated: {Path(output_path).stat().st_size / 1024 / 1024:.2f} MB")

# Restore original graph.json
shutil.move(backup, json_path)
print("Restored graph.json")
