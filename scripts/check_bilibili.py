import os

data_dir = r"E:\workspace\content-hunter-data\data"

files = ["bilibili-ai.md", "bilibili_new_items.md", "bilibili_new_p2.md", "douyin-ai.md"]
for fname in files:
    p = os.path.join(data_dir, fname)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        count = content.count("### 第") + content.count("## ")
        print(f"{fname}: {len(content)} bytes, ~{count} sections")
        print(f"  Preview: {content[:200]}\n")
