#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
print('[4/4] Uploading to cloud memory')
from upload_mem0 import main as mem0_main
try:
    mem0_main()
    print('Mem0 upload done')
except Exception as e:
    print(f'[ERROR] Milvus upload failed: {e}')
