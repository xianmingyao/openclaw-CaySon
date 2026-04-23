import json
with open(r'E:\workspace\scripts\magma_memory\sync_state.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
print('Total:', d.get('total', 0))
print('Processed:', len(d.get('processed', [])))
