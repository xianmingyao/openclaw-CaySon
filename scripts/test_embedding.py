#!/usr/bin/env python3
"""Test Ollama embedding"""
import requests

print('Testing Ollama embedding API...')
try:
    r = requests.post('http://localhost:11434/api/embeddings', 
        json={'model':'nomic-embed-text','prompt':'test'}, 
        timeout=120)
    result = r.json()
    if 'embedding' in result:
        print(f'Success! Embedding length: {len(result["embedding"])}')
    else:
        print(f'Response: {result}')
except Exception as e:
    print(f'Failed: {e}')
