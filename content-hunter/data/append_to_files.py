"""
Final append script - Add new content to existing bilibili.md and douyin.md
"""
import re

# Read existing files
with open("E:\\workspace\\content-hunter\\data\\bilibili.md", "r", encoding="utf-8") as f:
    bili_existing = f.read()

with open("E:\\workspace\\content-hunter\\data\\douyin.md", "r", encoding="utf-8") as f:
    dy_existing = f.read()

# Read new batch files
with open("E:\\workspace\\content-hunter\\data\\bilibili_101_200_final.md", "r", encoding="utf-8") as f:
    bili_new = f.read()

with open("E:\\workspace\\content-hunter\\data\\douyin_101_200.md", "r", encoding="utf-8") as f:
    dy_new = f.read()

# Count existing items
bili_existing_count = bili_existing.count("### 第")
dy_existing_count = dy_existing.count("### 第")
bili_new_count = bili_new.count("### 第")
dy_new_count = dy_new.count("### 第")

print(f"Bilibili: {bili_existing_count} existing + {bili_new_count} new = {bili_existing_count + bili_new_count}")
print(f"Douyin: {dy_existing_count} existing + {dy_new_count} new = {dy_existing_count + dy_new_count}")

# Append new content to existing
bili_combined = bili_existing + "\n" + bili_new
dy_combined = dy_existing + "\n" + dy_new

# Write combined files
with open("E:\\workspace\\content-hunter\\data\\bilibili.md", "w", encoding="utf-8") as f:
    f.write(bili_combined)

with open("E:\\workspace\\content-hunter\\data\\douyin.md", "w", encoding="utf-8") as f:
    f.write(dy_combined)

# Verify
with open("E:\\workspace\\content-hunter\\data\\bilibili.md", "r", encoding="utf-8") as f:
    bili_verify = f.read()
with open("E:\\workspace\\content-hunter\\data\\douyin.md", "r", encoding="utf-8") as f:
    dy_verify = f.read()

print(f"\nVerification:")
print(f"Bilibili.md final count: {bili_verify.count('### 第')}")
print(f"Douyin.md final count: {dy_verify.count('### 第')}")

print(f"\nFiles updated successfully!")
print(f"bilibili.md: {bili_verify.count('### 第')} items")
print(f"douyin.md: {dy_verify.count('### 第')} items")
