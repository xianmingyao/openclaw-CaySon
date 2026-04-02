# -*- coding: utf-8 -*-
import requests
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

GITHUB_TOKEN = os.environ.get("GITHUBTOKEN", "")
headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def fetch_file(url, output_path):
    """Fetch a single file from GitHub"""
    r = requests.get(url, headers=headers, timeout=30)
    if r.status_code == 200:
        # GitHub API returns base64 encoded content for files
        import base64
        content = base64.b64decode(r.json()['content']).decode('utf-8')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Downloaded: {output_path}")
        return content
    else:
        print(f"Failed to download {url}: {r.status_code}")
        return None

def fetch_tree(url, output_dir):
    """Fetch a directory tree from GitHub"""
    r = requests.get(url, headers=headers, timeout=30)
    if r.status_code == 200:
        os.makedirs(output_dir, exist_ok=True)
        items = r.json()
        for item in items:
            if item['type'] == 'file':
                fetch_file(item['url'], os.path.join(output_dir, item['name']))
            elif item['type'] == 'dir':
                fetch_tree(item['url'], os.path.join(output_dir, item['name']))
        return items
    else:
        print(f"Failed to fetch tree {url}: {r.status_code}")
        return []

# Create temp directory
temp_dir = "E:/workspace/temp_claude_code"
os.makedirs(temp_dir, exist_ok=True)

# Fetch key files
fetch_file("https://api.github.com/repos/sanbuphy/claude-code-source-code/contents/QUICKSTART.md", f"{temp_dir}/QUICKSTART.md")
fetch_file("https://api.github.com/repos/sanbuphy/claude-code-source-code/contents/README_CN.md", f"{temp_dir}/README_CN.md")

# Fetch src directory structure
fetch_tree("https://api.github.com/repos/sanbuphy/claude-code-source-code/contents/src", f"{temp_dir}/src")

print("\nDone!")
