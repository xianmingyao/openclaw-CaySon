# -*- coding: utf-8 -*-
"""
分批同步脚本 - 每次同步100个文件
用法: python sync_batch.py [批次号]
     python sync_batch.py 0  # 从头开始，第1批
     python sync_batch.py 1  # 第2批
     python sync_batch.py 2  # 第3批
     python sync_batch.py 3  # 第4批
     python sync_batch.py 4  # 第5批（最后一批，可能不满100）
"""
import sys
import os
from pathlib import Path
from datetime import datetime

KB_DIR = Path(__file__).parent
os.chdir(KB_DIR)
sys.path.insert(0, str(KB_DIR))

BATCH_SIZE = 100

def main():
    batch_num = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    start_idx = batch_num * BATCH_SIZE
    
    print("=" * 60)
    print(f"Karpathy Knowledge Base - Batch Sync #{batch_num + 1}")
    print("=" * 60)
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Start index: {start_idx}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 只同步飞书（最耗时的是飞书）
    print(f"[1/2] Syncing to Feishu (batch {batch_num + 1})")
    print("-" * 40)
    from sync_feishu import main as feishu_main
    try:
        # 飞书脚本需要修改支持分批，这里直接调用并传入参数
        # 但sync_feishu.py可能不支持分批，所以我们要修改它
        feishu_main(batch_start=start_idx, batch_size=BATCH_SIZE)
    except TypeError:
        # 如果sync_feishu不支持分批参数，先用原版
        print(f"   [INFO] sync_feishu 不支持分批参数，执行全量...")
        from sync_feishu import sync_all as feishu_sync
        feishu_sync()
    except Exception as e:
        print(f"   [ERROR] Feishu sync failed: {e}")
    print()
    
    print(f"[2/2] Syncing to Notion (batch {batch_num + 1})")
    print("-" * 40)
    from sync_notion import main as notion_main
    try:
        notion_main(batch_start=start_idx, batch_size=BATCH_SIZE)
    except TypeError:
        print(f"   [INFO] sync_notion 不支持分批参数，跳过...")
    except Exception as e:
        print(f"   [ERROR] Notion sync failed: {e}")
    print()
    
    print("=" * 60)
    print(f"Done! {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
