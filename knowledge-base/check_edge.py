import json
g = json.loads(open(r"E:\workspace\knowledge-base\graphify-out\graph.json", encoding="utf-8", errors="replace").read())
print("Sample link:", g["links"][0] if g["links"] else "none")
print("Keys in link:", list(g["links"][0].keys()) if g["links"] else [])
