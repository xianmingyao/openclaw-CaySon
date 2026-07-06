import json
from pathlib import Path

# Check the graph.json for correct encoding
json_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(json_path, 'r', encoding='utf-8') as f:
    graph = json.load(f)

print(f"Loaded graph.json: {len(graph.get('nodes', []))} nodes")

# The issue: graph.html was saved with wrong encoding
# Solution: regenerate graph.html from graph.json

from graphify.export import to_html

# Load as networkx graph
from networkx.readwrite import json_graph
G = json_graph.node_link_graph(graph)

# Get communities
communities = {}
for node in graph.get('nodes', []):
    cid = node.get('community', 0)
    if cid not in communities:
        communities[cid] = []
    communities[cid].append(node.get('id'))

# Regenerate HTML
html_content = to_html(G, communities, 'E:/workspace/knowledge-base/graphify-out/graph.html')

# Save
output_path = Path('E:/workspace/knowledge-base/graphify-out/graph.html')
output_path.write_text(html_content, encoding='utf-8')

print(f"Regenerated graph.html with correct UTF-8 encoding")
print(f"File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
