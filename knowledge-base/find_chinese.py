import json
from pathlib import Path

# Check the HTML for Chinese in a different way
html_path = Path('E:/workspace/knowledge-base/graphify-out/graph.html')
html_bytes = html_path.read_bytes()

# Search for UTF-8 encoded Chinese
# Chinese characters are typically 3 bytes in UTF-8: E[x-y][z-w][z-w]
# E4-B8-AD = 中
# E5-A4-A9 = 天

# Find position of one specific Chinese char
test_label = '自动化脚本'
test_utf8 = test_label.encode('utf-8')
print(f"Looking for: {test_label}")
print(f"UTF-8 bytes: {test_utf8.hex()}")

if test_utf8 in html_bytes:
    print("Found in HTML!")
else:
    print("NOT in HTML")
    
# Try another
test_label2 = '本地知识图谱'
test_utf8_2 = test_label2.encode('utf-8')
print(f"\nLooking for: {test_label2}")
print(f"UTF-8 bytes: {test_utf8_2.hex()}")

if test_utf8_2 in html_bytes:
    print("Found in HTML!")
else:
    print("NOT in HTML")

# Check the graph.json for the same
json_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
json_bytes = json_path.read_bytes()

if test_utf8 in json_bytes:
    print(f"\n{test_label} IS in graph.json")
else:
    print(f"\n{test_label} NOT in graph.json")

if test_utf8_2 in json_bytes:
    print(f"{test_label2} IS in graph.json")
else:
    print(f"{test_label2} NOT in graph.json")
