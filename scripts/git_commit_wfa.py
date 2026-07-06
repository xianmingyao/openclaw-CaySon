import subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
# Add files
files = [
    "douyin-knowledge/2026-05-19-Workflow与Agent的本质区别-知识沉淀.md",
    "knowledge-base/wiki/概念/企业AI本体Ontology-从工具到Agent的关键.md",
    "scripts/feishu_wfa.py",
    "scripts/milvus_sync_wfa.py",
]
for f in files:
    r = subprocess.run(["git", "-C", "E:\\workspace", "add", f], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ADD FAILED: {f} {r.stderr[:100]}")
    else:
        print(f"ADDED: {f}")
# Commit
msg = "docs: add Workflow Agent hybrid mode deep dive (Jiangge #74) + Ontology Section 20"
r = subprocess.run(["git", "-C", "E:\\workspace", "commit", "-m", msg], capture_output=True, text=True)
if r.returncode != 0:
    print(f"COMMIT FAILED: {r.stderr[:200]}")
else:
    print(f"COMMIT OK: {msg}")
