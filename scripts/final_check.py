import os, re

data_dir = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "content-hunter", "data")

for fname in ["bilibili.md", "douyin.md"]:
    p = os.path.join(data_dir, fname)
    if os.path.exists(p):
        raw = open(p, "rb").read()
        text = raw.decode("utf-8", errors="ignore")
        size = len(raw)
        
        # Count properly numbered items
        di_items = len(re.findall(r'###\s+第\s*\d+\s*条', text))
        zhui_items = len(re.findall(r'###\s+追加\s*\d+', text))
        total_h2 = text.count("##")
        
        # Count by splitting
        parts = re.split(r'###\s+', text)
        actual_items = sum(1 for p in parts if p.strip())
        
        print(f"\n=== {fname} ===")
        print(f"File size: {size} bytes")
        print(f"'第X条' items: {di_items}")
        print(f"'追加X' items: {zhui_items}")
        print(f"Total '##' count: {total_h2}")
        print(f"Split by '###': {len(parts)} parts")
        
        # Show first 3 items
        print("\nFirst items:")
        count = 0
        for part in parts[1:6]:  # Skip first empty
            if part.strip() and count < 3:
                lines = part.strip().split('\n')[:3]
                for l in lines:
                    if l.strip():
                        print(f"  {l.strip()[:80]}")
                print()
                count += 1
