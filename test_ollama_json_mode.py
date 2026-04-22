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
    'prompt': '''You are a UI element识别助手. Find the "发布商品" button in this screenshot.

Return ONLY valid JSON, no other text:
{"发布商品": {"position": {"x": number, "y": number}, "confidence": 0.9}}''',
    'images': [img_b64],
    'stream': False,
    'format': 'json'
}

print('Sending request to Ollama with format=json...')
r = requests.post('http://localhost:11434/api/generate', json=payload, timeout=120)
print('Status:', r.status_code)
print('Response:', r.text[:1000])
