#!/usr/bin/env python
import requests
import json

# Test Ollama embedding
resp = requests.post(
    "http://localhost:11434/api/embeddings",
    json={"model": "nomic-embed-text", "prompt": "test"},
    timeout=30
)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    emb = data.get("embedding", [])
    print(f"Embedding length: {len(emb)}")
    print(f"First 5: {emb[:5]}")
else:
    print(f"Error: {resp.text}")
