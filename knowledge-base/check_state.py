import json
state = json.loads(open(r"E:\workspace\knowledge-base\graphify-out\semantic_state.json", encoding="utf-8", errors="replace").read())
print(f"Processed: {len(state['processed'])}/505")
print(f"Nodes: {len(state['all_nodes'])}")
print(f"Edges: {len(state['all_edges'])}")
print(f"Errors: {state['errors']}")
