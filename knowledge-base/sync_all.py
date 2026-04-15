#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全量同步脚本
运行完整的知识库同步流程：
1. 编译 raw → wiki
2. 同步到飞书
3. 同步到 Notion
4. 上传到云端记忆
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# 设置工作目录
KB_DIR = Path(__file__).parent
os.chdir(KB_DIR)
sys.path.insert(0, str(KB_DIR))

print("=" * 60)
print("Karpathy Knowledge Base - Full Sync")
print("=" * 60)
print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 1. 编译（使用优化版本 v6）
print("[1/4] Compiling raw -> wiki (v6 optimized)")
print("-" * 40)
try:
    from compile_optimized import run_ingest
    run_ingest(force=False, batch_size=10)
except ImportError:
    # 降级：使用原版本
    print("   [INFO] compile_optimized 不可用，使用原版本")
    from compile import main as compile_main
    compile_main()
print()

# 2. 同步到飞书
print("[2/4] Syncing to Feishu")
print("-" * 40)
from sync_feishu import main as feishu_main
try:
    feishu_main()
except Exception as e:
    print(f"   [ERROR] Feishu sync failed: {e}")
print()

# 3. 同步到 Notion
print("[3/4] Syncing to Notion")
print("-" * 40)
from sync_notion import main as notion_main
try:
    notion_main()
except Exception as e:
    print(f"   [ERROR] Notion sync failed: {e}")
print()

# 4. 上传到云端
print("[4/4] Uploading to cloud memory")
print("-" * 40)
from upload_mem0 import main as mem0_main
try:
    mem0_main()
except Exception as e:
    print(f"   [ERROR] Milvus upload failed: {e}")
print()

print("=" * 60)
print(f"Done! {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
