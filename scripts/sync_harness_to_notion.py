#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'E:\workspace\knowledge-base')
from sync_notion import get_notion_token, notion_blocks_from_markdown, create_notion_page
from pathlib import Path

token = get_notion_token()
db_id = '33d2bb5417c380f6baaff3467dea91c8'

# 同步 Harness Engineering 文档
content = Path(r'E:\workspace\knowledge-base\wiki\来源\Harness-Engineering-需求分析-Agent.md').read_text(encoding='utf-8')
blocks = notion_blocks_from_markdown(content)
print(f'Converted to {len(blocks)} Notion blocks')

result = create_notion_page('Harness Engineering 需求分析 Agent 实战指南', blocks, db_id)
print('Result:', result)

page_id = result.get('id') or result.get('page_id', 'unknown')
print(f'Notion URL: https://notion.so/{page_id}')
