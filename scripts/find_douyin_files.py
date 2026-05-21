#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import datetime

base = r'E:\workspace\douyin-knowledge'
for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith('.md'):
            path = os.path.join(root, f)
            mtime = os.path.getmtime(path)
            dt = datetime.fromtimestamp(mtime)
            if dt.year == 2026 and dt.month in [3, 4]:
                print(f'{dt.strftime("%Y-%m-%d")} | {f}')
