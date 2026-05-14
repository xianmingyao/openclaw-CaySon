#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
auto_git_commit.py - 自动 Git 提交并推送
"""
import subprocess
import sys
from datetime import datetime

def run_git(cmd, cwd):
    """运行 git 命令"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True,
        encoding="utf-8", errors="replace"
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.returncode == 0

if __name__ == "__main__":
    workspace = r"E:\workspace"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"{'='*50}")
    print(f"Auto Git Commit - {timestamp}")
    print(f"{'='*50}")
    
    # 1. git add .
    if not run_git(["git", "add", "."], workspace):
        print("git add failed!")
        sys.exit(1)
    
    # 2. 检查是否有变更
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=workspace,
        capture_output=True, encoding="utf-8", errors="replace"
    )
    if not (status.stdout or "").strip():
        print("No changes to commit")
        sys.exit(0)
    
    # 3. git commit
    commit_msg = f"定时自动提交 - {timestamp}"
    if not run_git(["git", "commit", "-m", commit_msg], workspace):
        print("git commit failed!")
        sys.exit(1)
    
    # 4. git push
    if not run_git(["git", "push"], workspace):
        print("git push failed!")
        sys.exit(1)
    
    print(f"\n{'='*50}")
    print("Git commit and push completed!")
    print(f"{'='*50}")
