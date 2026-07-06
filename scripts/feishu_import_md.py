#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""使用飞书导入API将Markdown文件导入为飞书文档"""
import os
import json
import requests
import time

FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"

# 读取配置
config_path = os.path.expanduser("~/.openclaw/openclaw.json")
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)
feishu_config = config.get('channels', {}).get('feishu', {})
FEISHU_APP_ID = feishu_config.get('appId')
FEISHU_APP_SECRET = feishu_config.get('appSecret')

# 获取token
resp = requests.post(
    f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal",
    json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET},
    timeout=30
)
token = resp.json().get('tenant_access_token')
print(f"[1] Token: {token[:20]}...")

# 读取markdown文件
md_file = 'E:/workspace/knowledge-base/wiki/概念/企业AI本体Ontology-从工具到Agent的关键.md'
with open(md_file, 'r', encoding='utf-8') as f:
    md_content = f.read()
print(f"[2] Markdown: {len(md_content)} chars")

# 写入临时文件
temp_md = 'E:/workspace/temp_kb_import.md'
with open(temp_md, 'w', encoding='utf-8') as f:
    f.write(md_content)
print(f"[3] Temp file: {temp_md}")

# 尝试导入API
# POST /open-apis/drive/v1/import_tasks
# 这个API可以导入多种格式：docx, doc, xlsx, csv, pptx, pdf等
# 注意：飞书导入API可能不支持直接导入markdown格式

headers = {
    "Authorization": f"Bearer {token}"
}

# 方法1：直接用drive import API
# 先检查可用性
print(f"\n[4] Testing import API...")

# 尝试创建导入任务
import_url = f"{FEISHU_BASE_URL}/drive/v1/import_tasks"

# 注意：飞书导入API需要文件上传，不支持直接传内容
# 需要先上传文件到飞书云空间

# 方法2：使用wiki API创建文档
print(f"\n[5] Trying wiki API to create doc with content...")

# 创建文档
new_doc_payload = {
    "title": "企业AI本体Ontology - 从工具到Agent的关键"
}
create_url = f"{FEISHU_BASE_URL}/docx/v1/documents"
resp = requests.post(create_url, headers=headers, json=new_doc_payload, timeout=30)
print(f"Create doc: {resp.status_code}")
print(f"Response: {resp.text[:300]}")

if resp.status_code == 200 and resp.json().get('code') == 0:
    new_doc_id = resp.json().get('data', {}).get('document', {}).get('document_id')
    print(f"\nNew doc: {new_doc_id}")
    
    # 尝试用正确的block API写入
    # 问题可能是需要在folder中创建，而不是直接创建
    print(f"\n[6] Trying block insert with correct params...")
    
    # 使用根block_id插入
    block_url = f"{FEISHU_BASE_URL}/docx/v1/documents/{new_doc_id}/blocks/{new_doc_id}/children"
    
    # 简单文本块
    test_block = {
        "children": [{
            "block_type": 2,
            "text": {
                "elements": [{"type": "text_run", "text_run": {"content": "企业AI本体Ontology"}}],
                "style": {}
            }
        }]
    }
    
    resp = requests.post(block_url, headers=headers, json=test_block, timeout=30)
    print(f"Block insert: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")

print(f"\n[7] Note: Feishu API may require special permissions for block operations")
print(f"Manual option: Copy content to https://feishu.cn/docx/{new_doc_id}")
