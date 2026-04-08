#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""验证知识库上传"""
import requests
from pymilvus import MilvusClient

MILVUS_HOST = "8.137.122.11"
MILVUS_PORT = 19530
OLLAMA_URL = "http://localhost:11434"

client = MilvusClient(uri=f"http://{MILVUS_HOST}:{MILVUS_PORT}")
client.load_collection("CaySon_db")

# 搜索
query = "Karpathy 知识库"
response = requests.post(f"{OLLAMA_URL}/api/embeddings", json={"model": "nomic-embed-text", "prompt": query})
embedding = response.json()["embedding"]

results = client.search(collection_name="CaySon_db", data=[embedding], limit=3, output_fields=["text", "user_id"])

print("Search: Karpathy 知识库")
for r in results[0]:
    entity = r.get("entity", {})
    text = entity.get("text", "N/A")[:100]
    score = r.get("distance", 0)
    print(f"  - score: {score:.4f}")
    print(f"    text: {text}...")
    print()
