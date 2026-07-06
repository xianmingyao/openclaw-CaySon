import json
from pathlib import Path
import re

html_path = Path('E:/workspace/knowledge-base/graphify-out/graph.html')
content = html_path.read_text(encoding='utf-8')

# Fix 1: Update individual node font sizes from 0 to 14
# Pattern: "font": {"size": 0, ...} 
# We need to replace size: 0 with size: 14 and add face: 'Microsoft YaHei'

# Use regex to find and replace font objects in nodes
# The nodes are in the RAW_NODES array

# Find RAW_NODES section
match = re.search(r'const RAW_NODES = (\[.*?\]);', content, re.DOTALL)
if match:
    nodes_json = match.group(1)
    
    # Parse and update
    import json
    nodes = json.loads(nodes_json)
    
    for node in nodes:
        if 'font' in node:
            node['font']['size'] = 14
            node['font']['face'] = 'Microsoft YaHei'
            node['font']['color'] = '#e0e0e0'
    
    # Re-serialize
    new_nodes_json = json.dumps(nodes, ensure_ascii=False)
    
    # Replace in content
    content = content.replace(
        f'const RAW_NODES = {nodes_json};',
        f'const RAW_NODES = {new_nodes_json};'
    )
    
    print(f"Updated {len(nodes)} nodes with Chinese font")
else:
    print("Could not find RAW_NODES")

# Fix 2: Ensure vis.js config has proper font
content = content.replace(
    'nodes: { shape: \'dot\', borderWidth: 1.5, font: { face: \'Microsoft YaHei\', color: \'#e0e0e0\', size: 14 } },',
    'nodes: { shape: \'dot\', borderWidth: 1.5, font: { face: \'Microsoft YaHei\', color: \'#e0e0e0\', size: 14, bold: { enabled: true, size: 16 } } },'
)

# Write back
html_path.write_text(content, encoding='utf-8')
print(f"Updated HTML: {html_path.stat().st_size / 1024 / 1024:.2f} MB")
