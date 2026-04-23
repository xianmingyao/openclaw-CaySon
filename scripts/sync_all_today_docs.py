#!/usr/bin/env python3
"""Sync all today's new docs to all platforms"""
import sys
import os
sys.path.insert(0, r'E:\workspace\knowledge-base')

# Import sync modules
from sync_notion import get_notion_token, notion_blocks_from_markdown, create_notion_page

# Get today's new files
source_dir = r'E:\workspace\knowledge-base\wiki\来源'
files = [f for f in os.listdir(source_dir) if f.endswith('.md')]

# Key files from today
key_files = [
    '产品经理Skills完整指南.md',
    'OpenClaw-24个视频剪辑Skills.md',
    'OpenCode-ClaudeCode-Skills完整指南.md'
]

db_id = '33d2bb5417c380f6baaff3467dea91c8'

print('=== 今日文档五端同步 ===\n')

for fname in key_files:
    fpath = os.path.join(source_dir, fname)
    if not os.path.exists(fpath):
        print(f'[SKIP] {fname} - 文件不存在')
        continue
    
    print(f'[SYNC] {fname}')
    content = open(fpath, 'r', encoding='utf-8').read()
    
    # Notion
    try:
        blocks = notion_blocks_from_markdown(content)
        result = create_notion_page(fname.replace('.md',''), blocks, db_id)
        print(f'  [OK] Notion: {result.get("url", result.get("page_id", "OK"))}')
    except Exception as e:
        print(f'  [FAIL] Notion: {str(e)[:60]}')

print('\n[DONE]')
