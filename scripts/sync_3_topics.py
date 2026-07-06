# -*- coding: utf-8 -*-
"""Sync 3 topics to Feishu and Notion"""

import os
import sys
import json
import time
import requests

# ============ FEISHU CONFIG ============
FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"
FEISHU_APP_ID = None
FEISHU_APP_SECRET = None
TENANT_ACCESS_TOKEN = None
FEISHU_FOLDER_TOKEN = "33d2bb5417c380f6baaff3467dea91c8"  # Database ID provided

# ============ NOTION CONFIG ============
NOTION_TOKEN_FILE = r"E:\workspace\knowledge-base\.notion_token"
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
NOTION_DATABASE_ID = "33d2bb5417c380f6baaff3467dea91c8"


def get_feishu_config():
    global FEISHU_APP_ID, FEISHU_APP_SECRET
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    if os.path.exists(config_path):
        with open(config_path, encoding='utf-8') as f:
            config = json.load(f)
        feishu_config = config.get('channels', {}).get('feishu', {})
        FEISHU_APP_ID = feishu_config.get('appId')
        FEISHU_APP_SECRET = feishu_config.get('appSecret')


def get_tenant_access_token():
    global TENANT_ACCESS_TOKEN
    if TENANT_ACCESS_TOKEN:
        return TENANT_ACCESS_TOKEN
    get_feishu_config()
    if not FEISHU_APP_ID or not FEISHU_APP_SECRET:
        return None
    url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, headers={"Content-Type": "application/json"},
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}, timeout=10)
    result = resp.json()
    if result.get('code') == 0:
        TENANT_ACCESS_TOKEN = result.get('tenant_access_token')
        return TENANT_ACCESS_TOKEN
    return None


def create_feishu_doc(title, content, folder_token=None):
    """Create a Feishu doc and write content to it"""
    token = get_tenant_access_token()
    if not token:
        return {'success': False, 'error': 'No token'}

    # Create document
    url = f"{FEISHU_BASE_URL}/docx/v1/documents"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    resp = requests.post(url, headers=headers, json={"title": title}, timeout=10)
    result = resp.json()

    if result.get('code') != 0:
        return {'success': False, 'error': result.get('msg')}

    doc_id = result.get('data', {}).get('document', {}).get('document_id')
    print(f"   [FEISHU] Doc created: {doc_id}")

    # Get page block id
    resp = requests.get(
        f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks",
        headers={"Authorization": f"Bearer {token}"}, timeout=10)
    try:
        result_data = resp.json()
        items = result_data.get('data', {}).get('items', [])
        page_block_id = items[0].get('block_id', doc_id) if items else doc_id
    except:
        page_block_id = doc_id

    # Convert markdown to blocks and write
    blocks = markdown_to_feishu_blocks(content)
    write_result = write_blocks(doc_id, page_block_id, blocks)

    return {
        'success': write_result,
        'doc_id': doc_id,
        'url': f"https://feishu.cn/docx/{doc_id}"
    }


def markdown_to_feishu_blocks(markdown):
    """Convert markdown to Feishu blocks"""
    blocks = []
    lines = markdown.split('\n')

    for line in lines:
        line = line.rstrip()
        if not line.strip():
            continue

        if line.startswith('# '):
            blocks.append({
                "block_type": 3,
                "heading1": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[2:]}}],
                    "style": {}
                }
            })
        elif line.startswith('## '):
            blocks.append({
                "block_type": 4,
                "heading2": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[3:]}}],
                    "style": {}
                }
            })
        elif line.startswith('### '):
            blocks.append({
                "block_type": 5,
                "heading3": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[4:]}}],
                    "style": {}
                }
            })
        elif line.startswith('- '):
            blocks.append({
                "block_type": 12,
                "bullet": {
                    "elements": [{"type": "text_run", "text_run": {"content": line[2:]}}],
                    "style": {}
                }
            })
        elif line.startswith('>'):
            blocks.append({
                "block_type": 12,
                "bullet": {
                    "elements": [{"type": "text_run", "text_run": {"content": "  " + line[1:].strip()}}],
                    "style": {}
                }
            })
        elif line.startswith('```'):
            blocks.append({
                "block_type": 12,
                "bullet": {
                    "elements": [{"type": "text_run", "text_run": {"content": "[代码块]"}}],
                    "style": {}
                }
            })
        elif line.startswith('---') or line.startswith('***'):
            continue
        elif line.startswith('|'):
            # Table row - convert to text
            clean = line.replace('|', ' | ').strip()
            if clean and len(clean) < 500:
                blocks.append({
                    "block_type": 2,
                    "text": {
                        "elements": [{"type": "text_run", "text_run": {"content": clean}}],
                        "style": {}
                    }
                })
        else:
            clean = line.strip()
            if clean and len(clean) < 2000:
                blocks.append({
                    "block_type": 2,
                    "text": {
                        "elements": [{"type": "text_run", "text_run": {"content": clean}}],
                        "style": {}
                    }
                })

    return blocks


def write_blocks(doc_id, page_block_id, blocks):
    """Write blocks to Feishu doc"""
    token = get_tenant_access_token()
    if not token:
        return False

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{page_block_id}/children"

    batch_size = 10
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i+batch_size]
        payload = {"children": batch, "index": -1}

        for retry in range(3):
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            try:
                result = resp.json()
                if result.get('code') == 0:
                    break
                elif "frequency limit" in result.get('msg', '').lower():
                    time.sleep(2)
                    continue
                else:
                    print(f"   [FEISHU] Write error: {result.get('msg')}")
                    break
            except Exception as e:
                print(f"   [FEISHU] Write exception: {e}")
                break

        time.sleep(0.5)

    return True


# ============ NOTION FUNCTIONS ============

def get_notion_token():
    if os.path.exists(NOTION_TOKEN_FILE):
        return open(NOTION_TOKEN_FILE, encoding='utf-8').read().strip()
    return os.environ.get('NOTION_API_TOKEN', '')


def get_notion_headers():
    token = get_notion_token()
    if not token:
        return None
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Notion-Version': NOTION_VERSION
    }


def notion_blocks_from_markdown(markdown):
    """Convert markdown to Notion blocks"""
    blocks = []
    lines = markdown.split('\n')

    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue

        if line_stripped.startswith('# '):
            blocks.append({
                'object': 'block',
                'type': 'heading_1',
                'heading_1': {
                    'rich_text': [{'type': 'text', 'text': {'content': line_stripped[2:]}}]
                }
            })
        elif line_stripped.startswith('## '):
            blocks.append({
                'object': 'block',
                'type': 'heading_2',
                'heading_2': {
                    'rich_text': [{'type': 'text', 'text': {'content': line_stripped[3:]}}]
                }
            })
        elif line_stripped.startswith('### '):
            blocks.append({
                'object': 'block',
                'type': 'heading_3',
                'heading_3': {
                    'rich_text': [{'type': 'text', 'text': {'content': line_stripped[4:]}}]
                }
            })
        elif line_stripped.startswith('- '):
            blocks.append({
                'object': 'block',
                'type': 'bulleted_list_item',
                'bulleted_list_item': {
                    'rich_text': [{'type': 'text', 'text': {'content': line_stripped[2:]}}]
                }
            })
        elif line_stripped.startswith('>'):
            blocks.append({
                'object': 'block',
                'type': 'quote',
                'quote': {
                    'rich_text': [{'type': 'text', 'text': {'content': line_stripped[1:].strip()}}]
                }
            })
        elif line_stripped.startswith('```'):
            continue
        else:
            if len(line_stripped) > 2000:
                for i in range(0, len(line_stripped), 2000):
                    blocks.append({
                        'object': 'block',
                        'type': 'paragraph',
                        'paragraph': {
                            'rich_text': [{'type': 'text', 'text': {'content': line_stripped[i:i+2000]}}]
                        }
                    })
            else:
                blocks.append({
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [{'type': 'text', 'text': {'content': line_stripped}}]
                    }
                })

    return blocks


def create_notion_page(title, blocks, parent_id=None):
    """Create a Notion page"""
    headers = get_notion_headers()
    if not headers:
        return {'success': False, 'error': 'No token'}

    if not parent_id:
        parent_id = NOTION_DATABASE_ID

    if not parent_id:
        return {'success': False, 'error': 'No database ID'}

    url = f"{NOTION_API_URL}/pages"
    data = {
        'parent': {'database_id': parent_id},
        'properties': {
            '标题': {
                'title': [{'type': 'text', 'text': {'content': title}}]
            }
        },
        'children': blocks[:100]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        result = response.json()

        if response.status_code == 200:
            page_id = result.get('id')
            return {
                'success': True,
                'page_id': page_id,
                'url': f"https://notion.so/{page_id.replace('-', '')}"
            }
        else:
            return {
                'success': False,
                'error': result.get('message', 'Unknown error'),
                'code': response.status_code
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def main():
    # Read content
    content_file = r"E:\workspace\knowledge\temp_sync_content.json"
    if not os.path.exists(content_file):
        print(f"[ERROR] Content file not found: {content_file}")
        return

    with open(content_file, encoding='utf-8') as f:
        docs = json.load(f)

    print("=" * 60)
    print("SYNC 3 TOPICS TO FEISHU + NOTION")
    print("=" * 60)

    feishu_results = []
    notion_results = []

    for i, doc in enumerate(docs):
        title = doc['title']
        content = doc['content']

        print(f"\n[{i+1}/3] {title}")
        print("-" * 50)

        # Create Feishu doc
        print("   [FEISHU] Creating...")
        feishu_result = create_feishu_doc(title, content, FEISHU_FOLDER_TOKEN)
        if feishu_result.get('success'):
            print(f"   [FEISHU] SUCCESS: {feishu_result.get('url')}")
        else:
            print(f"   [FEISHU] FAILED: {feishu_result.get('error')}")
        feishu_results.append({'title': title, **feishu_result})

        time.sleep(1)

        # Create Notion page
        print("   [NOTION] Creating...")
        blocks = notion_blocks_from_markdown(content)
        notion_result = create_notion_page(title, blocks, NOTION_DATABASE_ID)
        if notion_result.get('success'):
            print(f"   [NOTION] SUCCESS: {notion_result.get('url')}")
        else:
            print(f"   [NOTION] FAILED: {notion_result.get('error')}")
        notion_results.append({'title': title, **notion_result})

        time.sleep(1)

    # Save results
    all_results = {
        'feishu': feishu_results,
        'notion': notion_results
    }
    output_file = r"E:\workspace\knowledge\sync_3_topics_results.json"
    with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
        json.dump(all_results, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    feishu_success = sum(1 for r in feishu_results if r.get('success'))
    notion_success = sum(1 for r in notion_results if r.get('success'))

    print(f"\n📄 FEISHU: {feishu_success}/3")
    for r in feishu_results:
        status = "✅" if r.get('success') else "❌"
        print(f"   {status} {r['title']}")
        if r.get('url'):
            print(f"      {r['url']}")

    print(f"\n📝 NOTION: {notion_success}/3")
    for r in notion_results:
        status = "✅" if r.get('success') else "❌"
        print(f"   {status} {r['title']}")
        if r.get('url'):
            print(f"      {r['url']}")

    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    main()
