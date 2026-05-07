import json
from pathlib import Path

# Load graph.json
json_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(json_path, 'r', encoding='utf-8') as f:
    graph = json.load(f)

print(f"Loaded: {len(graph.get('nodes', []))} nodes, {len(graph.get('links', []))} links")

# NetworkX expects 'edges' but we have 'links' - need to remap
# Or use a direct approach to regenerate HTML

# The safest approach: use graphify's export module directly
import sys
sys.path.insert(0, 'E:/workspace/graphify/graphify')

# Check what's available in export
import graphify.export as export_module
print(f"Available in export: {[x for x in dir(export_module) if not x.startswith('_')]}")

# Try to call to_html
from networkx.readwrite import json_graph

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

# Generate HTML
html_content = export_module.to_html(G, communities, 'E:/workspace/knowledge-base/graphify-out/graph.html')

# Save with UTF-8 BOM for maximum compatibility
output_path = Path('E:/workspace/knowledge-base/graphify-out/graph.html')
output_path.write_text(html_content, encoding='utf-8-sig')  # utf-8-sig adds BOM

print(f"Written: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
