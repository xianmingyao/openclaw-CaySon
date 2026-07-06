#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""快速 Lint 检查 - 只检查关键问题"""
import re
import os
from pathlib import Path
from collections import defaultdict

WIKI_DIR = Path(__file__).parent / "wiki"

def scan_wiki_pages(limit=500):
    """扫描 wiki 页面（限制数量）"""
    pages = {}
    count = 0
    for md_file in WIKI_DIR.rglob("*.md"):
        if md_file.name in ("index.md", "log.md"):
            continue
        rel_path = md_file.relative_to(WIKI_DIR)
        try:
            content = md_file.read_text(encoding='utf-8')
        except:
            continue
        pages[str(rel_path)] = {
            'path': md_file,
            'content': content,
            'title': md_file.stem,
            'links': extract_links(content)
        }
        count += 1
        if limit and count >= limit:
            break
    return pages

def extract_links(content):
    pattern = r'\[\[([^\]]+)\]\]'
    return re.findall(pattern, content)

def check_orphan_links(pages):
    orphans = []
    for path, page in pages.items():
        for link in page['links']:
            target = WIKI_DIR / (link + ".md")
            if not target.exists():
                orphans.append((path, link))
    return orphans

def check_short_pages(pages, min_chars=50):
    short = []
    for path, page in pages.items():
        text = re.sub(r'[#*`\[\]]', '', page['content'])
        if len(text.strip()) < min_chars:
            short.append((path, len(text.strip())))
    return short

if __name__ == "__main__":
    print("[Lint] Knowledge base quick check...")
    print(f"[Scan] Directory: {WIKI_DIR}")
    
    pages = scan_wiki_pages(limit=1000)
    print(f"[Pages] Scanned: {len(pages)}")
    
    # Orphan links check
    orphans = check_orphan_links(pages)
    print(f"[Orphan] Links: {len(orphans)}")
    for p, l in orphans[:10]:
        print(f"  - {p} -> [[{l}]]")
    
    # Short pages check
    short = check_short_pages(pages)
    print(f"[Short] Pages (<50 chars): {len(short)}")
    for p, l in short[:10]:
        print(f"  - {p} ({l} chars)")
    
    print("\n[DONE] Quick check complete")
