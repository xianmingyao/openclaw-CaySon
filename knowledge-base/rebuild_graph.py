import sys
from pathlib import Path

# Add graphify workspace to path FIRST
sys.path.insert(0, 'E:/workspace/graphify')
sys.path.insert(0, 'E:/workspace/graphify/graphify')

import json

# Now import from graphify (workspace version)
from detect import detect
from extract import extract
from build import build
from cluster import cluster
from analyze import analyze
from report import render_report

print('='*60)
print('Graphify - Building Knowledge Graph')
print('='*60)

# 1. Detect
print('\n[1/6] Detecting files...')
result = detect(Path('.'))
print(f'Found: {result["total_files"]} files')

# 2. Collect files
print('\n[2/6] Collecting files...')
all_files = []
for category, files in result.get('files', {}).items():
    for f in files:
        p = Path(f)
        if p.is_file():
            all_files.append(p)

print(f'Processing {len(all_files)} files...')

# 3. Extract
print('\n[3/6] Extracting entities and relationships...')
all_nodes = []
all_edges = []

# Process in batches
batch_size = 30
for i in range(0, len(all_files), batch_size):
    batch = all_files[i:i+batch_size]
    try:
        result = extract(batch)
        nodes = result.get('nodes', [])
        edges = result.get('edges', [])
        all_nodes.extend(nodes)
        all_edges.extend(edges)
        print(f'  Batch {i//batch_size + 1}: {len(nodes)} nodes, {len(edges)} edges')
    except Exception as e:
        print(f'  Error on batch {i//batch_size + 1}: {e}')

print(f'Total: {len(all_nodes)} nodes, {len(all_edges)} edges')

# 4. Build Graph
print('\n[4/6] Building graph...')
G = build({'nodes': all_nodes, 'edges': all_edges})
print(f'Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges')

# 5. Cluster
print('\n[5/6] Clustering...')
communities = cluster(G)
print(f'Communities: {len(communities)}')

# 6. Analyze
print('\n[6/6] Analyzing...')
analysis = analyze(G)

# Create output dir
output_dir = Path('E:/workspace/knowledge-base/graphify-out')
output_dir.mkdir(exist_ok=True)

# Generate JSON graph
print('\nGenerating graph.json...')

# Convert to node-link format for JSON
nodes_data = []
for nid in G.nodes():
    ndata = G.nodes[nid]
    nodes_data.append({
        'id': nid,
        'label': ndata.get('label', nid),
        'community': ndata.get('community', 0),
        'source_file': ndata.get('source_file', ''),
        'file_type': ndata.get('file_type', 'unknown'),
    })

links_data = []
for u, v, edata in G.edges(data=True):
    links_data.append({
        'source': u,
        'target': v,
        'relation': edata.get('relation', ''),
        'confidence': edata.get('confidence', 'EXTRACTED'),
    })

graph_json = {'nodes': nodes_data, 'links': links_data}
json_path = output_dir / 'graph.json'
json_path.write_text(json.dumps(graph_json, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Exported graph.json: {len(nodes_data)} nodes, {len(links_data)} edges')

# Generate HTML
print('Generating graph.html...')

from export import COMMUNITY_COLORS

# Build vis.js nodes
vis_nodes = []
for nid in G.nodes():
    ndata = G.nodes[nid]
    label = ndata.get('label', nid)
    community = ndata.get('community', 0)
    color = COMMUNITY_COLORS[community % len(COMMUNITY_COLORS)]
    degree = G.degree(nid)
    size = 10.0 if degree == 0 else min(10.0 + degree * 0.5, 30.0)
    
    vis_nodes.append({
        'id': nid,
        'label': label,
        'color': {'background': color, 'border': color, 'highlight': {'background': '#ffffff', 'border': color}},
        'size': size,
        'font': {'Size': 14, 'face': 'Microsoft YaHei', 'color': '#e0e0e0'},
        'title': label,
        'community': community,
        'community_name': f'Community {community}',
        'source_file': ndata.get('source_file', ''),
        'file_type': ndata.get('file_type', 'unknown'),
        'degree': degree,
    })

# Build vis.js edges
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

# Build legend
legend_data = []
for cid in sorted(communities.keys()):
    color = COMMUNITY_COLORS[cid % len(COMMUNITY_COLORS)]
    legend_data.append({
        'cid': cid,
        'color': color,
        'label': f'Community {cid}',
        'count': len(communities[cid])
    })

# Generate HTML
html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>Graphify 知识图谱</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0f0f1a; color: #e0e0e0; font-family: "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; display: flex; height: 100vh; overflow: hidden; }}
  #graph {{ flex: 1; }}
  #sidebar {{ width: 280px; background: #1a1a2e; border-left: 1px solid #2a2a4e; display: flex; flex-direction: column; overflow: hidden; }}
  #search-wrap {{ padding: 12px; border-bottom: 1px solid #2a2a4e; }}
  #search {{ width: 100%; background: #0f0f1a; border: 1px solid #3a3a5e; color: #e0e0e0; padding: 7px 10px; border-radius: 6px; font-size: 13px; outline: none; font-family: inherit; }}
  #search:focus {{ border-color: #4E79A7; }}
  #search-results {{ max-height: 140px; overflow-y: auto; padding: 4px 12px; border-bottom: 1px solid #2a2a4e; display: none; }}
  .search-item {{ padding: 4px 6px; cursor: pointer; border-radius: 4px; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
  .search-item:hover {{ background: #2a2a4e; }}
  #info-panel {{ padding: 14px; border-bottom: 1px solid #2a2a4e; min-height: 140px; }}
  #info-panel h3 {{ font-size: 13px; color: #aaa; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em; }}
  #info-content {{ font-size: 13px; color: #ccc; line-height: 1.6; }}
  #info-content .field {{ margin-bottom: 5px; }}
  #info-content .field b {{ color: #e0e0e0; }}
  #info-content .empty {{ color: #555; font-style: italic; }}
  .neighbor-link {{ display: block; padding: 2px 6px; margin: 2px 0; border-radius: 3px; cursor: pointer; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; border-left: 3px solid #333; }}
  .neighbor-link:hover {{ background: #2a2a4e; }}
  #neighbors-list {{ max-height: 160px; overflow-y: auto; margin-top: 4px; }}
  #legend-wrap {{ flex: 1; overflow-y: auto; padding: 12px; }}
  #legend-wrap h3 {{ font-size: 13px; color: #aaa; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.05em; }}
  .legend-item {{ display: flex; align-items: center; gap: 8px; padding: 4px 0; cursor: pointer; border-radius: 4px; font-size: 12px; }}
  .legend-item:hover {{ background: #2a2a4e; padding-left: 4px; }}
  .legend-item.dimmed {{ opacity: 0.35; }}
  .legend-dot {{ width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }}
  .legend-label {{ flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .legend-count {{ color: #666; font-size: 11px; }}
  #stats {{ padding: 10px 14px; border-top: 1px solid #2a2a4e; font-size: 11px; color: #555; }}
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
const LEGEND = {json.dumps(legend_data, ensure_ascii=False)};

function esc(s) {{
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}}

const nodesDS = new vis.DataSet(RAW_NODES);
const edgesDS = new vis.DataSet(RAW_EDGES);

const container = document.getElementById('graph');
const network = new vis.Network(container, {{ nodes: nodesDS, edges: edgesDS }}, {{
  physics: {{ enabled: true, solver: 'forceAtlas2Based', forceAtlas2Based: {{ gravitationalConstant: -60, centralGravity: 0.005, springLength: 120, springConstant: 0.08, damping: 0.4, avoidOverlap: 0.8 }}, stabilization: {{ iterations: 200, fit: true }} }},
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
  document.getElementById('info-content').innerHTML = '<div class="field"><b>'+esc(n.label)+'</b></div><div class="field">类型: '+(n.file_type || 'unknown')+'</div><div class="field">社区: '+esc(n.community_name)+'</div><div class="field">来源: '+(n.source_file || '-')+'</div><div class="field">度数: '+n.degree+'</div>'+(neighborIds.length ? '<div class="field" style="margin-top:8px;color:#aaa;font-size:11px">邻居 ('+neighborIds.length+')</div><div id="neighbors-list">'+neighborItems+'</div>' : '');
}}

function focusNode(nodeId) {{
  network.focus(nodeId, {{ scale: 1.4, animation: true }});
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
  const q = searchInput.value.toLowerCase().trim();
  searchResults.innerHTML = '';
  if (!q) {{ searchResults.style.display = 'none'; return; }}
  const matches = RAW_NODES.filter(n => n.label.toLowerCase().includes(q)).slice(0, 20);
  if (!matches.length) {{ searchResults.style.display = 'none'; return; }}
  searchResults.style.display = 'block';
  matches.forEach(n => {{
    const el = document.createElement('div');
    el.className = 'search-item';
    el.textContent = n.label;
    el.style.borderLeft = '3px solid ' + (n.color && n.color.background || '#333');
    el.style.paddingLeft = '8px';
    el.onclick = () => {{ network.focus(n.id, {{ scale: 1.5, animation: true }}); network.selectNodes([n.id]); showInfo(n.id); searchResults.style.display = 'none'; searchInput.value = ''; }};
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
  cb.className = 'legend-cb';
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

# Write HTML with UTF-8 BOM
html_path = output_dir / 'graph.html'
html_path.write_text(html_content, encoding='utf-8-sig')
size_mb = html_path.stat().st_size / 1024 / 1024
print(f'Generated graph.html: {size_mb:.2f} MB')

# Verify Chinese
if '自动化'.encode('utf-8') in html_path.read_bytes():
    print('[OK] Chinese characters correctly encoded')

print('\n' + '='*60)
print('Done!')
print('='*60)
print(f'Nodes: {G.number_of_nodes()}')
print(f'Edges: {G.number_of_edges()}')
print(f'Communities: {len(communities)}')
