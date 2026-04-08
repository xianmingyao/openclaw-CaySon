import requests
import json

response = requests.get('http://localhost:11434/api/tags')
data = response.json()
print('Available models:')
for model in data.get('models', []):
    print(f"  - {model.get('name', 'unknown')}")
