import json
from pathlib import Path

html_path = Path('E:/workspace/knowledge-base/graphify-out/graph.html')
content = html_path.read_text(encoding='utf-8')

# Find a section with Chinese-like characters
# Look for "知识" or other Chinese terms
idx = content.find('知识')
if idx >= 0:
    start = max(0, idx - 100)
    end = min(len(content), idx + 100)
    snippet = content[start:end]
    print(f"Found '知识' at position {idx}")
    print("Raw bytes:", snippet.encode('utf-8')[:200])
    print("\nAs displayed:", snippet)
else:
    print("'知识' not found")

# Check for \u escapes
idx = content.find('\\u')
if idx >= 0:
    print(f"\nFound \\u escape at position {idx}")
    print(content[idx:idx+50])
