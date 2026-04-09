#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LINT 维护脚本
定期检查知识库健康状况：
1. 孤儿链接检查（有链接但页面不存在）
2. 矛盾说法检查（同一概念不同页面有冲突）
3. 空页面/短页面检查
4. 重复内容检查
"""

import re
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# 配置
WIKI_DIR = Path(__file__).parent / "wiki"
RAW_DIR = Path(__file__).parent / "raw"
LOG_FILE = WIKI_DIR / "log.md"


def scan_wiki_pages():
    """扫描所有 wiki 页面"""
    pages = {}
    for md_file in WIKI_DIR.rglob("*.md"):
        if md_file.name == "index.md" or md_file.name == "log.md":
            continue
        rel_path = md_file.relative_to(WIKI_DIR)
        content = md_file.read_text(encoding='utf-8')
        pages[str(rel_path)] = {
            'path': md_file,
            'content': content,
            'title': md_file.stem,
            'links': extract_links(content)
        }
    return pages


def extract_links(content: str) -> list:
    """提取 [[双向链接]] 中的链接目标"""
    pattern = r'\[\[([^\]]+)\]\]'
    return re.findall(pattern, content)


def check_orphan_links(pages: dict) -> dict:
    """检查孤儿链接（链接存在但目标页面不存在）"""
    orphans = []
    
    for page_path, page_data in pages.items():
        for link in page_data['links']:
            # 尝试多种扩展名
            found = False
            for ext in ['.md', '/index.md']:
                # 链接可能是页面名或路径
                link_path = Path(link.replace('/', os.sep).replace('\\', os.sep))
                
                # 搜索所有可能的路径
                for page_file in WIKI_DIR.rglob("*.md"):
                    if page_file.stem == link or page_file.name == link + '.md':
                        found = True
                        break
                
                if found:
                    break
            
            if not found:
                orphans.append({
                    'source': page_path,
                    'link': link,
                    'type': 'orphan'
                })
    
    return orphans


def check_empty_short_pages(pages: dict) -> list:
    """检查空页面或过短页面"""
    issues = []
    MIN_LENGTH = 100  # 最少 100 字符
    
    for page_path, page_data in pages.items():
        content = page_data['content']
        # 去除 markdown 格式后计算纯文本长度
        plain = re.sub(r'[#*`\[\]()>_~\-]', '', content)
        plain = re.sub(r'\n+', '\n', plain).strip()
        
        if len(plain) < MIN_LENGTH:
            issues.append({
                'page': page_path,
                'length': len(plain),
                'type': 'too_short'
            })
    
    return issues


def check_duplicate_titles(pages: dict) -> list:
    """检查重复标题（相似名称的页面可能是重复的）"""
    titles = defaultdict(list)
    
    for page_path, page_data in pages.items():
        # 按标题分组
        titles[page_data['title']].append(page_path)
    
    duplicates = []
    for title, paths in titles.items():
        if len(paths) > 1:
            duplicates.append({
                'title': title,
                'pages': paths,
                'type': 'duplicate'
            })
    
    return duplicates


def check_conflicts(pages: dict) -> list:
    """检查矛盾说法（简化版：检查同一关键词在不同页面的定义）"""
    # 这是一个简化版本，完整版本需要 NLP
    # 这里只检查标题相似的页面是否有冲突
    
    conflicts = []
    title_groups = defaultdict(list)
    
    for page_path, page_data in pages.items():
        # 提取前3个词作为组键
        words = page_data['title'].split()[:3]
        if words:
            group_key = ' '.join(words)
            title_groups[group_key].append((page_path, page_data))
    
    for group_key, group_pages in title_groups.items():
        if len(group_pages) > 1:
            # 检查内容是否有重叠
            contents = [p[1]['content'] for p in group_pages]
            # 简化：只报告，不做深入分析
            conflicts.append({
                'group': group_key,
                'pages': [p[0] for p in group_pages],
                'type': 'potential_conflict',
                'note': '需要人工检查这些页面是否有矛盾'
            })
    
    return conflicts


def check_missing_structure(pages: dict) -> dict:
    """检查目录结构是否完整"""
    issues = []
    
    required_dirs = ['实体', '概念', '来源']
    for dir_name in required_dirs:
        dir_path = WIKI_DIR / dir_name
        if not dir_path.exists():
            issues.append({
                'type': 'missing_dir',
                'path': str(dir_path.relative_to(WIKI_DIR)),
                'severity': 'high'
            })
    
    # 检查 index.md
    index_path = WIKI_DIR / "index.md"
    if not index_path.exists():
        issues.append({
            'type': 'missing_file',
            'path': 'index.md',
            'severity': 'high'
        })
    
    return issues


def generate_log_entry(checks: dict, issues_count: int) -> str:
    """生成 log.md 的追加条目"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    entry = f"""

## LINT 检查报告 - {timestamp}

**问题总数**: {issues_count}

"""
    
    if checks.get('orphan_links'):
        entry += f"\n### 孤儿链接 ({len(checks['orphan_links'])} 项)\n\n"
        for o in checks['orphan_links']:
            entry += f"- [[{o['link']}]] (来源: {o['source']})\n"
    
    if checks.get('empty_pages'):
        entry += f"\n### 空/短页面 ({len(checks['empty_pages'])} 项)\n\n"
        for e in checks['empty_pages']:
            entry += f"- {e['page']} (长度: {e['length']} 字符)\n"
    
    if checks.get('duplicates'):
        entry += f"\n### 重复页面 ({len(checks['duplicates'])} 项)\n\n"
        for d in checks['duplicates']:
            entry += f"- 标题「{d['title']}」出现在:\n"
            for p in d['pages']:
                entry += f"  - {p}\n"
    
    if checks.get('conflicts'):
        entry += f"\n### 潜在矛盾 ({len(checks['conflicts'])} 项)\n\n"
        for c in checks['conflicts']:
            entry += f"- 组「{c['group']}」:\n"
            for p in c['pages']:
                entry += f"  - {p}\n"
    
    if checks.get('structure'):
        entry += f"\n### 目录结构问题 ({len(checks['structure'])} 项)\n\n"
        for s in checks['structure']:
            entry += f"- [{s['severity']}] {s['type']}: {s['path']}\n"
    
    if issues_count == 0:
        entry += "\n✅ 知识库健康，没有发现问题！\n"
    
    return entry


async def run_lint_async():
    """异步运行 LINT 检查"""
    print("=" * 50)
    print("WIKI LINT - Knowledge Base Health Check")
    print("=" * 50)
    print()
    
    # 扫描页面
    print("[1/5] Scanning wiki pages...")
    pages = scan_wiki_pages()
    print(f"      Found {len(pages)} pages")
    print()
    
    # 执行各项检查
    print("[2/5] Checking orphan links...")
    orphans = check_orphan_links(pages)
    print(f"      Found {len(orphans)} orphan links")
    print()
    
    print("[3/5] Checking empty/short pages...")
    empty_pages = check_empty_short_pages(pages)
    print(f"      Found {len(empty_pages)} short pages")
    print()
    
    print("[4/5] Checking duplicates & conflicts...")
    duplicates = check_duplicate_titles(pages)
    conflicts = check_conflicts(pages)
    print(f"      Found {len(duplicates)} duplicates, {len(conflicts)} potential conflicts")
    print()
    
    print("[5/5] Checking directory structure...")
    structure_issues = check_missing_structure(pages)
    print(f"      Found {len(structure_issues)} structure issues")
    print()
    
    # 汇总
    checks = {
        'orphan_links': orphans,
        'empty_pages': empty_pages,
        'duplicates': duplicates,
        'conflicts': conflicts,
        'structure': structure_issues
    }
    
    total_issues = len(orphans) + len(empty_pages) + len(duplicates) + len(conflicts) + len(structure_issues)
    
    print("=" * 50)
    print(f"HEALTH CHECK COMPLETE")
    print(f"Total issues: {total_issues}")
    print("=" * 50)
    
    # 详细报告
    if orphans:
        print(f"\n[ORPHANS] {len(orphans)} orphan links found:")
        for o in orphans[:10]:
            print(f"  - [[{o['link']}]] -> from {o['source']}")
        if len(orphans) > 10:
            print(f"  ... and {len(orphans) - 10} more")
    
    if empty_pages:
        print(f"\n[SHORT PAGES] {len(empty_pages)} pages too short:")
        for e in empty_pages[:10]:
            print(f"  - {e['page']} ({e['length']} chars)")
        if len(empty_pages) > 10:
            print(f"  ... and {len(empty_pages) - 10} more")
    
    if structure_issues:
        print(f"\n[STRUCTURE] {len(structure_issues)} structure issues:")
        for s in structure_issues:
            print(f"  - [{s['severity']}] {s['type']}: {s['path']}")
    
    # 追加到 log.md
    print(f"\n[LOG] Appending to wiki/log.md...")
    log_entry = generate_log_entry(checks, total_issues)
    LOG_FILE.parent.mkdir(exist_ok=True)
    
    if LOG_FILE.exists():
        existing = LOG_FILE.read_text(encoding='utf-8')
    else:
        existing = "# Wiki 操作日志\n\n> 本文件记录所有 wiki 的操作历史。\n"
    
    LOG_FILE.write_text(existing + log_entry, encoding='utf-8')
    print(f"      [OK] Log updated")
    
    return checks


def main():
    """主函数"""
    import asyncio
    asyncio.run(run_lint_async())


if __name__ == '__main__':
    main()
