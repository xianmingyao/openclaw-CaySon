#!/usr/bin/env python3
"""测试Ollama嵌入"""
import requests

print('测试 Ollama 嵌入API...')
try:
    r = requests.post('http://localhost:11434/api/embeddings',
        json={'model':'nomic-embed-text','prompt':'test'},
        timeout=60)
    result = r.json()
    if 'embedding' in result:
        print(f'OK! embedding length: {len(result["embedding"])}')
    else:
        print(f'Response: {result}')
except Exception as e:
    print(f'Failed: {e}')
