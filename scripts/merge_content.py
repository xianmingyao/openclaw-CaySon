#!/usr/bin/env python3
"""Merge historical content and prepare final output files"""
import os
import re
import sys
from datetime import datetime

data_dir = r"E:\workspace\content-hunter-data\data"
out_dir = os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "content-hunter", "data")
os.makedirs(out_dir, exist_ok=True)

def clean_bilibili_content():
    """Read and process historical bilibili data"""
    fpath = os.path.join(data_dir, "bilibili-ai.md")
    if not os.path.exists(fpath):
        print("bilibili-ai.md not found!", file=sys.stderr)
        return []
    
    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    print(f"Read {len(content)} chars from bilibili-ai.md", file=sys.stderr)
    
    # Parse items - look for pattern like "### 第xx条" or just extract sections
    # The file uses "### 第xx条" or similar markers
    items = []
    
    # Split by "###" to find individual items
    sections = re.split(r'###\s*第\s*(\d+)\s*条', content)
    print(f"Found {len(sections)//2} sections", file=sys.stderr)
    
    current_item = {}
    for i, section in enumerate(sections):
        if i % 2 == 0:
            # This is the text before a "第xx条" marker
            continue
        else:
            # This is the item number
            item_num = int(section)
            # The next element should be the content
            if i+1 < len(sections):
                item_content = sections[i+1]
                # Try to extract title
                title_match = re.search(r'标题[:：]\s*(.+)', item_content)
                author_match = re.search(r'UP主[:：]\s*@?(.+)', item_content)
                play_match = re.search(r'播放[:：]\s*(\d+)', item_content)
                
                if title_match:
                    items.append({
                        'num': item_num,
                        'title': title_match.group(1).strip(),
                        'author': author_match.group(1).strip() if author_match else '',
                        'play': play_match.group(1).strip() if play_match else '0',
                    })
    
    print(f"Parsed {len(items)} items", file=sys.stderr)
    return items

def parse_douyin_content():
    """Read historical douyin data"""
    fpath = os.path.join(data_dir, "douyin-ai.md")
    if not os.path.exists(fpath):
        print("douyin-ai.md not found!", file=sys.stderr)
        return []
    
    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    
    print(f"Read {len(content)} chars from douyin-ai.md", file=sys.stderr)
    
    # Parse items
    items = []
    sections = re.split(r'###\s*第\s*(\d+)\s*条', content)
    print(f"Found {len(sections)//2} douyin sections", file=sys.stderr)
    
    for i in range(1, len(sections), 2):
        item_num = sections[i]
        item_content = sections[i+1] if i+1 < len(sections) else ""
        
        title_match = re.search(r'标题[:：]\s*(.+)', item_content)
        author_match = re.search(r'作者[:：]\s*@?(.+)', item_content)
        digg_match = re.search(r'点赞[:：]\s*(\d+)', item_content)
        
        if title_match:
            items.append({
                'num': int(item_num) if item_num.isdigit() else 0,
                'title': title_match.group(1).strip(),
                'author': author_match.group(1).strip() if author_match else '',
                'digg': digg_match.group(1).strip() if digg_match else '0',
            })
    
    print(f"Parsed {len(items)} douyin items", file=sys.stderr)
    return items

def format_bilibili_md(items):
    lines = ["# B站 AI技术热门内容\n\n"]
    lines.append(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    lines.append(f"总计: {len(items)} 条\n\n---\n\n")
    
    for i, item in enumerate(items[:100], 1):
        lines.append(f"### 第{i}条\n")
        lines.append(f"- 标题: {item.get('title', '无标题')}\n")
        lines.append(f"- UP主: @{item.get('author', '未知')}\n")
        lines.append(f"- 播放: {item.get('play', '0')}\n\n")
    
    return ''.join(lines)

def format_douyin_md(items):
    lines = ["# 抖音 AI技术热门内容\n\n"]
    lines.append(f"抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
    lines.append(f"总计: {len(items)} 条\n\n---\n\n")
    
    for i, item in enumerate(items[:100], 1):
        lines.append(f"### 第{i}条\n")
        lines.append(f"- 标题: {item.get('title', '无标题')}\n")
        lines.append(f"- 作者: @{item.get('author', '未知')}\n")
        lines.append(f"- 点赞: {item.get('digg', '0')}\n\n")
    
    return ''.join(lines)

if __name__ == "__main__":
    print("=== Processing Bilibili ===", file=sys.stderr)
    bi_items = clean_bilibili_content()
    if bi_items:
        # Sort by item number
        bi_items.sort(key=lambda x: x.get('num', 0))
        md = format_bilibili_md(bi_items)
        out_path = os.path.join(out_dir, "bilibili.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Saved {len(bi_items)} bilibili items to {out_path}", file=sys.stderr)
    else:
        print("No bilibili items found!", file=sys.stderr)
    
    print("\n=== Processing Douyin ===", file=sys.stderr)
    dy_items = parse_douyin_content()
    if dy_items:
        dy_items.sort(key=lambda x: x.get('num', 0))
        md = format_douyin_md(dy_items)
        out_path = os.path.join(out_dir, "douyin.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"Saved {len(dy_items)} douyin items to {out_path}", file=sys.stderr)
    else:
        print("No douyin items found!", file=sys.stderr)
    
    print("\nDONE")
