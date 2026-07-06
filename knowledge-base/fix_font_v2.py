import re
from pathlib import Path

html_path = Path('E:/workspace/knowledge-base/graphify-out/graph.html')
content = html_path.read_text(encoding='utf-8')

# The issue is that vis.js font configuration might need a different format
# Let's update the network-level font config to use string format

# Find and replace the nodes config in vis.Network
old_config = "nodes: { shape: 'dot', borderWidth: 1.5, font: { face: 'Microsoft YaHei', color: '#e0e0e0', size: 14 } },"
new_config = "nodes: { shape: 'dot', borderWidth: 1.5, font: { size: 14, face: 'Microsoft YaHei', color: '#e0e0e0', bold: '14px Microsoft YaHei' } },"

content = content.replace(old_config, new_config)

# Also remove per-node font objects that override the network setting
# Pattern: , "font": { "size": 14, "color": "#e0e0e0", "face": "Microsoft YaHei" }
# We want to keep some font settings but maybe simplify

# Actually, let's keep the per-node font but make sure they're using the right format
# Replace all font objects that have the size 0 issue

# Pattern to find font objects in nodes
def replace_font_in_nodes(match):
    font_obj = match.group(0)
    # Replace size: 0 with size: 14
    font_obj = re.sub(r'"size":\s*0', '"size": 14', font_obj)
    # Make sure color is visible
    font_obj = re.sub(r'"color":\s*"#[^"]*"', '"color": "#e0e0e0", "face": "Microsoft YaHei"', font_obj)
    return font_obj

# Find and fix individual node font settings
# The pattern is "font": {"size": X, ...}
pattern = r'"font":\s*\{\s*"size":\s*\d+[^}]*\}'
content = re.sub(pattern, replace_font_in_nodes, content)

# Write back
html_path.write_text(content, encoding='utf-8')
print(f"Updated HTML: {html_path.stat().st_size / 1024 / 1024:.2f} MB")

# Verify the changes
if "Microsoft YaHei" in content:
    print("Microsoft YaHei font is in HTML")
