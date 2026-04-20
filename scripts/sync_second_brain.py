import sys
sys.path.insert(0, r'E:\workspace\knowledge-base')
from sync_notion import get_notion_token, notion_blocks_from_markdown, create_notion_page
from pathlib import Path

token = get_notion_token()
db_id = '33d2bb5417c380f6baaff3467dea91c8'

content = Path(r'E:\workspace\knowledge-base\wiki\来源\openclaw-second-brain.md').read_text(encoding='utf-8')
blocks = notion_blocks_from_markdown(content)

result = create_notion_page('AI时代第二大脑-OpenClaw知识库', blocks, db_id)
page_id = result.get('page_id', result.get('id', 'unknown'))
print('Created: https://notion.so/' + page_id)
