# -*- coding: utf-8 -*-
"""Create Feishu documents for the 3 topics"""

import json
import subprocess
import sys

def run_feishu_tool(tool_input):
    """Run feishu_doc tool via openclaw"""
    cmd = [
        'python', '-m', 'openclaw', 'tools', 'call', 'feishu_doc',
        '--json', json.dumps(tool_input)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    return result

def main():
    # Read content
    with open(r'E:\workspace\knowledge\temp_sync_content.json', encoding='utf-8') as f:
        docs = json.load(f)

    results = []

    for i, doc in enumerate(docs):
        print(f"Creating Feishu doc {i+1}/3: {doc['title']}")

        # Create and write to Feishu
        tool_input = {
            "action": "create_and_write",
            "title": doc['title'],
            "content": doc['content']
        }

        result = run_feishu_tool(tool_input)
        print(f"Result: {result.stdout[:500] if result.stdout else 'No stdout'}")
        if result.stderr:
            print(f"Stderr: {result.stderr[:500]}")

        results.append({
            'title': doc['title'],
            'tool_input': tool_input,
            'stdout': result.stdout,
            'stderr': result.stderr
        })

    # Save results
    with open(r'E:\workspace\knowledge\feishu_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\nDone! Results saved to feishu_results.json")

if __name__ == '__main__':
    main()
