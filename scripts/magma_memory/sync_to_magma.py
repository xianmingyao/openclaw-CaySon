#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sync_to_magma.py - 将 compile.py 编译后的 wiki 页面同步到 MAGMA 图谱

功能：
1. 扫描 wiki/*.md 文件（排除 index.md / log.md）
2. 解析页面内容，提取标题/链接/概念
3. 使用 MemoryWriter 写入 MAGMA 图谱
4. 集成遗忘机制 + 冲突检测 + 检索验证
5. 断点续传（基于内容指纹）
6. 进度保存，Ctrl+C 中断后可继续

用法：
  python sync_to_magma.py              # 断点续传同步
  python sync_to_magma.py --dry-run   # 预览模式
  python sync_to_magma.py --force     # 强制重新写入所有文件
  python sync_to_magma.py --reset     # 重置进度，从头开始
"""
import sys
import io
import re
import json
import hashlib
import pickle
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional

# UTF-8 输出修复
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到 path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.magma_memory.writer import MemoryWriter
from scripts.magma_memory.core import MemoryGraph


# ===================== 配置 =====================
WIKI_DIR = project_root / "knowledge-base" / "wiki"
MAGMA_DIR = Path(__file__).parent
GRAPH_FILE = MAGMA_DIR / "magma_graph.json"
STATE_FILE = MAGMA_DIR / "sync_state.json"

# 排除的文件
EXCLUDE_FILES = {"index.md", "log.md", "CLAUDE.md", ".cursorrules.md"}

# 支持的扩展名
SUPPORTED_EXTS = {".md", ".txt"}

# 每批处理数量
BATCH_SIZE = 100


def compute_fingerprint(content: str) -> str:
    """计算内容指纹，用于检测重复"""
    sample = content[:200].strip()
    return hashlib.md5(sample.encode('utf-8')).hexdigest()[:12]


def extract_wiki_content(file_path: Path) -> Optional[Dict]:
    """解析 wiki 页面，提取关键信息"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return None
    
    if not content.strip():
        return None
    
    # 提取标题
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem
    
    # 提取所有 [[双向链接]]
    links = re.findall(r'\[\[([^\]]+)\]\]', content)
    links = list(set(links))
    md_links = [l for l in links if l.endswith('.md')]
    concepts = [l for l in links if not l.endswith('.md')]
    
    # 生成摘要
    summary = content[:500].strip()
    fingerprint = compute_fingerprint(content)
    
    return {
        "title": title,
        "content": content,
        "summary": summary,
        "links": md_links,
        "concepts": concepts,
        "fingerprint": fingerprint,
        "source": "wiki",
        "file_path": str(file_path.relative_to(WIKI_DIR))
    }


def scan_wiki_files() -> List[Path]:
    """扫描 wiki 目录下的所有支持的文件"""
    files = []
    if not WIKI_DIR.exists():
        return files
    for f in WIKI_DIR.rglob("*"):
        if f.is_file() and f.suffix in SUPPORTED_EXTS:
            if f.name in EXCLUDE_FILES:
                continue
            files.append(f)
    return files


def load_sync_state() -> Dict:
    """加载同步进度状态"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"processed": [], "total": 0}


def save_sync_state(state: Dict):
    """保存同步进度状态"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False)


def sync_to_magma(dry_run: bool = False, force: bool = False, reset: bool = False) -> Dict:
    """同步 wiki 到 MAGMA 图谱（支持断点续传）"""
    
    print("\n" + "="*60)
    print("🔄 MAGMA Wiki 同步工具 (断点续传版)")
    print("="*60)
    print(f"Wiki 目录: {WIKI_DIR}")
    print(f"图谱文件: {GRAPH_FILE}")
    print(f"状态文件: {STATE_FILE}")
    print(f"模式: {'🔍 预览' if dry_run else '✅ 写入'}{' (强制)' if force else ''}{' (重置)' if reset else ''}")
    
    # 1. 扫描文件
    print("\n📂 [1/6] 扫描 wiki 文件...")
    files = scan_wiki_files()
    print(f"  找到 {len(files)} 个文件")
    
    if not files:
        print("❌ 没有找到需要同步的文件")
        return {"status": "error", "message": "no files"}
    
    # 2. 解析所有文件内容
    print("\n📝 [2/6] 解析页面内容...")
    all_pages = []
    for f in files:
        page = extract_wiki_content(f)
        if page:
            all_pages.append(page)
    print(f"  成功解析 {len(all_pages)} 个页面")
    
    # 3. 加载已有节点指纹
    print("\n🔐 [3/6] 检查已有数据...")
    existing_fps = set()
    if GRAPH_FILE.exists():
        try:
            with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for node_data in data.get("nodes", {}).values():
                keywords = node_data.get("semantic_keywords", [])
                for kw in keywords:
                    if kw.startswith("fp:"):
                        existing_fps.add(kw)
        except Exception:
            pass
    print(f"  已有指纹: {len(existing_fps)} 条")
    
    # 4. 加载同步状态
    print("\n📋 [4/6] 加载同步进度...")
    state = load_sync_state()
    processed_fps = set(state.get("processed", []))
    
    # 如果 reset，清空进度
    if reset:
        print("  🔄 重置进度，从头开始...")
        processed_fps = set()
        state = {"processed": [], "total": len(all_pages)}
    
    state["total"] = len(all_pages)
    print(f"  已处理: {len(processed_fps)}/{len(all_pages)}")
    
    # 5. 过滤需要同步的
    to_sync = [p for p in all_pages if f"fp:{p['fingerprint']}" not in processed_fps]
    
    if force:
        to_sync = all_pages
        processed_fps = set()
        print(f"  ⚠️ 强制模式，将重新同步所有 {len(to_sync)} 个文件")
    else:
        print(f"  待同步: {len(to_sync)} 个")
        print(f"  跳过: {len(all_pages) - len(to_sync)} 个（已存在）")
    
    if dry_run:
        print("\n🔍 预览模式 - 前10个待同步文件:")
        for page in to_sync[:10]:
            print(f"  - {page['title'][:40]} ({len(page['content'])}字符)")
        return {"status": "dry_run", "to_sync": len(to_sync)}
    
    if not to_sync:
        print("\n✅ 所有文件已是最新，无需同步")
        return {"status": "up_to_date", "synced": 0}
    
    # 6. 分批写入
    print(f"\n💾 [5/6] 开始写入 MAGMA 图谱...")
    
    # 初始化图谱和写入器
    graph = MemoryGraph(str(GRAPH_FILE) if GRAPH_FILE.exists() else None)
    writer = MemoryWriter(
        graph,
        enable_forgetting=True,
        enable_conflict_check=True,
        enable_verification=True
    )
    
    synced = 0
    errors = 0
    verified_count = 0
    conflict_count = 0
    batch = []
    
    def process_batch(batch):
        nonlocal synced, errors, verified_count, conflict_count, processed_fps
        
        for page in batch:
            try:
                wiki_content = f"""【{page['title']}】

📁 来源: {page['file_path']}
🔗 链接: {', '.join(page['links']) if page['links'] else '无'}
🏷️ 概念: {', '.join(page['concepts']) if page['concepts'] else '无'}

{page['summary']}"""
                
                keywords = [f"fp:{page['fingerprint']}"]
                if page['links']:
                    for link in page['links'][:3]:
                        keywords.append(link.replace('.md', ''))
                if page['concepts']:
                    keywords.extend(page['concepts'][:5])
                
                node_id, report = writer.add(
                    content=wiki_content,
                    source="wiki-sync",
                    keywords=keywords,
                    importance=0.7
                )
                
                processed_fps.add(f"fp:{page['fingerprint']}")
                state["processed"] = list(processed_fps)
                
                if report['verified']:
                    verified_count += 1
                if report['conflicts']:
                    conflict_count += len(report['conflicts'])
                
                synced += 1
                
            except Exception as e:
                errors += 1
                print(f"  ❌ 写入失败: {page['title'][:30]}: {e}")
        
        # 保存进度
        save_sync_state(state)
        graph.save()
    
    total_batches = (len(to_sync) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for i, page in enumerate(to_sync, 1):
        batch.append(page)
        if len(batch) >= BATCH_SIZE or i == len(to_sync):
            batch_num = (i - 1) // BATCH_SIZE + 1
            print(f"  批次 {batch_num}/{total_batches} ({len(batch)} 条)...")
            process_batch(batch)
            batch = []
    
    # 7. 生成报告
    print("\n📊 [6/6] 生成报告...")
    stats = writer.get_full_report()
    
    result = {
        "status": "success",
        "synced": synced,
        "errors": errors,
        "verified": verified_count,
        "conflicts": conflict_count,
        "total_in_graph": len(graph.nodes),
        "forgetting": stats.get("forgetting", {}),
        "conflicts_summary": stats.get("conflicts", {})
    }
    
    # 输出结果
    print(f"\n{'='*60}")
    print(f"✅ 同步完成!")
    print(f"{'='*60}")
    print(f"  📝 新增: {synced} 条")
    print(f"  ❌ 失败: {errors} 条")
    print(f"  🔍 验证通过: {verified_count}/{synced}")
    print(f"  ⚠️ 冲突: {conflict_count}")
    print(f"  📊 图谱总数: {len(graph.nodes)} 条")
    
    if stats.get("forgetting"):
        f = stats["forgetting"]
        print(f"\n  📈 遗忘状态:")
        print(f"    🟢 新鲜: {f.get('fresh', 0)}")
        print(f"    🟡 正常: {f.get('normal', 0)}")
        print(f"    🟠 老化: {f.get('aging', 0)}")
        print(f"    🔴 衰减: {f.get('fading', 0)}")
    
    print(f"\n💾 状态已保存到: {STATE_FILE}")
    print(f"   中断后可继续: python sync_to_magma.py")
    print(f"{'='*60}")
    
    return result


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='MAGMA Wiki 同步工具')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际写入')
    parser.add_argument('--force', action='store_true', help='强制重新写入所有文件')
    parser.add_argument('--reset', action='store_true', help='重置进度，从头开始')
    
    args = parser.parse_args()
    
    try:
        result = sync_to_magma(dry_run=args.dry_run, force=args.force, reset=args.reset)
    except KeyboardInterrupt:
        print("\n\n⚠️ 中断已保存进度，下次运行会自动继续")
        save_sync_state(state)
        sys.exit(0)
    
    if result["status"] in ("empty", "up_to_date", "dry_run"):
        sys.exit(0)
    elif result.get("errors", 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
