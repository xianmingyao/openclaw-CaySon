import sys
sys.path.insert(0, 'E:/workspace/scripts')

# Read the knowledge base content
with open('E:/workspace/knowledge-base/wiki/概念/Zilliz-Cloud企业知识库完整指南.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Import feishu_doc
from feishu_doc import feishu_doc

# Create Feishu doc
result = feishu_doc({
    'action': 'create',
    'title': 'Zilliz Cloud 企业知识库完整指南 v1.0',
    'owner_open_id': 'ou_29ce355d02cb91c7c2f58c8844dc7177'
})
print("Create result:", result)

# Extract doc_token if created
import json
if isinstance(result, str):
    try:
        data = json.loads(result)
        if 'data' in data and 'document' in data['data']:
            doc_token = data['data']['document']['document_id']
            print(f"Created doc_token: {doc_token}")
            
            # Write content to the doc
            write_result = feishu_doc({
                'action': 'write',
                'doc_token': doc_token,
                'content': content
            })
            print("Write result:", write_result)
    except Exception as e:
        print(f"Error: {e}")
