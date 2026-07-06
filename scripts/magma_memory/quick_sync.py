#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import io
import re
import hashlib
import json
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, 'E:/workspace/scripts')

from magma_memory.writer import MemoryWriter
from magma_memory.core import MemoryGraph

GRAPH_FILE = Path('E:/workspace/scripts/magma_memory/magma_graph.json')
WIKI_DIR = Path('E:/workspace/knowledge-base/wiki')

files = [f for f in WIKI_DIR.rglob('*.md') if f.name not in {'index.md', 'log.md'}][:200]

graph = MemoryGraph(str(GRAPH_FILE))
writer = MemoryWriter(graph)

print(f'同步 {len(files)} 个文件到图谱...')

for i, f in enumerate(files, 1):
    try:
        content = f.read_text(encoding='utf-8')
        fp = hashlib.md5(content[:200].encode()).hexdigest()[:12]
        title = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title.group(1).strip()[:50] if title else f.stem[:50]
        
        node_id, report = writer.add(
            content=f'【{title}】\n\n{f.name}\n\n{content[:200]}',
            source='wiki-sync',
            keywords=[f'fp:{fp}', f.stem[:20]],
            importance=0.7
        )
        if i % 50 == 0:
            print(f'进度 {i}/{len(files)}')
    except Exception as e:
        print(f'Error: {f.name}: {e}')

graph.save()
print(f'\n完成! 图谱中: {len(graph.nodes)} 条')

with open(GRAPH_FILE) as f:
    data = json.load(f)
print(f'文件保存: {len(data["nodes"])} 条')
