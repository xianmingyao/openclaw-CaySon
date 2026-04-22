# -*- coding: utf-8 -*-
import base64
import requests
from pathlib import Path
import json
import time
import re

# Read image
img_path = r'E:\workspace\jingmai_current_screen.png'
img_data = Path(img_path).read_bytes()
img_base64 = base64.b64encode(img_data).decode('utf-8')

# Call Ollama with JSON prompt
url = 'http://localhost:11434/api/generate'
payload = {
    'model': 'qwen3-vl:8b',
    'prompt': '''Analyze this screenshot of a software interface. Find UI elements like buttons or menu items.

You MUST return ONLY valid JSON in this exact format, nothing else:
{"button1": {"x": 100, "y": 200, "w": 80, "h": 30}}

Return empty object {} if you find nothing. Do not write any explanatory text, only JSON.''',
    'images': [img_base64],
    'stream': False
}

print("Calling Ollama with JSON prompt...")
start = time.time()
try:
    response = requests.post(url, json=payload, timeout=25)
    elapsed = time.time() - start
    print(f'Response time: {elapsed:.1f}s')
    print(f'Status: {response.status_code}')

    result = response.json()
    response_text = result.get('response', '')
    print(f'Response: {response_text}')

    # Try to parse as JSON
    try:
        parsed = json.loads(response_text)
        print(f'Parsed JSON: {parsed}')
    except:
        print('Not valid JSON')

        # Try to find JSON in the text
        match = re.search(r'\{[^{}]*\}', response_text)
        if match:
            print(f'Found JSON-like: {match.group()}')

except Exception as e:
    elapsed = time.time() - start
    print(f'Error after {elapsed:.1f}s: {e}')
