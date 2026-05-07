import json
from pathlib import Path

graph_path = Path('E:/workspace/knowledge-base/graphify-out/graph.json')
with open(graph_path, 'r', encoding='utf-8') as f:
    g = json.load(f)

links = g.get('links', [])
print(f"Total links before: {len(links)}")

# Fix or remove bad links
fixed_links = []
for l in links:
    if 'target' not in l:
        # Try to use 'label' as target, or skip
        if 'label' in l:
            l['target'] = l['label']
            del l['label']
            fixed_links.append(l)
            print(f"Fixed link: {l}")
        else:
            print(f"Removed bad link: {l}")
    else:
        fixed_links.append(l)

print(f"Total links after: {len(fixed_links)}")

# Save fixed graph
g['links'] = fixed_links
backup_path = graph_path.with_suffix('.json.bak')
graph_path.rename(backup_path)
with open(graph_path, 'w', encoding='utf-8') as f:
    json.dump(g, f, ensure_ascii=False, indent=2)

print(f"\nFixed graph saved to {graph_path}")
print(f"Backup saved to {backup_path}")
