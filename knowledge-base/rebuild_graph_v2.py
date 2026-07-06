import sys
import json
from pathlib import Path

# Use site-packages graphify
from graphify.detect import detect
from graphify.extract import collect_files, extract
from graphify.build import build_from_json, build
from graphify.cluster import cluster
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.export import to_json, to_html

print('='*60)
print('Graphify - Building Knowledge Graph')
print('='*60)

# 1. Detect
print('\n[1/6] Detecting files...')
result = detect(Path('.'))
print(f'Found: {result["total_files"]} files')
print(f'  Code: {len(result.get("files", {}).get("code", []))} files')
print(f'  Docs: {len(result.get("files", {}).get("docs", []))} files')

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
G = build([{'nodes': all_nodes, 'edges': all_edges}])
print(f'Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges')

# 5. Cluster
print('\n[5/6] Clustering...')
communities = cluster(G)
print(f'Communities: {len(communities)}')

# 6. Analyze
print('\n[6/6] Analyzing...')
gn = god_nodes(G)
print(f'God nodes: {len(gn)}')

# Create output dir
output_dir = Path('E:/workspace/knowledge-base/graphify-out')
output_dir.mkdir(exist_ok=True)

# Generate JSON graph
print('\nGenerating graph.json...')
json_data = to_json(G, communities, str(output_dir / 'graph.json'))
print(f'Exported graph.json')

# Generate HTML
print('Generating graph.html...')

from graphify.export import to_html
to_html(G, communities, str(output_dir / 'graph.html'))
print('Generated graph.html')

# Verify
html_bytes = (output_dir / 'graph.html').read_bytes()
if '自动化'.encode('utf-8') in html_bytes:
    print('[OK] Chinese characters correctly encoded')

print('\n' + '='*60)
print('Done!')
print('='*60)
print(f'Nodes: {G.number_of_nodes()}')
print(f'Edges: {G.number_of_edges()}')
print(f'Communities: {len(communities)}')
