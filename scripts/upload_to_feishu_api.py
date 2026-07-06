#!/usr/bin/env python3
"""使用飞书开放平台API直接上传文档"""
import requests
import json
import os

# 读取文档内容
doc_path = r'E:\workspace\knowledge\千问创享日参会准备清单-2026-04-28.md'
with open(doc_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 飞书 API 配置
# 请替换为你的实际 App ID 和 App Secret
APP_ID = os.environ.get('FEISHU_APP_ID', 'cli_xxxxxxxxxxxxx')
APP_SECRET = os.environ.get('FEISHU_APP_SECRET', 'xxxxxxxxxxxxxxxxxxxx')

# 获取 tenant_access_token
def get_token():
    url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
    headers = {'Content-Type': 'application/json'}
    data = {'app_id': APP_ID, 'app_secret': APP_SECRET}
    resp = requests.post(url, headers=headers, json=data)
    return resp.json().get('tenant_access_token')

# 创建文档
def create_doc(token, title, content):
    # 1. 创建空文档
    url = 'https://open.feishu.cn/open-apis/docx/v1/documents'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {'title': title}
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code != 200:
        print(f"创建文档失败: {resp.text}")
        return None
    doc_data = resp.json()
    doc_token = doc_data.get('data', {}).get('document', {}).get('document_id')
    print(f"文档创建成功, token: {doc_token}")
    return doc_token

# 写入内容块
def write_blocks(token, doc_token, blocks):
    url = f'https://open.feishu.cn/open-apis/docx/v1/documents/{doc_token}/blocks/{doc_token}/children'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # 构建block结构
    block_items = []
    for i, text in enumerate(blocks):
        block = {
            'block_type': 2,  # Text block
            'text': {
                'elements': [{'text_run': {'content': text}}],
                'style': {}
            }
        }
        block_items.append(block)
    
    data = {
        'children': block_items,
        'index': i
    }
    
    resp = requests.post(url, headers=headers, json=data)
    print(f"写入结果: {resp.status_code}")
    return resp.json()

def main():
    print("正在获取访问令牌...")
    token = get_token()
    if not token:
        print("获取token失败，请检查APP_ID和APP_SECRET")
        return
    
    print("正在创建文档...")
    title = '千问创享日参会准备清单-2026-04-28'
    doc_token = create_doc(token, title, content)
    
    if doc_token:
        print(f"\n{'='*50}")
        print(f"文档创建成功!")
        print(f"标题: {title}")
        print(f"链接: https://feishu.cn/docx/{doc_token}")
        print(f"{'='*50}")
        
        # 保存链接
        with open(r'E:\workspace\knowledge\last_feishu_doc.txt', 'w') as f:
            f.write(f"标题: {title}\n链接: https://feishu.cn/docx/{doc_token}")
    else:
        print("文档创建失败")

if __name__ == '__main__':
    main()
