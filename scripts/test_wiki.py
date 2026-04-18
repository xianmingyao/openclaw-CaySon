# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import requests
import json

# Wiki node token from URL
WIKI_TOKEN = "VZaowJKF1iwPRGkUPRucANomn4f"

# Read token from config
TOKEN_FILE = "E:/workspace/.feishu_token"
try:
    FEISHU_APP_ID, FEISHU_APP_SECRET = open(TOKEN_FILE).read().strip().split(',')
except:
    print("Token file not found or invalid")
    sys.exit(1)

# Get tenant access token
resp = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
    timeout=10
)
token = resp.json().get("tenant_access_token")
print(f"Token acquired: {token[:20]}...")

# Try to get wiki node
headers = {"Authorization": f"Bearer {token}"}
try:
    resp = requests.get(
        f"https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={WIKI_TOKEN}",
        headers=headers,
        timeout=10
    )
    print(f"Wiki response: {resp.status_code}")
    print(resp.text[:1000])
except Exception as e:
    print(f"Error: {e}")
