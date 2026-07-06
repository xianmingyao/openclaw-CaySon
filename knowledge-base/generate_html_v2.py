import json
from pathlib import Path
import sys
sys.path.insert(0, 'E:/workspace/graphify/graphify')

from networkx.readwrite import json_graph

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

# Build vis_nodes
node_data_map = {}
for n in graph['nodes']:
    node_data_map[n['id']] = n

community_colors = [
    "#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F",
    "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC",
]

vis_nodes = []
for nid in G.nodes():
    ndata = G.nodes[nid]
    orig = node_data_map.get(nid, {})
    
    label = ndata.get('label', nid)
    community = ndata.get('community', 0)
    color = community_colors[community % len(community_colors)]
    degree = G.degree(nid)
    size = 10.0 if degree == 0 else min(10.0 + degree * 0.5, 30.0)
    source_file = ndata.get('source_file', orig.get('source_file', ''))
    file_type = ndata.get('file_type', orig.get('file_type', 'unknown'))
    
    vis_nodes.append({
        'id': nid,
        'label': label,
        'color': {'background': color, 'border': color, 'highlight': {'background': '#ffffff', 'border': color}},
        'size': size,
        'font': {'size': 0, 'color': '#ffffff'},
        'title': label,
        'community': community,
        'community_name': f'Community {community}',
        'source_file': source_file,
        'file_type': file_type,
        'degree': degree,
    })

vis_edges = []
for u, v, data in G.edges(data=True):
    relation = data.get('relation', '')
    confidence = data.get('confidence', 'EXTRACTED')
    vis_edges.append({
        'from': u,
        'to': v,
        'title': f'{relation} [{confidence}]',
        'dashes': confidence != 'EXTRACTED',
        'width': 2 if confidence == 'EXTRACTED' else 1,
        'color': {'opacity': 0.7 if confidence == 'EXTRACTED' else 0.35},
    })

legend = []
for cid in sorted(communities.keys()):
    color = community_colors[cid % len(community_colors)]
    legend.append({
        'cid': cid,
        'color': color,
        'label': f'Community {cid}',
        'count': len(communities[cid])
    })

# Serialize
nodes_json = json.dumps(vis_nodes, ensure_ascii=False, indent=2)
edges_json = json.dumps(vis_edges, ensure_ascii=False, indent=2)
legend_json = json.dumps(legend, ensure_ascii=False, indent=2)
stats = f"{G.number_of_nodes()} nodes &middot; {G.number_of_edges()} edges &middot; {len(communities)} communities"

# Read the existing HTML and just update the RAW_NODES, RAW_EDGES, LEGEND and stats
html_path = Path('E:/workspace/knowledge-base/graphify-out/graph.html')
html_content = html_path.read_text(encoding='utf-8')

# Replace the JSON data sections
import re

# Replace RAW_NODES
html_content = re.sub(
    r'const RAW_NODES = \[[\s\S]*?\];',
    f'const RAW_NODES = {nodes_json};',
    html_content,
    count=1
)

# Replace RAW_EDGES
html_content = re.sub(
    r'const RAW_EDGES = \[[\s\S]*?\];',
    f'const RAW_EDGES = {edges_json};',
    html_content,
    count=1
)

# Replace LEGEND
html_content = re.sub(
    r'const LEGEND = \[[\s\S]*?\];',
    f'const LEGEND = {legend_json};',
    html_content,
    count=1
)

# Replace stats
html_content = re.sub(
    r'<div id="stats">[\s\S]*?</div>',
    f'<div id="stats">{stats}</div>',
    html_content,
    count=1
)

# Write back
html_path.write_text(html_content, encoding='utf-8')

print(f"Updated HTML: {html_path.stat().st_size / 1024 / 1024:.2f} MB")

# Verify Chinese
test = '自动化'.encode('utf-8')
if test in html_path.read_bytes():
    print("Chinese IS in HTML!")
else:
    print("Chinese NOT in HTML - ERROR!")
