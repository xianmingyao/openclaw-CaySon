import os, re, sys

data_dir = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "content-hunter", "data")

for fname in ["bilibili.md", "douyin.md"]:
    p = os.path.join(data_dir, fname)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            c = f.read()
        sections = re.split(r'###\s*第\s*(\d+)\s*条', c)
        count = len(sections) // 2
        print(f"{fname}: {count} items, {len(c)} chars, {os.path.getsize(p)} bytes")
        # Show first 3 items
        print("First item preview:")
        idx = c.find("###")
        if idx >= 0:
            preview = c[idx:idx+300]
            for line in preview.split("\n")[:6]:
                if line.strip():
                    print(f"  {line.strip()[:100]}")
        print()
