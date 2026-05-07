import json
from pathlib import Path
import re

html_path = Path('E:/workspace/knowledge-base/graphify-out/graph.html')
content = html_path.read_bytes().decode('utf-8')

# Find RAW_NODES = [ ... ] 
match = re.search(r'const RAW_NODES = (\[)', content)
if match:
    start = match.start()
    # Find the matching closing bracket
    depth = 0
    i = start
    while i < len(content):
        if content[i] == '[':
            depth += 1
        elif content[i] == ']':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
        i += 1
    
    nodes_str = content[start:end]
    print(f"Found RAW_NODES at {start}-{end}, length {len(nodes_str)}")
    
    # Replace font size 0 with 14 and add Chinese font
    # Pattern: "font": {"size": 0, ...}
    def fix_font(match):
        font_content = match.group(0)
        # Replace size: 0 with size: 14
        font_content = re.sub(r'"size":\s*0', '"size": 14', font_content)
        # Replace color #ffffff with #e0e0e0
        font_content = re.sub(r'"color":\s*"#ffffff"', '"color": "#e0e0e0", "face": "Microsoft YaHei"', font_content)
        return font_content
    
    # Match the entire font object
    font_pattern = r'"font":\s*\{[^}]+\}'
    new_nodes_str = re.sub(font_pattern, fix_font, nodes_str)
    
    # Check if changes were made
    if '"size": 14' in new_nodes_str:
        print("Font sizes updated!")
    
    # Replace in content
    new_content = content[:start] + new_nodes_str + content[end:]
    
    # Write back
    html_path.write_text(new_content, encoding='utf-8')
    print(f"Updated HTML: {html_path.stat().st_size / 1024 / 1024:.2f} MB")
else:
    print("RAW_NODES not found")
