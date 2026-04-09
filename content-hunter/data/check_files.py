import re

# Check existing bilibili.md - how many items
with open("E:\\workspace\\content-hunter\\data\\bilibili.md", "r", encoding="utf-8") as f:
    bili_content = f.read()
bili_count = bili_content.count("### 第")
print(f"Existing bilibili.md: {bili_count} items")

# Check bilibili_101_200_final.md
with open("E:\\workspace\\content-hunter\\data\\bilibili_101_200_final.md", "r", encoding="utf-8") as f:
    bili_new = f.read()
bili_new_count = bili_new.count("### 第")
print(f"bilibili_101_200_final.md: {bili_new_count} items")

# Count Chinese items in new bilibili data
bili_new_titles = re.findall(r'- 标题: (.+)', bili_new)
chinese = sum(1 for t in bili_new_titles if any('\u4e00' <= c <= '\u9fff' for c in t))
print(f"Chinese titles in new bilibili data: {chinese}/{len(bili_new_titles)}")

# Check if bilibili_batch2 has AI content
with open("E:\\workspace\\content-hunter\\data\\bilibili_batch2.md", "r", encoding="utf-8") as f:
    bili_batch2 = f.read()
b2_count = bili_batch2.count("### 第")
print(f"\nbilibili_batch2.md: {b2_count} items")

# Check AI-related in batch2
b2_titles = re.findall(r'- 标题: (.+)', bili_batch2)
ai_keywords = ["AI", "ChatGPT", "DeepSeek", "AIGC", "大模型", "LLM", "人工智能", "机器学习", "神经网络", "Copilot", "Claude", "Gemini", "OpenAI", "文生图"]
ai_count = sum(1 for t in b2_titles for kw in ai_keywords if kw.lower() in t.lower())
print(f"AI-related items in batch2: {ai_count}/{len(b2_titles)}")

# Show first few AI items from batch2
print("\nSample AI titles from batch2:")
count = 0
for t in b2_titles:
    for kw in ai_keywords:
        if kw.lower() in t.lower():
            print(f"  {t[:80]}")
            count += 1
            if count >= 5:
                break
    if count >= 5:
        break

# Check existing douyin.md
with open("E:\\workspace\\content-hunter\\data\\douyin.md", "r", encoding="utf-8") as f:
    dy_content = f.read()
dy_count = dy_content.count("### 第")
print(f"\nExisting douyin.md: {dy_count} items")

# Check the new douyin_101_200.md
with open("E:\\workspace\\content-hunter\\data\\douyin_101_200.md", "r", encoding="utf-8") as f:
    dy_new = f.read()
dy_new_count = dy_new.count("### 第")
print(f"douyin_101_200.md: {dy_new_count} items")
dy_new_titles = re.findall(r'- 标题: (.+)', dy_new)
dy_chinese = sum(1 for t in dy_new_titles if any('\u4e00' <= c <= '\u9fff' for c in t))
print(f"Chinese titles in new douyin data: {dy_chinese}/{len(dy_new_titles)}")
