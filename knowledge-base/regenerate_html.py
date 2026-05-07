import json
from pathlib import Path
import sys
sys.path.insert(0, 'E:/workspace/graphify/graphify')

from networkx.readwrite import json_graph
import graphify.export as export_module

# Load graph.json
json_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(json_path, 'r', encoding='utf-8') as f:
    graph = json.load(f)

print(f"Loaded: {len(graph.get('nodes', []))} nodes, {len(graph.get('links', []))} links")

# Fix: rename 'links' to 'edges' for NetworkX
graph_fixed = dict(graph)
graph_fixed['edges'] = graph_fixed.pop('links')

G = json_graph.node_link_graph(graph_fixed)
print(f"Created NetworkX graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Get communities
communities = {}
for node in graph.get('nodes', []):
    cid = node.get('community', 0)
    if cid not in communities:
        communities[cid] = []
    communities[cid].append(node.get('id'))

print(f"Communities: {len(communities)}")

# Output path
output_path = str(Path('E:/workspace/knowledge-base/graphify-out/graph.html').resolve())

# Generate HTML - to_html writes directly to file
export_module.to_html(G, communities, output_path)

# Verify the file was written
output_file = Path(output_path)
if output_file.exists():
    size = output_file.stat().st_size / 1024 / 1024
    print(f"Written: {size:.2f} MB")
else:
    print("ERROR: File was not written")
