#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""同步CLAUDE.md和Harness文档到飞书"""
import json
import time
import requests
from pathlib import Path

FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"
WIKI_DIR = Path(r'E:\workspace\knowledge-base\wiki\来源')

def get_token():
    try:
        config_path = Path.home() / ".openclaw" / "openclaw.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        feishu = config.get('channels', {}).get('feishu', {})
        url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
        resp = requests.post(url, headers={"Content-Type": "application/json"},
            json={"app_id": feishu.get('appId'), "app_secret": feishu.get('appSecret')}, timeout=10)
        return resp.json().get('tenant_access_token')
    except Exception as e:
        print(f"获取token失败: {e}")
        return None

def create_doc(title: str) -> str:
    token = get_token()
    if not token:
        return None
    try:
        url = f"{FEISHU_BASE_URL}/docx/v1/documents"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        resp = requests.post(url, headers=headers, json={"title": title}, timeout=10)
        data = resp.json()
        if data.get('code') == 0:
            doc_id = data['data']['document']['document_id']
            print(f'[OK] Created: {title} -> {doc_id}')
            return doc_id
        else:
            print(f'[FAIL] {title}: {data}')
            return None
    except Exception as e:
        print(f'[ERROR] {title}: {e}')
        return None

def add_content(doc_id: str, content: str):
    token = get_token()
    if not token:
        return
    try:
        url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        # 简单的段落插入
        resp = requests.post(url, headers=headers, json={
            "children": [{
                "block_type": 2,  # paragraph
                "paragraph": {
                    "elements": [{"type": "text_run", "text_run": {"content": content[:500]}}],
                    "style": {}
                }
            }]
        }, timeout=10)
        print(f'  Content added: {resp.json().get("code")}')
    except Exception as e:
        print(f'  Content error: {e}')

# 同步文档列表
docs = [
    ('CLAUDE.md - AI编程行为准则 v1.1', WIKI_DIR / 'CLAUDE.md'),
    ('Harness Engineering 需求分析Agent实战', WIKI_DIR / 'Harness-Engineering-需求分析-Agent.md'),
]

print('=== 飞书同步 ===')
for title, path in docs:
    if path.exists():
        print(f'\n[SYNC] {title}')
        doc_id = create_doc(title)
        if doc_id:
            content = path.read_text(encoding='utf-8')
            add_content(doc_id, content[:2000])
            print(f'  URL: https://feishu.cn/docx/{doc_id}')
        time.sleep(1)
    else:
        print(f'[SKIP] {title} - file not found')

print('\n[DONE]')
