import json
g = json.loads(open(r"E:\workspace\knowledge-base\graphify-out\graph.json", encoding="utf-8", errors="replace").read())
print(f"Nodes: {len(g['nodes'])}")
print(f"Links: {len(g['links'])}")
