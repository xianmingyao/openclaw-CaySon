#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import time
sys.path.insert(0, r'E:\workspace\knowledge-base')
from sync_notion import get_notion_token, notion_blocks_from_markdown, create_notion_page
from pathlib import Path

token = get_notion_token()
db_id = '33d2bb5417c380f6baaff3467dea91c8'

# 同步最重要的10个文件
files = [
    'github-top20-2026-week16.md',
    'github-top20-2026-week15.md',
    'github-projects.md',
    'ai-news-2026-04-15.md',
    'ai-news-2026-04-19.md',
    'ELUCKY-account-nurture-plan.md',
    'ELUCKY-agent-task-list.md',
    'behavior-guidelines.md',
    'openclaw-knowledge-system.md',
    'skill-writing-guide.md',
]

for fname in files:
    fpath = Path(rf'E:\workspace\knowledge-base\wiki\来源\{fname}')
    if fpath.exists():
        try:
            content = fpath.read_text(encoding='utf-8')
            blocks = notion_blocks_from_markdown(content)
            result = create_notion_page(fname.replace('.md',''), blocks, db_id)
            print(f'[OK] {fname} -> https://notion.so/{result.get("id", result.get("page_id", "unknown"))}')
            time.sleep(0.5)  # 避免限流
        except Exception as e:
            print(f'[FAIL] {fname}: {e}')
    else:
        print(f'[SKIP] {fname} not found')

print('[DONE]')
