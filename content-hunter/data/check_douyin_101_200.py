import json
import re

# Check the generated douyin 101-200 file
with open("E:\\workspace\\content-hunter\\data\\douyin_101_200.md", "r", encoding="utf-8") as f:
    content = f.read()

count = content.count("### 第")
print(f"Total items in douyin_101_200.md: {count}")

# Check if it's mostly English
lines_with_titles = [l for l in content.split("\n") if l.startswith("- 标题:")]
chinese_count = 0
english_count = 0
for line in lines_with_titles:
    title = line.replace("- 标题: ", "")
    # Check if contains Chinese characters
    if any('\u4e00' <= c <= '\u9fff' for c in title):
        chinese_count += 1
    else:
        english_count += 1

print(f"Chinese titles: {chinese_count}")
print(f"English titles: {english_count}")

# Show some Chinese titles
print("\n--- Sample Chinese titles ---")
for line in lines_with_titles:
    title = line.replace("- 标题: ", "")
    if any('\u4e00' <= c <= '\u9fff' for c in title):
        print(f"  {title[:80]}")

# Now check the bilibili files
with open("E:\\workspace\\content-hunter\\data\\bilibili_101_200_final.md", "r", encoding="utf-8") as f:
    bili_content = f.read()
bili_count = bili_content.count("### 第")
print(f"\nTotal items in bilibili_101_200_final.md: {bili_count}")

# Check existing bilibili.md
with open("E:\\workspace\\content-hunter\\data\\bilibili.md", "r", encoding="utf-8") as f:
    existing_bili = f.read()
existing_count = existing_bili.count("### 第")
print(f"Existing bilibili.md items: {existing_count}")

# Check existing douyin.md
with open("E:\\workspace\\content-hunter\\data\\douyin.md", "r", encoding="utf-8") as f:
    existing_douyin = f.read()
existing_dy_count = existing_douyin.count("### 第")
print(f"Existing douyin.md items: {existing_dy_count}")
