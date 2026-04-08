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
from pathlib import Path
from datetime import datetime

print("=" * 60)
print("🚀 Karpathy 知识库 - 全量同步")
print("=" * 60)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 1. 编译
print("📦 STEP 01: 编译 raw → wiki")
print("-" * 40)
sys.path.insert(0, str(Path(__file__).parent))
from compile import main as compile_main
asyncio.run(compile_main())
print()

# 2. 同步到飞书
print("📤 STEP 02: 同步到飞书")
print("-" * 40)
from sync_feishu import main as feishu_main
feishu_main()
print()

# 3. 同步到 Notion
print("📓 STEP 03: 同步到 Notion")
print("-" * 40)
from sync_notion import main as notion_main
notion_main()
print()

# 4. 上传到云端
print("☁️  STEP 04: 上传到云端记忆")
print("-" * 40)
from upload_mem0 import main as mem0_main
mem0_main()
print()

print("=" * 60)
print("✅ 全量同步完成!")
print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
