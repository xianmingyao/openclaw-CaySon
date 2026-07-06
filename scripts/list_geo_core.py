# -*- coding: utf-8 -*-
"""列出 GEO-Platform 核心源代码文件(排除缓存/测试/.next/.demo 截图)。"""
import os
from collections import defaultdict

ROOT = r"E:\PY\yunfanshujing\GEO-Platform"
EXCLUDE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    "dist", "build", ".idea", ".vscode", ".next", ".next-demo", "target",
    ".mypy_cache", ".pytest_cache", ".gradle", "out", ".superpowers",
    ".ccg", ".codegraph", ".agents", ".claude", ".codex", "archive",
}
EXCLUDE_DIR_PREFIX = (".next", ".turbo", "test-results", "playwright-report",
                      "turbopack", "docs/暂时可以不看")
EXCLUDE_EXTS = {".class", ".jar", ".war", ".pyc", ".pyo", ".so", ".dll",
                ".exe", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
                ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".mp3", ".zip",
                ".tar", ".gz", ".rar", ".pdf", ".log", ".sst", ".meta",
                ".pid", ".tmp", ".bak", ".lock", ".swp", ".swo",
                ".tsbuildinfo", ".map"}

# 优先关注的文件类型
PRIORITY_EXTS = {"py", "ts", "tsx", "vue", "sql", "yaml", "yml", "toml"}

ext_map = {
    "py": "Python", "ts": "TypeScript", "tsx": "TSX-React",
    "vue": "Vue", "json": "JSON", "yaml": "YAML", "yml": "YAML",
    "md": "Markdown", "sql": "SQL", "css": "CSS", "scss": "SCSS",
    "html": "HTML", "toml": "TOML", "ini": "INI", "env": "ENV",
    "js": "JavaScript", "mjs": "JavaScript", "cjs": "JavaScript",
    "sh": "Shell", "bat": "Batch", "ps1": "PowerShell",
    "txt": "TXT", "cfg": "Config", "conf": "Config",
    "txt": "TXT",
}

groups = defaultdict(list)
total = 0
for dirpath, dirnames, filenames in os.walk(ROOT):
    # 排除目录
    dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".next")]
    # 排除特定前缀目录
    rel_dir = os.path.relpath(dirpath, ROOT)
    if any(rel_dir.startswith(p) for p in EXCLUDE_DIR_PREFIX):
        continue
    for fn in filenames:
        ext = os.path.splitext(fn)[1].lower().lstrip(".")
        if ext in EXCLUDE_EXTS:
            continue
        rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
        # 跳过 archive 目录
        if "archive" in rel.split(os.sep):
            continue
        groups[ext_map.get(ext, ext.upper())].append(rel)
        total += 1

# 输出
print(f"# GEO-Platform 核心文件清单(共 {total} 个)\n")
for lang in sorted(groups.keys()):
    print(f"\n## {lang} ({len(groups[lang])} 个)")
    for rel in sorted(groups[lang]):
        print(f"  {rel}")
