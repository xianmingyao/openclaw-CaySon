import json
g = json.loads(open(r"E:\workspace\knowledge-base\graphify-out\graph.json", encoding="utf-8", errors="replace").read())
print(f"Nodes: {len(g['nodes'])}")
print(f"Edges: {len(g['edges'])}")
if g["nodes"]:
    print(f"Sample node: {g['nodes'][0]}")
if g["edges"]:
    print(f"Sample edge: {g['edges'][0]}")
