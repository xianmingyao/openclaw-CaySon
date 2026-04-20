#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
print('[1/4] Compiling raw -> wiki')
from compile import run_ingest
run_ingest(force=False, batch_size=10)
print('Compile done')
