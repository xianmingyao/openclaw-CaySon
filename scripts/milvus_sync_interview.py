import sys; sys.stdout.reconfigure(encoding='utf-8')
import requests

texts = [
    ('2026052300', 'ByteDance Agent interview MCP RAG circuit breaker: MCP adapter layer handles tool protocol parameter validation permission control timeout audit. Source: Douyin 小哲讲面经 2026-05-11.'),
    ('2026052301', 'ByteDance Agent interview: Model writes to DB vs reads from DB. Write: model generates intent+params backend validates. Read: RAG vector retrieval + rerank + generation.'),
    ('2026052302', 'ByteDance Agent interview: Agent modes ReAct Plan-and-Execute Workflow. Closer to production business less free. RAG pipeline: ingestion清洗 chunking embedding retrieval rerank generation.'),
    ('2026052303', 'ByteDance Agent interview: Short-term memory serves current session solves "dont forget this round". Long-term memory serves cross-session solves "remember next time". Compression triggers: token limit / too many turns / new phase. Methods: intelligent(model summarization) + mechanical(rule-based trim).'),
    ('2026052304', 'ByteDance Agent interview: Multi-agent model selection layered. Simple tasks use small models fast cheap. Complex tasks use strong models accurate. Circuit breaker: max steps / per-call timeout / total timeout. Error handling by type.'),
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
