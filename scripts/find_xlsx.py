#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, re

ROOT = r'E:\PY\yunfanshujing\GEO-Platform\apps\admin\src'
PATTERNS = [
    re.compile(r"from\s+['\"]xlsx['\"]"),
    re.compile(r"require\(['\"]xlsx['\"]\)"),
    re.compile(r"import\s*\*\s*as\s+\w+\s+from\s+['\"]xlsx['\"]"),
]
hits = []
for dp, _, files in os.walk(ROOT):
    for f in files:
        if not f.endswith(('.ts', '.tsx', '.js', '.jsx')):
            continue
        p = os.path.join(dp, f)
        try:
            with open(p, 'r', encoding='utf-8') as fp:
                for i, line in enumerate(fp, 1):
                    for pat in PATTERNS:
                        if pat.search(line):
                            hits.append((p, i, line.strip()))
        except Exception:
            pass

print(f'Real xlsx imports: {len(hits)}')
for h in hits:
    print(f'  {h[0]}:{h[1]}: {h[2]}')
