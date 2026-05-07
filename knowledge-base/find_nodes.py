import json

g = json.loads(open(r"E:\workspace\knowledge-base\graphify-out\graph.json", encoding="utf-8", errors="replace").read())

# Find nodes related to compile
compile_nodes = [n for n in g["nodes"] if "compile" in n["id"].lower()]
web_nodes = [n for n in g["nodes"] if "web" in n["id"].lower()]

print("Compile-related nodes:")
for n in compile_nodes[:5]:
    print(f"  {n}")

print("\nWeb-related nodes:")
for n in web_nodes[:5]:
    print(f"  {n}")
