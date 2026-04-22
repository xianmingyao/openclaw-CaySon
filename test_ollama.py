# -*- coding: utf-8 -*-
import base64
import requests
from pathlib import Path
import json

# Read image
img_path = r'E:\workspace\jingmai_current_screen.png'
img_data = Path(img_path).read_bytes()
img_base64 = base64.b64encode(img_data).decode('utf-8')

# Call Ollama without format parameter
response = requests.post(
    'http://localhost:11434/api/generate',
    json={
        'model': 'qwen3-vl:8b',
        'prompt': 'Please analyze this screenshot. Find UI elements like buttons, menus, or links. Return ONLY valid JSON in this format - no other text: {"element_name": {"position": {"x": 100, "y": 200, "width": 80, "height": 40}, "confidence": 0.9}}. If you find nothing, return empty JSON: {}',
        'images': [img_base64],
        'stream': False
    },
    timeout=30
)

result = response.json()
response_text = result.get('response', '')
print('Response length:', len(response_text))
print('Response:', response_text[:1500])

# Try to parse JSON
try:
    parsed = json.loads(response_text)
    print('Parsed JSON:', parsed)
except json.JSONDecodeError as e:
    print('JSON parse error:', e)
    # Try to find JSON in the response
    start = response_text.find('{')
    end = response_text.rfind('}') + 1
    if start >= 0 and end > start:
        print('Found JSON substring:', response_text[start:end][:500])
