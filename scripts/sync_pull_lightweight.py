"""
轻量级知识同步脚本 - 直接执行，不走 Agent
避免 MiniMax API 调用，直接运行同步命令
"""
import subprocess
import sys
import os
from datetime import datetime

LOG_FILE = r"E:\workspace\logs\sync_pull.log"

def log(msg):
    """写入日志"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    print(msg)

def run_command(cmd, timeout=120):
    """执行命令并返回结果"""
    log(f"执行: {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace"
        )
        if result.returncode == 0:
            log(f"✓ 成功: {result.stdout[:200] if result.stdout else '无输出'}")
            return True
        else:
            log(f"✗ 失败 (code={result.returncode}): {result.stderr[:200] if result.stderr else '无错误'}")
            return False
    except subprocess.TimeoutExpired:
        log(f"✗ 超时 ({timeout}s)")
        return False
    except Exception as e:
        log(f"✗ 异常: {e}")
        return False

def main():
    log("=" * 50)
    log("开始知识-pull同步")
    
    # 1. 同步飞书
    feishu_ok = run_command(r"python E:\workspace\knowledge-base\sync_pull_feishu.py", timeout=180)
    
    # 2. 同步 Notion
    notion_ok = run_command(r"python E:\workspace\knowledge-base\sync_pull_notion.py", timeout=180)
    
    # 3. 同步 GitHub Trending
    github_ok = run_command(r"python E:\workspace\scripts\feishu_write_github_trending.py", timeout=120)
    
    log("=" * 50)
    if feishu_ok and notion_ok and github_ok:
        log("同步完成：全部成功")
        return 0
    elif feishu_ok or notion_ok or github_ok:
        log("同步完成：部分成功")
        return 1
    else:
        log("同步完成：全部失败")
        return 2

if __name__ == "__main__":
    sys.exit(main())
