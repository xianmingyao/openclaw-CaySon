import re

# Check existing douyin.md
with open("E:\\workspace\\content-hunter\\data\\douyin.md", "r", encoding="utf-8") as f:
    content = f.read()

count = content.count("### 第")
print(f"Total items in existing douyin.md: {count}")

# Check language distribution
lines_with_titles = [l for l in content.split("\n") if l.startswith("- 标题: ")]
chinese_count = 0
for line in lines_with_titles:
    title = line.replace("- 标题: ", "")
    if any('\u4e00' <= c <= '\u9fff' for c in title):
        chinese_count += 1

print(f"Chinese titles in existing douyin.md: {chinese_count}")

# Show first 5 Chinese titles
print("\nFirst 5 Chinese titles:")
for line in lines_with_titles[:20]:
    title = line.replace("- 标题: ", "")
    if any('\u4e00' <= c <= '\u9fff' for c in title):
        print(f"  {title[:80]}")
