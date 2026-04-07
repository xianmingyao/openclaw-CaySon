#!/usr/bin/env python3
import os

data_dir = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "content-hunter", "data")

for fname in ["bilibili.md", "douyin.md"]:
    p = os.path.join(data_dir, fname)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        items = content.count("### 第")
        # Show first 3 items
        lines = content.split("\n")
        print(f"\n=== {fname}: {items} items, {len(content)} chars ===")
        for i, line in enumerate(lines[:30]):
            if line.strip():
                print(f"  {line.strip()[:100]}")
