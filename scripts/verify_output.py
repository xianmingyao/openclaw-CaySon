import os

data_dir = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "content-hunter", "data")

for fname in ["bilibili.md", "douyin.md"]:
    p = os.path.join(data_dir, fname)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        items = content.count("### 第")
        print(f"{fname}: {items} items, {len(content)} bytes")
        print(f"  First item: {content[content.find('###'):content.find('###')+200]}")
        print()
