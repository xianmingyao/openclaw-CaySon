#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
continuous_ingest.py - 持续 ingest 机制

Karpathy 方法论的核心：人类记录到 log → AI 自动整理到 wiki

功能：
1. 监控 raw/ 目录变化（新增文件）
2. 自动触发 compile.py 进行增量 ingest
3. 生成整理报告

使用说明：
    python continuous_ingest.py          # 单次运行（适合 Cron）
    python continuous_ingest.py --watch   # 持续监控模式
    python continuous_ingest.py --daemon  # 守护进程模式
"""

import os
import sys
import io
import time
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional



from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

# ============== 配置 ==============
RAW_DIR = Path(__file__).parent / "raw"
WIKI_DIR = Path(__file__).parent / "wiki"
LOG_FILE = WIKI_DIR / "log.md"
PROCESSED_FILE = Path(__file__).parent / ".processed_files.json"
COMPILE_SCRIPT = Path(__file__).parent / "compile.py"


# ============== 文件变化监控 ==============

class RawDirectoryHandler(FileSystemEventHandler):
    """监控 raw/ 目录变化"""
    
    def __init__(self, callback):
        self.callback = callback
        self.processed = load_processed_files()
    
    def on_created(self, event: FileSystemEvent):
        if event.is_directory:
            return
        
        filepath = Path(event.src_path)
        if filepath.suffix.lower() in ['.md', '.txt', '.pdf', '.html']:
            self.process_new_file(filepath)
    
    def on_modified(self, event: FileSystemEvent):
        if event.is_directory:
            return
        
        filepath = Path(event.src_path)
        if filepath.suffix.lower() in ['.md', '.txt', '.pdf', '.html']:
            # 检查文件是否真的有变化
            file_hash = get_file_hash(filepath)
            if file_hash != self.processed.get(str(filepath), {}).get('hash'):
                self.process_new_file(filepath)
    
    def process_new_file(self, filepath: Path):
        """处理新文件"""
        print(f"\n[NEW FILE] {filepath.name}")
        
        # 计算文件 hash
        file_hash = get_file_hash(filepath)
        
        # 检查是否已处理
        if str(filepath) in self.processed:
            last_hash = self.processed[str(filepath)]['hash']
            if last_hash == file_hash:
                print(f"       已处理，跳过")
                return
        
        # 记录到待处理
        self.processed[str(filepath)] = {
            'hash': file_hash,
            'detected_at': datetime.now().isoformat(),
            'processed': False
        }
        
        # 触发 ingest
        self.callback([filepath])
        
        # 更新状态
        self.processed[str(filepath)]['processed'] = True
        self.processed[str(filepath)]['processed_at'] = datetime.now().isoformat()
        save_processed_files(self.processed)


def get_file_hash(filepath: Path) -> str:
    """计算文件 MD5 hash"""
    md5 = hashlib.md5()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()
    except:
        return ""


def load_processed_files() -> Dict:
    """加载已处理文件记录"""
    if PROCESSED_FILE.exists():
        return json.loads(PROCESSED_FILE.read_text(encoding='utf-8'))
    return {}


def save_processed_files(processed: Dict):
    """保存已处理文件记录"""
    PROCESSED_FILE.write_text(json.dumps(processed, ensure_ascii=False, indent=2), encoding='utf-8')


# ============== Ingest 逻辑 ==============

def run_compile_for_files(filepaths: List[Path]) -> bool:
    """为指定文件运行 compile"""
    print(f"[INGEST] 触发 compile.py for {len(filepaths)} 个文件")
    
    try:
        # 调用 compile.py（增量模式）
        cmd = [sys.executable, str(COMPILE_SCRIPT), "--force"]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300
        )
        
        if result.returncode == 0:
            print("[INGEST] [OK] compile.py 执行成功")
            return True
        else:
            print(f"[INGEST] [WARN] compile.py 执行异常: {result.stderr[:200]}")
            return False
            
    except subprocess.TimeoutExpired:
        print("[INGEST] [FAIL] compile.py 超时")
        return False
    except Exception as e:
        print(f"[INGEST] [FAIL] compile.py 执行失败: {e}")
        return False


def append_to_log(message: str):
    """追加消息到 log.md"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    entry = f"""

### [{timestamp}] 持续 ingest

{message}

"""
    
    if LOG_FILE.exists():
        existing = LOG_FILE.read_text(encoding='utf-8')
    else:
        existing = "# Wiki 操作日志\n\n> 本文件由 Karpathy 知识库系统自动维护\n"
    
    LOG_FILE.write_text(existing + entry, encoding='utf-8')


# ============== 持续监控 ==============

def watch_directory(callback):
    """监控目录变化"""
    event_handler = RawDirectoryHandler(callback)
    observer = Observer()
    observer.schedule(event_handler, str(RAW_DIR), recursive=True)
    
    print(f"\n👀 监控目录: {RAW_DIR}")
    print("   按 Ctrl+C 停止\n")
    
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n\n👋 停止监控")
    
    observer.join()


# ============== 单次运行 ==============

def scan_and_ingest() -> Dict:
    """扫描并 ingest 新文件"""
    print("=" * 50)
    print("CONTINUOUS INGEST - 单次扫描")
    print("=" * 50)
    
    processed = load_processed_files()
    
    # 扫描 raw/ 目录
    new_files = []
    for ext in ['.md', '.txt', '.pdf', '.html']:
        for filepath in RAW_DIR.rglob(f"*{ext}"):
            if filepath.is_file():
                file_hash = get_file_hash(filepath)
                
                # 检查是否已处理
                if str(filepath) not in processed or processed[str(filepath)]['hash'] != file_hash:
                    new_files.append(filepath)
    
    print(f"\n[1/2] 扫描 raw/ 目录...")
    print(f"      发现 {len(new_files)} 个新/变更文件")
    
    if not new_files:
        print("\n[SKIP] 没有新文件需要处理")
        return {"scanned": 0, "ingested": 0}
    
    # 触发 ingest
    print(f"\n[2/2] 触发 compile.py...")
    success = run_compile_for_files(new_files)
    
    # 更新记录
    for filepath in new_files:
        processed[str(filepath)] = {
            'hash': get_file_hash(filepath),
            'detected_at': datetime.now().isoformat(),
            'processed': success,
            'processed_at': datetime.now().isoformat() if success else None
        }
    
    save_processed_files(processed)
    
    # 记录到 log
    if success:
        append_to_log(f"持续 ingest 处理了 {len(new_files)} 个文件")
    
    return {"scanned": len(new_files), "ingested": 1 if success else 0}


# ============== 主入口 ==============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="持续 ingest 机制")
    parser.add_argument('--watch', action='store_true', help='持续监控模式')
    parser.add_argument('--daemon', action='store_true', help='守护进程模式')
    
    args = parser.parse_args()
    
    if args.watch or args.daemon:
        # 持续监控模式
        def on_new_files(filepaths):
            run_compile_for_files(filepaths)
        
        watch_directory(on_new_files)
    else:
        # 单次运行
        result = scan_and_ingest()
        print(f"\n[DONE] 扫描: {result['scanned']} / ingest: {result['ingested']}")


if __name__ == '__main__':
    main()
