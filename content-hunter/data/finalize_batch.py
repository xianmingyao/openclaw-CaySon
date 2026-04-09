"""
Finalize and append batch data to existing files
"""
import json
import re

# Read the batch2 bilibili data
with open("E:\\workspace\\content-hunter\\data\\bilibili_batch2.md", "r", encoding="utf-8") as f:
    batch2_content = f.read()

# Read the 101_200 bilibili data
with open("E:\\workspace\\content-hunter\\data\\bilibili_101_200_final.md", "r", encoding="utf-8") as f:
    final_bili_content = f.read()

# Count items
batch2_items = re.findall(r'### 第(\d+)条', batch2_content)
final_items = re.findall(r'### 第(\d+)条', final_bili_content)

print(f"bilibili_batch2.md: {len(batch2_items)} items")
print(f"bilibili_101_200_final.md: {len(final_items)} items")

# Check existing bilibili.md item count
with open("E:\\workspace\\content-hunter\\data\\bilibili.md", "r", encoding="utf-8") as f:
    bili_content = f.read()
bili_items = re.findall(r'### 第(\d+)条', bili_content)
print(f"bilibili.md existing: {len(bili_items)} items")

# Show what we have in the batch files
print("\n--- bilibili_batch2.md first 5 items ---")
for item in batch2_content.split("### 第")[1:6]:
    print(f"  第{item[:50]}")

print("\n--- bilibili_101_200_final.md first 5 items ---")
for item in final_bili_content.split("### 第")[1:6]:
    print(f"  第{item[:80]}")
