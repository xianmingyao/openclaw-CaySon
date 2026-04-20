#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Feishu + Notion sync script - Week 16 2026
Doc 1: GitHub Star Top20 Weekly Report
Doc 2: AI Weekly #440
"""
import os
import json
import time
import requests
from pathlib import Path

# ============ Config ============
FEISHU_BASE_URL = "https://open.feishu.cn/open-apis"
FEISHU_APP_ID = None
FEISHU_APP_SECRET = None
TENANT_ACCESS_TOKEN = None

NOTION_TOKEN = "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"
NOTION_DATABASE_ID = "33d2bb5417c380f6baaff3467dea91c8"
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# ============ Feishu Auth ============
def get_feishu_config():
    global FEISHU_APP_ID, FEISHU_APP_SECRET
    config_path = Path.home() / ".openclaw" / "openclaw.json"
    if config_path.exists():
        config = json.loads(config_path.read_text(encoding='utf-8'))
        feishu_config = config.get('channels', {}).get('feishu', {})
        FEISHU_APP_ID = feishu_config.get('appId')
        FEISHU_APP_SECRET = feishu_config.get('appSecret')

def get_feishu_token():
    global TENANT_ACCESS_TOKEN
    if TENANT_ACCESS_TOKEN:
        return TENANT_ACCESS_TOKEN
    get_feishu_config()
    if not FEISHU_APP_ID or not FEISHU_APP_SECRET:
        print("[FAIL] Feishu config missing")
        return None
    url = f"{FEISHU_BASE_URL}/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, headers={"Content-Type": "application/json"},
        json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}, timeout=10)
    result = resp.json()
    if result.get('code') == 0:
        TENANT_ACCESS_TOKEN = result.get('tenant_access_token')
        print("[OK] Feishu token acquired")
        return TENANT_ACCESS_TOKEN
    print(f"[FAIL] Feishu token failed: {result}")
    return None

# ============ Feishu Doc ============
def create_feishu_doc(title: str) -> str:
    token = get_feishu_token()
    if not token:
        return None
    url = f"{FEISHU_BASE_URL}/docx/v1/documents"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json={"title": title}, timeout=10)
    result = resp.json()
    if result.get('code') == 0:
        doc_id = result.get('data', {}).get('document', {}).get('document_id')
        print(f"[OK] Feishu doc: {title} -> {doc_id}")
        return doc_id
    print(f"[FAIL] Create failed: {result.get('msg')}")
    return None

def md_to_feishu_blocks(markdown: str) -> list:
    blocks = []
    lines = markdown.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].rstrip()
        
        if not line.strip():
            i += 1
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
            content = line[2:]
            blocks.append({
                "block_type": 12,
                "bullet": {
                    "elements": [{"type": "text_run", "text_run": {"content": content}}],
                    "style": {}
                }
            })
        elif line.startswith('**') and line.endswith('**'):
            content = line[2:-2]
            blocks.append({
                "block_type": 2,
                "text": {
                    "elements": [{"type": "text_run", "text_run": {"content": content, "text_run_style": {"bold": True}}}],
                    "style": {}
                }
            })
        else:
            blocks.append({
                "block_type": 2,
                "text": {
                    "elements": [{"type": "text_run", "text_run": {"content": line}}],
                    "style": {}
                }
            })
        i += 1
    
    return blocks

def write_feishu_doc(doc_id: str, markdown: str):
    token = get_feishu_token()
    if not token:
        return False
    blocks = md_to_feishu_blocks(markdown)
    if not blocks:
        print("[WARN] No blocks to write")
        return False
    
    # Get page block id
    resp = requests.get(
        f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks",
        headers={"Authorization": f"Bearer {token}"}, timeout=10)
    try:
        result = resp.json()
        items = result.get('data', {}).get('items', [])
        page_block_id = items[0].get('block_id', doc_id) if items else doc_id
    except:
        page_block_id = doc_id
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{FEISHU_BASE_URL}/docx/v1/documents/{doc_id}/blocks/{page_block_id}/children"
    
    batch_size = 5
    success_count = 0
    for start in range(0, len(blocks), batch_size):
        batch = blocks[start:start+batch_size]
        payload = {"children": batch, "index": -1}
        
        for retry in range(3):
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            try:
                result = resp.json()
                if result.get('code') == 0:
                    success_count += len(batch)
                    break
                elif "frequency limit" in result.get('msg', '').lower():
                    time.sleep(2)
                    continue
            except:
                pass
        time.sleep(0.5)
    
    print(f"[OK] Content written ({success_count}/{len(blocks)} blocks)")
    return success_count > 0

# ============ Notion ============
def notion_headers():
    return {
        'Authorization': f'Bearer {NOTION_TOKEN}',
        'Content-Type': 'application/json',
        'Notion-Version': NOTION_VERSION
    }

def md_to_notion_blocks(markdown: str) -> list:
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
        elif line_stripped.startswith('**') and line_stripped.endswith('**'):
            content = line_stripped[2:-2]
            blocks.append({
                'object': 'block',
                'type': 'paragraph',
                'paragraph': {
                    'rich_text': [{'type': 'text', 'text': {'content': content, 'annotations': {'bold': True}}}]
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

def create_notion_page(title: str, markdown: str) -> str:
    blocks = md_to_notion_blocks(markdown)
    
    url = f"{NOTION_API_URL}/pages"
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "title": {
                "title": [{"text": {"content": title}}]
            }
        },
        "children": blocks
    }
    
    for retry in range(5):
        try:
            resp = requests.post(url, headers=notion_headers(), json=payload, timeout=15)
            result = resp.json()
            if 'id' in result:
                page_id = result['id']
                print(f"[OK] Notion page: {title} -> {page_id}")
                return page_id
            else:
                print(f"[FAIL] Notion failed: {result.get('message', result)}")
                if retry < 4:
                    time.sleep(2)
        except Exception as e:
            print(f"[WARN] Notion error: {e}")
            if retry < 4:
                time.sleep(2)
    
    return None

# ============ Content ============
DOC1_TITLE = "GitHub Star Top20 Weekly Report | Week 16 2026"
DOC1_CONTENT = """# GitHub Star Top20 Weekly Report | Week 16 2026

## Weekly Theme

Hermes Agent / MemPalace / Claude Code continue to heat up

## TOP 10

- hermes-agent (NousResearch) - 102k stars, +38.2k this week | The agent that grows with you
- andrej-karpathy-skills (forrestchang) - 61.3k stars, +45.4k this week | Karpathy's Claude Code guide
- claude-mem (thedotmack) - 63.3k stars, +14.6k this week | Claude session memory plugin
- ai-hedge-fund (virattt) - 56.3k stars | AI quant hedge fund team
- Kronos (shiyu-coder) - 19.6k stars | LLM foundation model for financial markets
- GenericAgent (lsdefine) - 4.5k stars, +3.5k | Self-evolving Agent, 6x lower Token consumption
- evolver (EvoMap) - 5.5k stars, +3.4k | GEP-driven AI Agent evolution engine
- dive-into-llms (Lordog) - 32.5k stars | Hands-on LLM tutorial series
- markitdown (microsoft) - 112.6k stars, +9k this week | Office to Markdown converter
- multica (multica-ai) - 16.7k stars, +7.8k this week | Open source hosted Agent platform

## Weekly Highlights

- Hermes Agent tops the list, +38.2k new this week
- Claude Code ecosystem explodes (karpathy-skills/claude-mem/agent-skills)
- AI Agent self-evolution track rises (Evolver/GenericAgent)
- karpathy-skills: 45.4k new in one week, Karpathy halo effect

## Data Source

Douyin by 扶摇的鱼 | 2026-04-20"""

DOC2_TITLE = "AI Weekly #440 | AI Weekly Roundup (Apr 19)"
DOC2_CONTENT = """# AI Weekly #440 | AI Weekly Roundup (Apr 19)

## Theme: Claude Ends Design

## 12 AI Events

- Claude Design (00:03) - Anthropic launches Claude Design, takes over entire design workflow
- Claude Opus 4.7 (00:26) - Anthropic launches strongest coding model
- Mythos (00:35) - Concept revealed (Claude Mythos series)
- Codex upgrade (00:48) - OpenAI upgrades Codex, fully competes with Claude Code
- AI Video (01:00) - Next-gen AI video model
- GPT-Image-2 (01:15) - OpenAI testing next-gen image model
- Arrow 1.1 (01:28) - Quiver launches strongest vector graphics model
- TokenLight (01:38) - Adobe releases image relighting model
- OmniShow (01:47) - ByteDance open-sources digital human model
- Happy Oyster (02:00) - Alibaba open-sources open world model
- AniGen (02:14) - Researcher open-sources strongest 3D animation model
- Gemini 3.1 Flash TTS (02:21) - Gemini launches strongest TTS model
- Neural Computers (02:33) - Meta develops neural computers

## Key Analysis

- Claude Design: Anthropic releases, design industry game-changer, takes over entire workflow
- Claude Opus 4.7: Strongest coding ability upgraded again
- OpenAI Codex: Fully competes with Claude Code, counterattack
- ByteDance OmniShow: Digital human open source, lowers production barrier
- Alibaba Happy Oyster: Open world model, world simulator track
- Meta Neural Computers: New neural computers track

## Trend Insights

- Anthropic: Design + Opus 4.7, design + coding both covered
- OpenAI: Codex upgrade + GPT-Image-2 testing, defensive counterattack
- Open source ecosystem: Heygen/ByteDance/Alibaba continue open-source arms race
- New track: Neural Computers Neural Computers debuts

## Stats

3225 likes / 78 comments / 1563 bookmarks / 684 shares

## Data Source

Douyin by 产品君 | Posted 2026-04-19 22:27"""

# ============ Main ============
def main():
    print("=" * 50)
    print("Feishu + Notion Sync - Week 16 2026")
    print("=" * 50)
    
    results = {}
    
    # ===== Task 1: Feishu =====
    print("\n[TASK1] Feishu document sync")
    print("-" * 30)
    
    # Doc 1
    print(f"\nCreating doc1: {DOC1_TITLE}")
    doc1_id = create_feishu_doc(DOC1_TITLE)
    if doc1_id:
        time.sleep(1)
        write_feishu_doc(doc1_id, DOC1_CONTENT)
        results['feishu_doc1'] = f"https://feishu.cn/docx/{doc1_id}"
    
    time.sleep(2)
    
    # Doc 2
    print(f"\nCreating doc2: {DOC2_TITLE}")
    doc2_id = create_feishu_doc(DOC2_TITLE)
    if doc2_id:
        time.sleep(1)
        write_feishu_doc(doc2_id, DOC2_CONTENT)
        results['feishu_doc2'] = f"https://feishu.cn/docx/{doc2_id}"
    
    # ===== Task 2: Notion =====
    print("\n[TASK2] Notion sync")
    print("-" * 30)
    
    # Page 1
    print(f"\nCreating page1: {DOC1_TITLE}")
    notion1_id = create_notion_page(DOC1_TITLE, DOC1_CONTENT)
    if notion1_id:
        results['notion_page1'] = f"https://www.notion.so/{NOTION_DATABASE_ID.replace('-', '')}"
    
    time.sleep(2)
    
    # Page 2
    print(f"\nCreating page2: {DOC2_TITLE}")
    notion2_id = create_notion_page(DOC2_TITLE, DOC2_CONTENT)
    if notion2_id:
        results['notion_page2'] = f"https://www.notion.so/{NOTION_DATABASE_ID.replace('-', '')}"
    
    # ===== Summary =====
    print("\n" + "=" * 50)
    print("Sync complete! Summary:")
    print("=" * 50)
    for k, v in results.items():
        print(f"  {k}: {v}")
    
    return results

if __name__ == "__main__":
    main()
