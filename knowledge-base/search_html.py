import json
from pathlib import Path

# Search for ANY Chinese character in the HTML
html_path = Path('E:/workspace/knowledge-base/graphify-out/graph.html')
html_bytes = html_path.read_bytes()

print(f"HTML size: {len(html_bytes) / 1024 / 1024:.2f} MB")

# Search for common Chinese UTF-8 sequences
# 中 = E4 B8 AD
# 国 = E5 9B BD  
# 知 = E7 9F A5
# 识 = E8 AF 86

patterns = [
    (b'\xe4\xb8\xad', '中'),
    (b'\xe5\x9b\xbd', '国'),
    (b'\xe7\x9f\xa5', '知'),
    (b'\xe8\xaf\x86', '识'),
    (b'\xe8\x87\xaa', '自'),
    (b'\xe5\x8a\xa8', '动'),
    (b'\xe5\x8c\x96', '化'),
    (b'\xe6\x9c\xac', '本'),
    (b'\xe5\x9c\xb0', '地'),
]

for pattern, char in patterns:
    count = html_bytes.count(pattern)
    if count > 0:
        print(f"Found '{char}' ({pattern.hex()}): {count} times")

# Search for '自动化' as a sequence
test = '自动化'.encode('utf-8')
count = html_bytes.count(test)
print(f"\n'自动化' ({test.hex()}): {count} times")

# Search for '知识' 
test2 = '知识'.encode('utf-8')
count2 = html_bytes.count(test2)
print(f"'知识' ({test2.hex()}): {count2} times")
