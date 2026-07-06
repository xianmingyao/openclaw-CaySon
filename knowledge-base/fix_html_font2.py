import re
from pathlib import Path

html_path = Path('E:/workspace/knowledge-base/graphify-out/graph.html')
content = html_path.read_text(encoding='utf-8')

# Simply replace all font size 0 with size 14 in the RAW_NODES section
# This regex finds "font": {"size": 0 and replaces the 0 with 14
pattern = r'("font":\s*\{"size":\s*)0(,\s*"color":\s*"#ffffff")'

def replacer(match):
    return match.group(1) + '14' + match.group(2)

content = re.sub(pattern, replacer, content)

# Also add Chinese font face to all font objects
pattern2 = r'("font":\s*\{)"size":\s*14",\s*"color":\s*"#ffffff"(\})'

def replacer2(match):
    return match.group(1) + '"size": 14, "face": "Microsoft YaHei", "color": "#e0e0e0"' + match.group(2)

content = re.sub(pattern2, replacer2, content)

# Write back
html_path.write_text(content, encoding='utf-8')
print(f"Updated HTML: {html_path.stat().st_size / 1024 / 1024:.2f} MB")

# Verify
if b'font' in html_path.read_bytes():
    print("Font settings found in HTML")
