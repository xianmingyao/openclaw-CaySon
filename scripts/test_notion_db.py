#!/usr/bin/env python
import requests

with open('E:/workspace/knowledge-base/.notion_token') as f:
    token = f.read().strip()

headers = {
    'Authorization': f'Bearer {token}',
    'Notion-Version': '2022-06-28'
}

db_id = '33d2bb5417c380f6baaff3467dea91c8'
url = f'https://api.notion.com/v1/databases/{db_id}'
resp = requests.get(url, headers=headers, timeout=10)
print(f'Status: {resp.status_code}')
print(f'Message: {resp.json().get("message", "")}')
