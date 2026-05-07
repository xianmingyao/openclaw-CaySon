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

# Convert to NetworkX
graph_fixed = dict(graph)
graph_fixed['edges'] = graph_fixed.pop('links')
G = json_graph.node_link_graph(graph_fixed)

# Get communities
communities = {}
for node in graph.get('nodes', []):
    cid = node.get('community', 0)
    if cid not in communities:
        communities[cid] = []
    communities[cid].append(node.get('id'))

# Get communities as a dict with list
communities_list = {cid: [] for cid in communities}
for node in graph.get('nodes', []):
    cid = node.get('community', 0)
    communities_list[cid].append(node.get('id'))

# Test generate_html directly
from io import StringIO
import json as json_module

# Manually call what to_html does
def generate_test_html(G, communities, output_path):
    # Get node data for vis.js
    nodes = []
    for nid in G.nodes():
        ndata = G.nodes[nid]
        label = ndata.get('label', nid)
        nodes.append({
            'id': nid,
            'label': label,
            'community': ndata.get('community', 0),
        })
    
    # Check for Chinese in first 10 nodes
    for n in nodes[:20]:
        label = n['label']
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in label)
        if has_chinese:
            print(f"Chinese node: {n['id']} -> {label}")
    
    print(f"\nTotal nodes: {len(nodes)}")
    chinese_count = sum(1 for n in nodes if any('\u4e00' <= c <= '\u9fff' for c in n['label']))
    print(f"Chinese nodes: {chinese_count}")

generate_test_html(G, communities_list, 'test.html')
