import json
from pathlib import Path

graph_file = Path(r"E:\workspace\knowledge-base\graphify-out\graph.json")
g = json.loads(graph_file.read_text(encoding="utf-8", errors="replace"))

# 转换为 graphify 期望的格式: nodes + links
fixed = {
    "nodes": g["nodes"],
    "links": g["edges"]  # edges -> links
}

graph_file.write_text(json.dumps(fixed, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Fixed: {len(fixed['nodes'])} nodes, {len(fixed['links'])} links")
print("Saved to:", graph_file)
