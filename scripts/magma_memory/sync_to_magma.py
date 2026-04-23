#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
sync_to_magma.py - 将 compile.py 编译后的 wiki 页面同步到 MAGMA 图谱

功能：
1. 扫描 wiki/*.md 文件（排除 index.md / log.md）
2. 解析页面内容，提取标题/链接/概念
3. 使用 MemoryWriter 写入 MAGMA 图谱
4. 集成遗忘机制 + 冲突检测 + 检索验证
5. 避免重复写入（基于内容指纹）

用法：
  python sync_to_magma.py              # 全量同步
  python sync_to_magma.py --dry-run   # 预览模式
  python sync_to_magma.py --force     # 强制重新写入
"""
import sys
import io
import re
import hashlib
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
MAGMA_DIR = project_root / "scripts" / "magma_memory" / "data"
GRAPH_FILE = MAGMA_DIR / "magma_graph.json"

# 排除的文件
EXCLUDE_FILES = {"index.md", "log.md", "CLAUDE.md", ".cursorrules.md"}

# 支持的扩展名
SUPPORTED_EXTS = {".md", ".txt"}


def compute_fingerprint(content: str) -> str:
    """计算内容指纹，用于检测重复"""
    # 取前200字符的MD5
    sample = content[:200].strip()
    return hashlib.md5(sample.encode('utf-8')).hexdigest()[:12]


def extract_wiki_content(file_path: Path) -> Optional[Dict]:
    """
    解析 wiki 页面，提取关键信息
    
    Returns:
        Dict with keys: title, content, links, concepts, source, fingerprint
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  ⚠️ 读取失败 {file_path.name}: {e}")
        return None
    
    if not content.strip():
        return None
    
    # 提取标题（第一个 # 标题）
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem
    
    # 提取所有 [[双向链接]]
    links = re.findall(r'\[\[([^\]]+)\]\]', content)
    # 去重
    links = list(set(links))
    
    # 过滤纯链接（如 [[文件名.md]] 保留，去掉 [[概念名]])
    md_links = [l for l in links if l.endswith('.md')]
    
    # 提取概念（不是 .md 的链接）
    concepts = [l for l in links if not l.endswith('.md')]
    
    # 生成摘要（前500字符）
    summary = content[:500].strip()
    
    # 计算指纹
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
        print(f"❌ Wiki 目录不存在: {WIKI_DIR}")
        return files
    
    for f in WIKI_DIR.rglob("*"):
        if f.is_file() and f.suffix in SUPPORTED_EXTS:
            if f.name in EXCLUDE_FILES:
                continue
            files.append(f)
    
    return files


def load_existing_fingerprints() -> Set[str]:
    """加载已有的内容指纹，避免重复写入"""
    fingerprints = set()
    
    if GRAPH_FILE.exists():
        try:
            import json
            with open(GRAPH_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 从已有节点提取指纹（存在 semantic_keywords 最后一位）
            for node_data in data.get("nodes", {}).values():
                keywords = node_data.get("semantic_keywords", [])
                for kw in keywords:
                    if kw.startswith("fp:"):
                        fingerprints.add(kw)
        except Exception as e:
            print(f"  ⚠️ 加载已有指纹失败: {e}")
    
    return fingerprints


def sync_to_magma(dry_run: bool = False, force: bool = False) -> Dict:
    """
    同步 wiki 到 MAGMA 图谱
    
    Args:
        dry_run: True=预览模式，不实际写入
        force: True=强制重新写入所有文件
    
    Returns:
        同步报告
    """
    print("\n" + "="*60)
    print("🔄 MAGMA Wiki 同步工具")
    print("="*60)
    print(f"Wiki 目录: {WIKI_DIR}")
    print(f"图谱文件: {GRAPH_FILE}")
    print(f"模式: {'🔍 预览模式' if dry_run else '✅ 正式写入'}")
    print()
    
    # 1. 扫描文件
    print("📂 [1/5] 扫描 wiki 文件...")
    files = scan_wiki_files()
    print(f"  找到 {len(files)} 个文件")
    
    if not files:
        print("❌ 没有找到需要同步的文件")
        return {"status": "empty", "synced": 0}
    
    # 2. 解析内容
    print("\n📝 [2/5] 解析页面内容...")
    pages = []
    for f in files:
        page = extract_wiki_content(f)
        if page:
            pages.append(page)
    print(f"  成功解析 {len(pages)} 个页面")
    
    # 3. 检查已有指纹
    print("\n🔐 [3/5] 检查已有数据...")
    existing_fps = load_existing_fingerprints()
    print(f"  已有指纹: {len(existing_fps)} 条")
    
    # 4. 过滤需要同步的
    to_sync = []
    skipped = 0
    for page in pages:
        fp = page["fingerprint"]
        if fp in existing_fps and not force:
            skipped += 1
        else:
            to_sync.append(page)
    
    print(f"  需要同步: {len(to_sync)} 个")
    print(f"  跳过（已存在）: {skipped} 个")
    
    if dry_run:
        print("\n🔍 预览模式 - 前5个待同步文件:")
        for page in to_sync[:5]:
            print(f"  - {page['title']} ({len(page['content'])}字符)")
        return {"status": "dry_run", "to_sync": len(to_sync), "skipped": skipped}
    
    if not to_sync:
        print("\n✅ 所有文件已是最新，无需同步")
        return {"status": "up_to_date", "synced": 0}
    
    # 5. 写入 MAGMA
    print("\n💾 [4/5] 写入 MAGMA 图谱...")
    
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
    
    for i, page in enumerate(to_sync, 1):
        try:
            # 构建写入内容
            wiki_content = f"""【{page['title']}】

📁 来源: {page['file_path']}
🔗 链接: {', '.join(page['links']) if page['links'] else '无'}
🏷️ 概念: {', '.join(page['concepts']) if page['concepts'] else '无'}

{page['summary']}"""
            
            # 使用 fingerprint 作为关键词标记（用于去重）
            keywords = [f"fp:{page['fingerprint']}"]
            if page['links']:
                # 从链接提取文件名作为关键词
                for link in page['links'][:3]:
                    keywords.append(link.replace('.md', ''))
            if page['concepts']:
                keywords.extend(page['concepts'][:5])
            
            # 写入
            node_id, report = writer.add(
                content=wiki_content,
                source="wiki-sync",
                keywords=keywords,
                importance=0.7  # wiki 来源重要性设为 0.7
            )
            
            if report['verified']:
                verified_count += 1
            if report['conflicts']:
                conflict_count += len(report['conflicts'])
            
            synced += 1
            
            if i % 20 == 0:
                print(f"  已处理 {i}/{len(to_sync)}...")
        
        except Exception as e:
            errors += 1
            print(f"  ❌ 写入失败 {page['title']}: {e}")
    
    # 6. 获取统计
    print("\n📊 [5/5] 生成报告...")
    stats = writer.get_full_report()
    
    result = {
        "status": "success",
        "synced": synced,
        "errors": errors,
        "skipped": skipped,
        "verified": verified_count,
        "conflicts": conflict_count,
        "forgetting": stats.get("forgetting", {}),
        "conflicts_summary": stats.get("conflicts", {})
    }
    
    # 输出结果
    print(f"\n✅ 同步完成!")
    print(f"  新增: {synced} 条")
    print(f"  跳过: {skipped} 条")
    print(f"  失败: {errors} 条")
    print(f"  验证通过: {verified_count}/{synced}")
    print(f"  冲突: {conflict_count}")
    
    if stats.get("forgetting"):
        f = stats["forgetting"]
        print(f"\n📈 遗忘状态:")
        print(f"  🟢 新鲜: {f.get('fresh', 0)}")
        print(f"  🟡 正常: {f.get('normal', 0)}")
        print(f"  🟠 老化: {f.get('aging', 0)}")
        print(f"  🔴 衰减: {f.get('fading', 0)}")
    
    print("\n" + "="*60)
    
    return result


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='MAGMA Wiki 同步工具')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际写入')
    parser.add_argument('--force', action='store_true', help='强制重新写入所有文件')
    
    args = parser.parse_args()
    
    result = sync_to_magma(dry_run=args.dry_run, force=args.force)
    
    # 返回退出码
    if result["status"] in ("empty", "up_to_date", "dry_run"):
        sys.exit(0)
    elif result.get("errors", 0) > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
