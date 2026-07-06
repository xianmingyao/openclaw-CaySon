# -*- coding: utf-8 -*-
"""列出 GEO-Platform 项目下所有代码文件（排除无关目录）。"""
import os
import sys

ROOT = r"E:\PY\yunfanshujing\GEO-Platform"
EXCLUDE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "env",
                "dist", "build", ".idea", ".vscode", ".next", "target",
                "migrations", ".mypy_cache", ".pytest_cache", ".gradle", "out"}
EXCLUDE_EXTS = {".class", ".jar", ".war", ".pyc", ".pyo", ".so", ".dll",
                ".exe", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
                ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".mp3", ".zip",
                ".tar", ".gz", ".rar", ".pdf", ".log"}

ext_map = {
    "py": "Python",
    "js": "JavaScript",
    "ts": "TypeScript",
    "tsx": "TypeScript-React",
    "jsx": "JavaScript-React",
    "vue": "Vue",
    "html": "HTML",
    "css": "CSS",
    "scss": "SCSS",
    "less": "LESS",
    "json": "JSON",
    "yaml": "YAML",
    "yml": "YAML",
    "md": "Markdown",
    "sql": "SQL",
    "xml": "XML",
    "java": "Java",
    "go": "Go",
    "php": "PHP",
    "sh": "Shell",
    "bat": "Batch",
    "ps1": "PowerShell",
    "toml": "TOML",
    "ini": "INI",
    "env": "ENV",
    "properties": "Properties",
    "txt": "TXT",
}

files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
    for fn in filenames:
        ext = os.path.splitext(fn)[1].lower().lstrip(".")
        if ext in EXCLUDE_EXTS:
            continue
        rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
        files.append((rel, ext_map.get(ext, ext.upper())))

# 按文件类型分组
from collections import defaultdict
groups = defaultdict(list)
for rel, lang in files:
    groups[lang].append(rel)

print(f"# GEO-Platform 文件清单（共 {len(files)} 个文件）\n")
for lang in sorted(groups.keys()):
    print(f"\n## {lang} ({len(groups[lang])} 个)")
    for rel in sorted(groups[lang]):
        print(f"  {rel}")

# 同时把所有文件路径写到 txt 供后续分析用
with open(r"E:\workspace\temp_geo_files.txt", "w", encoding="utf-8") as f:
    for rel, lang in files:
        f.write(f"{rel}\n")

print(f"\n\n# 路径文件: E:\\workspace\\temp_geo_files.txt")
