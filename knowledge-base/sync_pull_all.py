#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sync_pull_all.py - 一键同步飞书+Notion到本地
"""
import subprocess
import sys

def run_script(name, script_path):
    print(f"\n{'='*50}")
    print(f"Running: {name}")
    print(f"{'='*50}")
    result = subprocess.run([sys.executable, script_path], capture_output=False)
    return result.returncode == 0

if __name__ == "__main__":
    kb_dir = r"E:\workspace\knowledge-base"
    
    # 1. 飞书同步
    feishu_ok = run_script("Feishu Sync", rf"{kb_dir}\sync_pull_feishu.py")
    
    # 2. Notion同步
    notion_ok = run_script("Notion Sync", rf"{kb_dir}\sync_pull_notion.py")
    
    print(f"\n{'='*50}")
    print("Sync Complete")
    print(f"  Feishu: {'OK' if feishu_ok else 'FAILED'}")
    print(f"  Notion: {'OK' if notion_ok else 'FAILED'}")
    print(f"{'='*50}")
