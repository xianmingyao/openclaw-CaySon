import json
from pathlib import Path

# Load existing graph.json with full Chinese nodes
json_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

nodes = data['nodes']
links = data['links']
print(f"Loaded: {len(nodes)} nodes, {len(links)} edges")

# Build communities from nodes
communities = {}
for n in nodes:
    cid = n.get('community', 0)
    if cid not in communities:
        communities[cid] = []
    communities[cid].append(n['id'])

# Community colors
COLORS = ["#4E79A7","#F28E2B","#E15759","#76B7B2","#59A14F","#EDC948","#B07AA1","#FF9DA7","#9C755F","#BAB0AC"]

# Build vis.js nodes
vis_nodes = []
for n in nodes:
    nid = n['id']
    label = n.get('label', nid)
    cid = n.get('community', 0)
    color = COLORS[cid % len(COLORS)]
    source = n.get('source_file', '')
    ftype = n.get('file_type', 'unknown')
    
    vis_nodes.append({
        'id': nid,
        'label': label,
        'color': {'background': color, 'border': color, 'highlight': {'background': '#ffffff', 'border': color}},
        'size': 15.0,
        'font': {'size': 14, 'face': 'Microsoft YaHei', 'color': '#e0e0e0'},
        'title': label,
        'community': cid,
        'community_name': f'Community {cid}',
        'source_file': source,
        'file_type': ftype,
    })

# Build vis.js edges
vis_edges = []
for l in links:
    src = l.get('source') or l.get('src')
    tgt = l.get('target') or l.get('tgt')
    if not src or not tgt:
        continue
    rel = l.get('relation', '')
    conf = l.get('confidence', 'EXTRACTED')
    vis_edges.append({
        'from': src,
        'to': tgt,
        'title': f'{rel} [{conf}]',
        'dashes': conf != 'EXTRACTED',
        'width': 1.5,
    })

# Legend
legend = []
for cid in sorted(communities.keys()):
    legend.append({
        'cid': cid,
        'color': COLORS[cid % len(COLORS)],
        'label': f'Community {cid}',
        'count': len(communities[cid])
    })

# HTML
html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>Graphify 知识图谱</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background: #0f0f1a; color: #e0e0e0; font-family: "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; display: flex; height: 100vh; overflow: hidden; }}
#graph {{ flex: 1; }}
#sidebar {{ width: 300px; background: #1a1a2e; border-left: 1px solid #2a2a4e; display: flex; flex-direction: column; overflow: hidden; }}
#search-wrap {{ padding: 12px; border-bottom: 1px solid #2a2a4e; }}
#search {{ width: 100%; background: #0f0f1a; border: 1px solid #3a3a5e; color: #e0e0e0; padding: 8px 12px; border-radius: 6px; font-size: 13px; outline: none; font-family: inherit; }}
#search:focus {{ border-color: #4E79A7; }}
#search-results {{ max-height: 150px; overflow-y: auto; padding: 4px 12px; border-bottom: 1px solid #2a2a4e; display: none; }}
.search-item {{ padding: 5px 8px; cursor: pointer; border-radius: 4px; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; font-family: inherit; }}
.search-item:hover {{ background: #2a2a4e; }}
#info-panel {{ padding: 14px; border-bottom: 1px solid #2a2a4e; min-height: 150px; }}
#info-panel h3 {{ font-size: 12px; color: #888; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.05em; }}
#info-content {{ font-size: 13px; color: #ccc; line-height: 1.6; font-family: inherit; }}
#info-content .field {{ margin-bottom: 6px; }}
#info-content .field b {{ color: #e0e0e0; }}
#info-content .empty {{ color: #555; font-style: italic; }}
.neighbor-link {{ display: block; padding: 3px 8px; margin: 2px 0; border-radius: 3px; cursor: pointer; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; border-left: 3px solid #333; font-family: inherit; }}
.neighbor-link:hover {{ background: #2a2a4e; }}
#neighbors-list {{ max-height: 180px; overflow-y: auto; margin-top: 6px; }}
#legend-wrap {{ flex: 1; overflow-y: auto; padding: 12px; }}
#legend-wrap h3 {{ font-size: 12px; color: #888; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.05em; }}
.legend-item {{ display: flex; align-items: center; gap: 8px; padding: 4px 6px; cursor: pointer; border-radius: 4px; font-size: 12px; }}
.legend-item:hover {{ background: #2a2a4e; }}
.legend-item.dimmed {{ opacity: 0.35; }}
.legend-dot {{ width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }}
.legend-label {{ flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-family: inherit; }}
.legend-count {{ color: #666; font-size: 11px; }}
#stats {{ padding: 10px 14px; border-top: 1px solid #2a2a4e; font-size: 11px; color: #555; font-family: inherit; }}
</style>
</head>
<body>
<div id="graph"></div>
<div id="sidebar">
  <div id="search-wrap">
    <input id="search" type="text" placeholder="搜索节点..." autocomplete="off">
    <div id="search-results"></div>
  </div>
  <div id="info-panel">
    <h3>节点信息</h3>
    <div id="info-content"><span class="empty">点击节点查看详情</span></div>
  </div>
  <div id="legend-wrap">
    <h3>社区</h3>
    <div id="legend"></div>
  </div>
  <div id="stats"></div>
</div>
<script>
const RAW_NODES = {json.dumps(vis_nodes, ensure_ascii=False)};
const RAW_EDGES = {json.dumps(vis_edges, ensure_ascii=False)};
const LEGEND = {json.dumps(legend, ensure_ascii=False)};

function esc(s) {{
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}}

const nodesDS = new vis.DataSet(RAW_NODES);
const edgesDS = new vis.DataSet(RAW_EDGES);
const container = document.getElementById('graph');
const network = new vis.Network(container, {{ nodes: nodesDS, edges: edgesDS }}, {{
  physics: {{ enabled: true, solver: 'forceAtlas2Based', forceAtlas2Based: {{ gravitationalConstant: -80, centralGravity: 0.01, springLength: 150, springConstant: 0.08, damping: 0.4, avoidOverlap: 0.8 }}, stabilization: {{ iterations: 200, fit: true }} }},
  interaction: {{ hover: true, tooltipDelay: 100, hideEdgesOnDrag: true, navigationButtons: false, keyboard: false }},
  nodes: {{ shape: 'dot', borderWidth: 1.5 }},
  edges: {{ smooth: {{ type: 'continuous', roundness: 0.2 }}, selectionWidth: 3 }},
}});
network.once('stabilizationIterationsDone', () => {{ network.setOptions({{ physics: {{ enabled: false }} }}); }});

function showInfo(nodeId) {{
  const n = nodesDS.get(nodeId);
  if (!n) return;
  const neighborIds = network.getConnectedNodes(nodeId);
  const neighborItems = neighborIds.map(nid => {{
    const nb = nodesDS.get(nid);
    const color = nb ? nb.color.background : '#555';
    return '<span class="neighbor-link" style="border-left-color:'+esc(color)+'" onclick="focusNode(\\''+nid+'\\')">'+(nb ? esc(nb.label) : nid)+'</span>';
  }}).join('');
  document.getElementById('info-content').innerHTML = '<div class="field"><b>'+esc(n.label)+'</b></div><div class="field">类型: '+(n.file_type || 'unknown')+'</div><div class="field">社区: '+esc(n.community_name)+'</div><div class="field">来源: '+(n.source_file || '-')+'</div>'+(neighborIds.length ? '<div class="field" style="margin-top:10px;color:#888;font-size:11px">邻居 ('+neighborIds.length+')</div><div id="neighbors-list">'+neighborItems+'</div>' : '');
}}

function focusNode(nodeId) {{
  network.focus(nodeId, {{ scale: 1.5, animation: true }});
  network.selectNodes([nodeId]);
  showInfo(nodeId);
}}

let hoveredNodeId = null;
network.on('hoverNode', params => {{ hoveredNodeId = params.node; container.style.cursor = 'pointer'; }});
network.on('blurNode', () => {{ hoveredNodeId = null; container.style.cursor = 'default'; }});
container.addEventListener('click', () => {{ if (hoveredNodeId !== null) {{ showInfo(hoveredNodeId); network.selectNodes([hoveredNodeId]); }} }});
network.on('click', params => {{ if (params.nodes.length > 0) showInfo(params.nodes[0]); else if (hoveredNodeId === null) document.getElementById('info-content').innerHTML = '<span class="empty">点击节点查看详情</span>'; }});

const searchInput = document.getElementById('search');
const searchResults = document.getElementById('search-results');
searchInput.addEventListener('input', () => {{
  const q = searchInput.value.trim();
  searchResults.innerHTML = '';
  if (!q) {{ searchResults.style.display = 'none'; return; }}
  const matches = RAW_NODES.filter(n => n.label.includes(q) || n.label.toLowerCase().includes(q.toLowerCase())).slice(0, 20);
  if (!matches.length) {{ searchResults.style.display = 'none'; return; }}
  searchResults.style.display = 'block';
  matches.forEach(n => {{
    const el = document.createElement('div');
    el.className = 'search-item';
    el.textContent = n.label;
    el.style.borderLeft = '3px solid ' + (n.color && n.color.background || '#333');
    el.style.paddingLeft = '8px';
    el.onclick = () => {{ focusNode(n.id); searchResults.style.display = 'none'; searchInput.value = ''; }};
    searchResults.appendChild(el);
  }});
}});
document.addEventListener('click', e => {{ if (!searchResults.contains(e.target) && e.target !== searchInput) searchResults.style.display = 'none'; }});

const hiddenCommunities = new Set();
const legendEl = document.getElementById('legend');
LEGEND.forEach(c => {{
  const item = document.createElement('div');
  item.className = 'legend-item';
  const cb = document.createElement('input');
  cb.type = 'checkbox';
  cb.checked = true;
  cb.addEventListener('change', () => {{
    if (cb.checked) {{ hiddenCommunities.delete(c.cid); item.classList.remove('dimmed'); }}
    else {{ hiddenCommunities.add(c.cid); item.classList.add('dimmed'); }}
    nodesDS.update(RAW_NODES.filter(n => n.community === c.cid).map(n => ({{ id: n.id, hidden: hiddenCommunities.has(c.cid) }})));
  }});
  item.innerHTML = '<div class="legend-dot" style="background:'+c.color+'"></div><span class="legend-label">'+c.label+'</span><span class="legend-count">'+c.count+'</span>';
  item.prepend(cb);
  item.onclick = (e) => {{ if (e.target !== cb) {{ cb.checked = !cb.checked; cb.dispatchEvent(new Event('change')); }} }};
  legendEl.appendChild(item);
}});
document.getElementById('stats').textContent = RAW_NODES.length + ' 节点 · ' + RAW_EDGES.length + ' 边 · ' + LEGEND.length + ' 社区';
</script>
</body>
</html>'''

output = Path('E:/workspace/knowledge-base/graphify-out/graph.html')
output.write_text(html, encoding='utf-8-sig')
print(f"Generated: {output.stat().st_size / 1024 / 1024:.2f} MB")
print(f"Nodes: {len(vis_nodes)}, Edges: {len(vis_edges)}, Communities: {len(legend)}")

# Verify Chinese
if '自动化'.encode('utf-8') in output.read_bytes():
    print("OK: Chinese characters present")
