import json
from collections import Counter

g = json.loads(open(r"E:\workspace\knowledge-base\graphify-out\graph.json", encoding="utf-8", errors="replace").read())
links = g.get("links", [])

# Count edge tuples
edge_tuples = [(l["source"], l["target"]) for l in links]
counter = Counter(edge_tuples)

# Find duplicates
dups = [(s, t, c) for (s, t), c in counter.items() if c > 1]
print(f"Total links: {len(links)}")
print(f"Unique source-target pairs: {len(counter)}")
print(f"Duplicate edges: {len(dups)}")

if dups:
    print("\nTop duplicates:")
    for s, t, c in sorted(dups, key=lambda x: -x[2])[:5]:
        print(f"  {s} -> {t}: {c} times")
