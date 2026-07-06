import json
from collections import defaultdict

g = json.loads(open(r"E:\workspace\knowledge-base\graphify-out\graph.json", encoding="utf-8", errors="replace").read())
links = g.get("links", [])

# Deduplicate: keep first edge for each source-target pair
seen = set()
unique_links = []
for link in links:
    key = (link["source"], link["target"])
    if key not in seen:
        seen.add(key)
        unique_links.append(link)

print(f"Before: {len(links)} links")
print(f"After: {len(unique_links)} links")
print(f"Removed: {len(links) - len(unique_links)} duplicates")

g["links"] = unique_links
open(r"E:\workspace\knowledge-base\graphify-out\graph.json", "w", encoding="utf-8").write(json.dumps(g, indent=2, ensure_ascii=False))
print("Saved!")
