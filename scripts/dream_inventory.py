#!/usr/bin/env python3
"""Dream Phase 1 inventory script."""
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_DIR = Path(r"E:\workspace\memory")
MARKER = "consolidated to MEMORY.md"
TODAY = datetime.now()
CUTOFF_7D = TODAY - timedelta(days=7)
CUTOFF_30D = TODAY - timedelta(days=30)


def main():
    if not MEMORY_DIR.exists():
        print("memory/ 目录不存在")
        return

    files = sorted(MEMORY_DIR.glob("*.md"))
    total_files = len(files)
    total_lines = 0
    recent = []  # last 7 days
    old_unmarked = []  # >30 days, no consolidation marker

    print("===== Phase 1 Inventory =====")
    print(f"Total files: {total_files}")

    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"  [warn] failed to read {f.name}: {e}")
            continue

        lines = content.count("\n") + 1
        total_lines += lines
        mtime = datetime.fromtimestamp(f.stat().st_mtime)

        if mtime > CUTOFF_7D:
            recent.append({
                "name": f.name,
                "lines": lines,
                "modified": mtime.strftime("%Y-%m-%d %H:%M"),
            })
        elif mtime < CUTOFF_30D and MARKER not in content:
            old_unmarked.append({
                "name": f.name,
                "days_old": (TODAY - mtime).days,
            })

    print(f"Total lines: {total_lines}")
    print()
    print("===== Recent files (last 7 days) =====")
    if recent:
        for r in recent:
            print(f"  {r['name']:24s}  {r['lines']:5d} lines  {r['modified']}")
    else:
        print("  (none)")
    print()
    print("===== Old files > 30 days, unmarked =====")
    print(f"Count: {len(old_unmarked)}")
    for o in old_unmarked:
        print(f"  {o['name']:24s}  {o['days_old']} days old")

    print()
    print(f"Total files: {total_files}")
    print(f"Total lines: {total_lines}")
    print(f"Recent (7d): {len(recent)}")
    print(f"Old >30d unmarked: {len(old_unmarked)}")


if __name__ == "__main__":
    main()
