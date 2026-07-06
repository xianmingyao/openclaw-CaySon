import json

g = json.loads(open(r"E:\workspace\knowledge-base\graphify-out\graph.json", encoding="utf-8", errors="replace").read())
links = g.get("links", [])

missing_target = 0
missing_source = 0
for link in links:
    if "target" not in link:
        missing_target += 1
    if "source" not in link:
        missing_source += 1

print(f"Total links: {len(links)}")
print(f"Missing 'target': {missing_target}")
print(f"Missing 'source': {missing_source}")

# Check if some links have 'to' instead of 'target'
has_to = sum(1 for l in links if "to" in l)
has_target = sum(1 for l in links if "target" in l)
print(f"Has 'to': {has_to}")
print(f"Has 'target': {has_target}")

# Show some samples
print("\nSample links:")
for l in links[:3]:
    print(f"  {l}")
