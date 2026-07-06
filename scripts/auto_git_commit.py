#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
auto_git_commit.py - 自动 Git 提交并推送
修复：处理子模块 + 检查实际变更 + 处理分支divergence
"""
import subprocess
import sys
from datetime import datetime

def run_git(cmd, cwd, check=True):
    """运行 git 命令"""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True,
        encoding="utf-8", errors="replace"
    )
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)
    if check and result.returncode != 0:
        return False
    return result.returncode == 0

def has_actual_changes(workspace):
    """检查是否有实际需要提交的内容"""
    # 主仓库变更
    status = subprocess.run(
        ["git", "status", "--porcelain", "-uno"], 
        cwd=workspace, capture_output=True, encoding="utf-8", errors="replace"
    )
    main_changed = bool(status.stdout.strip())
    
    # 子模块变更（检查每个子模块）
    submodule_status = subprocess.run(
        ["git", "submodule", "status"], 
        cwd=workspace, capture_output=True, encoding="utf-8", errors="replace"
    )
    
    has_submodule_changes = False
    if submodule_status.stdout:
        for line in submodule_status.stdout.strip().split("\n"):
            if line:
                # 检查子模块是否有未提交的改动
                sub_result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=f"{workspace}/{line.split()[1]}" if len(line.split()) > 1 else None,
                    capture_output=True, encoding="utf-8", errors="replace"
                )
                if sub_result.stdout.strip():
                    has_submodule_changes = True
                    print(f"Submodule has changes: {line.split()[1] if len(line.split()) > 1 else line}")
    
    return main_changed or has_submodule_changes

def force_push_if_needed(workspace):
    """检测 push 是否因 divergence 失败，必要时 force push"""
    status = subprocess.run(
        ["git", "status", "-b", "--porcelain"],
        cwd=workspace, capture_output=True, encoding="utf-8", errors="replace"
    )
    output = status.stdout or ""
    
    # divergence 检测：[ahead X, behind Y] 格式
    has_ahead = "ahead" in output
    has_behind = "behind" in output
    
    if has_ahead and has_behind:
        print("Branch has diverged from origin (ahead & behind), forcing push...")
        result = subprocess.run(
            ["git", "push", "--force-with-lease", "origin", "auto-optimize-20260420-1453"], 
            cwd=workspace, capture_output=True, encoding="utf-8", errors="replace"
        )
        if result.returncode == 0:
            print("Force push successful!")
            return True
        else:
            print(f"Force push failed: {result.stderr}")
            return False
    return True

if __name__ == "__main__":
    workspace = r"E:\workspace"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"{'='*50}")
    print(f"Auto Git Commit - {timestamp}")
    print(f"{'='*50}")
    
    # 0. 检查是否有实际变更
    if not has_actual_changes(workspace):
        print("No changes to commit (main repo and submodules)")
        sys.exit(0)
    
    # 1. git add -A (包括子模块)
    if not run_git(["git", "add", "-A"], workspace):
        print("git add failed!")
        sys.exit(1)
    
    # 3. 再次检查是否有变更（add之后）
    status = subprocess.run(
        ["git", "status", "--porcelain"], cwd=workspace,
        capture_output=True, encoding="utf-8", errors="replace"
    )
    if not (status.stdout or "").strip():
        print("No changes to commit after git add -A")
        sys.exit(0)
    
    print(f"Staged changes:\n{status.stdout}")
    
    # 4. git commit
    commit_msg = f"定时自动提交 - {timestamp}"
    if not run_git(["git", "commit", "-m", commit_msg], workspace):
        print("git commit failed!")
        sys.exit(1)
    
    # 5. git push（带重试 + divergence 自动 force push）
    push_success = False
    for attempt in range(3):
        if run_git(["git", "push"], workspace, check=False):
            push_success = True
            break
        print(f"Push failed, attempt {attempt + 1}/3...")
        if attempt == 2:  # 最后一次尝试
            if not force_push_if_needed(workspace):
                print("git push failed after all attempts!")
                sys.exit(1)
            push_success = True
        else:
            subprocess.run(["git", "fetch", "origin"], cwd=workspace, capture_output=True)
    
    print(f"\n{'='*50}")
    print("Git commit and push completed!")
    print(f"{'='*50}")
