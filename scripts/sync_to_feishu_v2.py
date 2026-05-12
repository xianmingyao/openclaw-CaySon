#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""同步知识库到飞书文档 - 简化版"""
import os
import json
import requests
import time

DOC_ID = "HjOVdDudOoYGycxIHKZcrMoonxe"
FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"

# 获取token
config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
feishu_config = config.get('channels', {}).get('feishu', {})
FEISHU_APP_ID = feishu_config.get('appId')
FEISHU_APP_SECRET = feishu_config.get('appSecret')

resp = requests.post(
    f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal",
    json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
    timeout=30
)
token = resp.json().get('tenant_access_token')
print(f"Token: {token[:20]}...")

# 读取文件
with open('E:/workspace/knowledge-base/wiki/概念/企业AI本体Ontology-从工具到Agent的关键.md', 'r', encoding='utf-8') as f:
    content = f.read()
print(f"Content: {len(content)} chars")

# 简化处理：按段落分割
paragraphs = []
current = []
for line in content.split('\n'):
    if line.strip():
        current.append(line)
    else:
        if current:
            paragraphs.append(' '.join(current))
            current = []
if current:
    paragraphs.append(' '.join(current))

print(f"Paragraphs: {len(paragraphs)}")

# 逐段写入
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
url = f"{FEISHU_BASE_URL}/docx/v1/documents/{DOC_ID}/blocks/children"

success = 0
for i, para in enumerate(paragraphs[:50]):  # 先写50段测试
    if len(para) < 2:
        continue
    
    block = {
        "block_type": 2,
        "text": {
            "elements": [{"type": "text_run", "text_run": {"content": para[:500]}}],
            "style": {}
        }
    }
    
    try:
        resp = requests.post(url, headers=headers, json={"children": [block]}, timeout=15)
        result = resp.json()
        if result.get('code') == 0:
            success += 1
            if success % 10 == 0:
                print(f"  {success} paragraphs written...")
        else:
            print(f"  [{i}] code={result.get('code')}: {result.get('msg', '')[:50]}")
    except Exception as e:
        print(f"  [{i}] Error: {e}")
    
    time.sleep(0.3)  # 避免限流

print(f"\n[OK] {success} paragraphs written")
print(f"Doc: https://feishu.cn/docx/{DOC_ID}")
