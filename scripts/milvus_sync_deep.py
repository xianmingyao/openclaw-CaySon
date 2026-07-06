import sys; sys.stdout.reconfigure(encoding='utf-8')
import requests

texts = [
    ('2026052400', 'ByteDance Agent deep interview: MCP adapter layer unifies tool protocol enables pluggable governance extensible tool discovery. MCP is tool-level Ontology defining tool schema and instances.'),
    ('2026052401', 'ByteDance Agent deep: Circuit breaker engineering implementation in LangGraph. max_steps=10, per_call_timeout=30s, total_timeout=300s. Error handling: timeout retry / permission denied / tool not found / business exception.'),
    ('2026052402', 'ByteDance Agent deep: RAG production challenges. Chunk size strategy fixed/semantic/overlap. Recall threshold tuning. rerank model selection. Embedding model choice BGE/M3E/ada-002.'),
    ('2026052403', 'ByteDance Agent deep: Memory system architecture. Short-term: session context window token limited. Long-term: cross-session persistence vector DB. Compression: intelligent(model summarization) + mechanical(rule trim).'),
    ('2026052404', 'ByteDance Agent deep: Multi-agent model routing. Simple tasks small models fast cheap. Complex tasks strong models accurate. Model gateway design: routing load balancing fallback model.'),
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
    print(f'{id_}: code={r.json().get("code")}')
