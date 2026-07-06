import json
from pathlib import Path
import sys
sys.path.insert(0, 'E:/workspace/graphify/graphify')

from networkx.readwrite import json_graph
import html as _html

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

# Get vis_nodes
vis_nodes = []
for nid in G.nodes():
    ndata = G.nodes[nid]
    label = ndata.get('label', nid)
    community = ndata.get('community', 0)
    
    vis_nodes.append({
        'id': nid,
        'label': label,
        'community': community,
    })

# Find Chinese in vis_nodes
chinese_found = [n for n in vis_nodes if any('\u4e00' <= c <= '\u9fff' for c in n['label'])]
output = []
output.append(f'Total vis_nodes: {len(vis_nodes)}')
output.append(f'vis_nodes with Chinese: {len(chinese_found)}')

# Now check what _js_safe does
def _js_safe(obj) -> str:
    return json.dumps(obj, ensure_ascii=False).replace('</', '<\\/')

nodes_json = _js_safe(vis_nodes)

# Check if Chinese is in nodes_json
test_utf8 = '自动化脚本'.encode('utf-8')
if test_utf8 in nodes_json.encode('utf-8'):
    output.append('\nChinese bytes ARE in nodes_json')
else:
    output.append('\nChinese bytes NOT in nodes_json')
    
# Write first 2000 chars of nodes_json to file
Path('E:/workspace/knowledge-base/debug_nodes_json.txt').write_text(nodes_json[:2000], encoding='utf-8')
output.append('Written first 2000 chars to debug_nodes_json.txt')

# Write to file
Path('E:/workspace/knowledge-base/debug_output.txt').write_text('\n'.join(output), encoding='utf-8')
print('\n'.join(output))
