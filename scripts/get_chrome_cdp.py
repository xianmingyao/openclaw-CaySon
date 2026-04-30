import urllib.request
import json

try:
    url = "http://localhost:9222/json"
    response = urllib.request.urlopen(url, timeout=5)
    data = json.loads(response.read().decode())
    for page in data:
        print(f"Title: {page.get('title', 'N/A')}")
        print(f"URL: {page.get('url', 'N/A')}")
        print(f"ID: {page.get('id', 'N/A')}")
        print("---")
except Exception as e:
    print(f"Error: {e}")
