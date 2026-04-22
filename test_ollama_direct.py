# -*- coding: utf-8 -*-
import base64
import requests
from pathlib import Path
import json
import time

# Read image
img_path = r'E:\workspace\jingmai_current_screen.png'
img_data = Path(img_path).read_bytes()
img_base64 = base64.b64encode(img_data).decode('utf-8')

print(f"Image size: {len(img_base64)} bytes (base64)")

# Call Ollama directly with a simple prompt
url = 'http://localhost:11434/api/generate'
payload = {
    'model': 'qwen3-vl:8b',
    'prompt': 'Look at this screenshot. What is the main content? Give a brief description in 20 words or less.',
    'images': [img_base64],
    'stream': False
}

print("Calling Ollama...")
start = time.time()
try:
    response = requests.post(url, json=payload, timeout=20)
    elapsed = time.time() - start
    print(f'Response time: {elapsed:.1f}s')
    print(f'Status: {response.status_code}')

    result = response.json()
    response_text = result.get('response', '')
    print(f'Response length: {len(response_text)}')
    print(f'Response: {response_text[:500]}')
except Exception as e:
    elapsed = time.time() - start
    print(f'Error after {elapsed:.1f}s: {e}')
