import base64
import json
import requests

# 截图路径
img_path = r'C:\Users\Administrator\AppData\Local\Temp\jingmai_screenshot_52320_31253.25.png'

with open(img_path, 'rb') as f:
    img_b64 = base64.b64encode(f.read()).decode()

print(f"Image size: {len(img_b64)} chars ({len(img_b64)//1024}KB)")

payload = {
    'model': 'qwen3-vl:8b',
    'prompt': 'Find the publish product button. Return JSON: {"button": {"x": number, "y": number}}',
    'images': [img_b64],
    'stream': False,
    'format': 'text'
}

print('Sending request to Ollama...')
r = requests.post('http://localhost:11434/api/generate', json=payload, timeout=60)
print('Status:', r.status_code)
print('Response:', r.text[:800])
