#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r'E:\workspace\knowledge-base')
from sync_notion import get_notion_token, notion_blocks_from_markdown, create_notion_page
from pathlib import Path

token = get_notion_token()
db_id = '33d2bb5417c380f6baaff3467dea91c8'

content = Path(r'E:\workspace\knowledge-base\wiki\来源\github-top20-2026-week16.md').read_text(encoding='utf-8')
blocks = notion_blocks_from_markdown(content)

result = create_notion_page('GitHub TOP20第16周(2026)', blocks, db_id)
print('Result type:', type(result))
print('Result:', result)
