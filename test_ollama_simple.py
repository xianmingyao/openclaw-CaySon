# -*- coding: utf-8 -*-
import base64
import requests
from pathlib import Path
import time

# Test Ollama with a simple prompt
print('Testing Ollama...')
start = time.time()
response = requests.post(
    'http://localhost:11434/api/generate',
    json={
        'model': 'qwen3-vl:8b',
        'prompt': 'What is shown in this image? Answer in one word.',
        'images': [],
        'stream': False
    },
    timeout=10
)
elapsed = time.time() - start
print('Time: {:.1f}s'.format(elapsed))
print('Status: {}'.format(response.status_code))
print('Response: {}'.format(response.json().get('response', '')[:100]))
