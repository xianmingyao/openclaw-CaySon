import sys; sys.stdout.reconfigure(encoding='utf-8')
import requests, json

texts = [
    ('2026052201', 'LangGraph hybrid mode: graph.add_node validate workflow_fn for fixed flow; graph.add_node calculate agent_fn for AI decisions. StateGraph enables both Workflow and Agent nodes with state passing.'),
    ('2026052202', 'Ontology safety net for Workflow Agent hybrid: RULE IF Order.amount>1000000 THEN needs_approval=True. Both Workflow nodes and Agent nodes must pass ontology rule check. Enterprise AI = Workflow(stable) + Agent(intelligent) + Ontology(safe).'),
]

url = 'http://8.137.122.11:19530/v2/vectordb/entities/insert'
headers = {'Content-Type': 'application/json'}

for id_, text in texts:
    embed_resp = requests.post('http://localhost:11434/api/embeddings',
        json={'model': 'nomic-embed-text', 'prompt': text}, timeout=30)
    embedding = embed_resp.json()['embedding']
    data = {
        'dbName': 'default', 'collectionName': 'CaySon_db',
        'data': [{'id': id_, 'vector': embedding, 'text': text, 'user_id': 'cayson'}]
    }
    r = requests.post(url, headers=headers, json=data, timeout=15)
    code = r.json().get('code')
    print(f'{id_}: code={code}')
