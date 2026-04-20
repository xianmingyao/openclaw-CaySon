#!/usr/bin/env python
"""
发送内容捕手汇报到飞书用户
"""
import requests, json, sys

# Load config
config = json.load(open('C:/Users/Administrator/.openclaw/openclaw.json'))
feishu = config['channels']['feishu']

# Get fresh token
resp = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': feishu['appId'], 'app_secret': feishu['appSecret']},
    timeout=10)
token = resp.json().get('tenant_access_token')
if not token:
    print('Failed to get token')
    sys.exit(1)
print(f'Token obtained: {token[:30]}...')

# Read report content
report_path = 'E:/workspace/content-hunter-data/report-2026-04-20-1800.md'
with open(report_path, 'r', encoding='utf-8') as f:
    report_content = f.read()

# User ID to send to - ou_ prefix indicates open_id
user_id = 'ou_29ce355d02cb91c7c2f58c8844dc7177'

# Send message using the message API with open_id
send_data = {
    "receive_id": user_id,
    "msg_type": "text",
    "content": json.dumps({"text": report_content})
}

resp3 = requests.post('https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id',
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    },
    json=send_data,
    timeout=10)

result = resp3.json()
print(f'Send result: code={result.get("code")}, msg={result.get("msg")}')
if result.get('code') != 0:
    print(f'Full response: {json.dumps(result, ensure_ascii=False)}')
else:
    print('Message sent successfully!')
