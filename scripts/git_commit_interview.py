import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

files = [
    "douyin-knowledge/2026-05-19-字节Agent面试高频题MCP-RAG-熔断.md",
    "scripts/feishu_bytedance_interview.py",
    "scripts/milvus_sync_interview.py",
]

for f in files:
    r = subprocess.run(["git", "-C", "E:\\workspace", "add", f], capture_output=True, text=True)
    if r.returncode == 0:
        print(f"ADDED: {f}")
    else:
        print(f"ADD FAILED: {f}")

msg = "docs: add ByteDance Agent interview high-frequency questions (MCP RAG circuit breaker)"
r = subprocess.run(["git", "-C", "E:\\workspace", "commit", "-m", msg], capture_output=True, text=True)
if r.returncode == 0:
    print(f"COMMIT OK: {msg}")
else:
    print(f"COMMIT FAILED: {r.stderr[:200]}")
