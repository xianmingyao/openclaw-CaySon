import json
from pathlib import Path

html_path = Path('E:/workspace/knowledge-base/graphify-out/graph.html')
content = html_path.read_text(encoding='utf-8')

# Find RAW_NODES line
idx = content.find('const RAW_NODES')
if idx >= 0:
    # Show 500 chars around it
    start = max(0, idx - 50)
    end = min(len(content), idx + 500)
    print(f"Found RAW_NODES at position {idx}")
    print(content[start:end])
else:
    print("RAW_NODES not found")
    # Check for other patterns
    for pattern in ['RAW_NODES', 'RAW_EDGES', 'var nodes', 'var edges']:
        idx = content.find(pattern)
        if idx >= 0:
            print(f"Found '{pattern}' at position {idx}")
