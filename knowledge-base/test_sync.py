#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sync_feishu import create_doc, write_blocks, markdown_to_blocks, load_wiki_files, read_wiki_content

files = load_wiki_files()
print(f'Found {len(files)} files')

# 只同步前3个
for wiki_file in files[:3]:
    doc_data = read_wiki_content(wiki_file)
    title = doc_data['title']
    content = doc_data['content']
    
    print(f'Processing: {title}')
    
    create_result = create_doc(title)
    if create_result.get('success'):
        doc_id = create_result.get('doc_id')
        blocks = markdown_to_blocks(content)
        print(f'  Created: {doc_id}, blocks: {len(blocks)}')
        
        write_result = write_blocks(doc_id, blocks)
        if write_result.get('success'):
            print(f'  Written OK! URL: https://feishu.cn/docx/{doc_id}')
        else:
            print(f'  Write failed: {write_result.get("error")}')
    else:
        print(f'  Create failed: {create_result.get("error")}')
