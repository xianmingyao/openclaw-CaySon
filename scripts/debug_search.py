# -*- coding: utf-8 -*-
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

from mem0 import Memory
from pymilvus import MilvusClient
import requests

MILVUS_HOST = '8.137.122.11'
MILVUS_PORT = 19530
MILVUS_COLLECTION = 'CaySon_db'
OLLAMA_URL = 'http://localhost:11434'
EMBEDDING_MODEL = 'nomic-embed-text'
LOCAL_CHROMA_PATH = os.path.expanduser('~/.mem0/chroma')
USER_ID = 'ningcaison'

os.environ.pop('OPENAI_API_KEY', None)

config = {
    'vector_store': {'provider': 'chroma', 'config': {'collection_name': 'clawdbot_memories', 'path': LOCAL_CHROMA_PATH}},
    'llm': {'provider': 'ollama', 'config': {'model': 'llama3.2', 'temperature': 0.0, 'ollama_base_url': OLLAMA_URL}},
    'embedder': {'provider': 'ollama', 'config': {'model': EMBEDDING_MODEL, 'ollama_base_url': OLLAMA_URL}}
}
memory_client = Memory.from_config(config)
milvus_client = MilvusClient(uri=f'http://{MILVUS_HOST}:{MILVUS_PORT}')

try:
    milvus_client.load_collection(MILVUS_COLLECTION)
except:
    pass

query = 'AI热点'
local_results = memory_client.search(query, user_id=USER_ID, limit=5)
print(f'Local results type: {type(local_results)}')
print(f'Local results: {local_results}')
