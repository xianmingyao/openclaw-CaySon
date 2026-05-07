import json
import os
from pathlib import Path

cache_dir = Path('E:/workspace/knowledge-base/graphify-out/graphify-out/cache')
chunk_files = sorted(cache_dir.glob('.graphify_chunk_*.json'))
print(f"Chunk files: {len(chunk_files)}")

total_nodes = 0
total_edges = 0
for cf in chunk_files[:3]:
    with open(cf, 'r', encoding='utf-8') as f:
        d = json.load(f)
    print(f"{cf.name}: {len(d.get('nodes', []))} nodes, {len(d.get('edges', []))} edges")
    total_nodes += len(d.get('nodes', []))
    total_edges += len(d.get('edges', []))

print(f"\nTotal so far (first 3): {total_nodes} nodes, {total_edges} edges")

# Check semantic files
semantic_files = sorted(cache_dir.glob('semantic_*.json'))
print(f"\nSemantic files: {len(semantic_files)}")
for sf in semantic_files[:3]:
    with open(sf, 'r', encoding='utf-8') as f:
        d = json.load(f)
    print(f"{sf.name}: {len(d.get('nodes', []))} nodes, {len(d.get('edges', []))} edges")
