#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sync_pull_lightweight.py - 轻量级同步脚本（cron调用版本）
调用 knowledge-base/sync_pull_all.py 执行飞书和Notion双向同步
"""
import subprocess
import sys
from pathlib import Path

def main():
    kb_dir = Path(__file__).parent.parent / "knowledge-base"
    sync_script = kb_dir / "sync_pull_all.py"
    
    if not sync_script.exists():
        print(f"ERROR: {sync_script} not found")
        sys.exit(2)
    
    result = subprocess.run(
        [sys.executable, str(sync_script)],
        capture_output=False
    )
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
