#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Karpathy 知识库 Lint 工具 v2
定时自动执行知识库健康检查
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from collections import defaultdict

# ========== 配置 ==========
WIKI_DIR = Path(__file__).parent / "wiki"
WIKI_CONCEPTS = WIKI_DIR / "概念"
WIKI_SOURCES = WIKI_DIR / "来源"
WIKI_ENTITIES = WIKI_DIR / "实体"
REPORT_FILE = Path(__file__).parent / ".lint_report.json"

# ========== Lint检查项 ==========

def check_orphan_links() -> List[Dict]:
    """检查孤儿链接（引用但不存在的页面）"""
    issues = []
    
    # 收集所有页面中的链接
    all_links = set()
    existing_pages = set()
    
    for wiki_dir in [WIKI_CONCEPTS, WIKI_SOURCES, WIKI_ENTITIES]:
        if not wiki_dir.exists():
            continue
        for md_file in wiki_dir.glob("*.md"):
            existing_pages.add(md_file.stem)
            content = md_file.read_text(encoding='utf-8')
            # 提取 [[链接]]
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            for link in links:
                all_links.add(link.strip())
    
    # 找孤儿链接
    for link in all_links:
        if link not in existing_pages:
            issues.append({
                "type": "orphan_link",
                "link": link,
                "severity": "warning",
                "message": f"链接 [[{link}]] 指向不存在的页面"
            })
    
    return issues

def check_empty_pages() -> List[Dict]:
    """检查空页面或过短页面"""
    issues = []
    
    min_chars = 100  # 最小字符数
    
    for wiki_dir in [WIKI_CONCEPTS, WIKI_SOURCES, WIKI_ENTITIES]:
        if not wiki_dir.exists():
            continue
        for md_file in wiki_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            # 移除markdown格式
            text = re.sub(r'[#*_\[\]`>\n]', '', content)
            text = text.strip()
            
            if len(text) < min_chars:
                issues.append({
                    "type": "empty_page",
                    "file": str(md_file.relative_to(WIKI_DIR)),
                    "severity": "warning",
                    "message": f"页面过短 ({len(text)} 字符): {md_file.name}"
                })
    
    return issues

def check_contradictions() -> List[Dict]:
    """检查矛盾说法（同一概念在不同页面有冲突）"""
    issues = []
    
    # 收集同一概念的不同描述
    concept_descriptions = defaultdict(list)
    
    for wiki_dir in [WIKI_CONCEPTS, WIKI_ENTITIES]:
        if not wiki_dir.exists():
            continue
        for md_file in wiki_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            # 提取第一段描述
            lines = [l.strip() for l in content.split('\n') if l.strip() and not l.strip().startswith('#')]
            if lines:
                first_para = lines[0][:200]  # 取前200字符
                concept_descriptions[md_file.stem].append({
                    "file": md_file.name,
                    "desc": first_para
                })
    
    # 简单矛盾检测：同一stem的多个文件
    # （这里可以扩展更复杂的语义对比）
    for concept, descs in concept_descriptions.items():
        if len(descs) > 1:
            # 名字相似但内容不同
            first_descs = [d['desc'] for d in descs]
            if len(set(first_descs)) > 1:
                issues.append({
                    "type": "potential_contradiction",
                    "concept": concept,
                    "severity": "info",
                    "message": f"概念 '{concept}' 有 {len(descs)} 个不同来源，可能需要合并"
                })
    
    return issues

def check_duplicate_pages() -> List[Dict]:
    """检查重复页面"""
    issues = []
    
    # 收集所有页面标题
    titles = defaultdict(list)
    
    for wiki_dir in [WIKI_CONCEPTS, WIKI_SOURCES, WIKI_ENTITIES]:
        if not wiki_dir.exists():
            continue
        for md_file in wiki_dir.glob("*.md"):
            # 提取标题
            content = md_file.read_text(encoding='utf-8')
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                title = title_match.group(1).strip().lower()
                titles[title].append(str(md_file.relative_to(WIKI_DIR)))
    
    # 找重复标题
    for title, files in titles.items():
        if len(files) > 1:
            issues.append({
                "type": "duplicate_title",
                "title": title,
                "files": files,
                "severity": "warning",
                "message": f"标题 '{title}' 出现 {len(files)} 次: {', '.join(files)}"
            })
    
    return issues

def check_outdated_sources() -> List[Dict]:
    """检查过时来源（超过30天未更新的来源页）"""
    issues = []
    
    if not WIKI_SOURCES.exists():
        return issues
    
    import time
    
    for md_file in WIKI_SOURCES.glob("*.md"):
        content = md_file.read_text(encoding='utf-8')
        # 提取摄入时间
        time_match = re.search(r'摄入时间[：:](\d{4}-\d{2}-\d{2})', content)
        if time_match:
            date_str = time_match.group(1)
            try:
                file_time = datetime.strptime(date_str, '%Y-%m-%d')
                days_ago = (datetime.now() - file_time).days
                
                if days_ago > 30:
                    issues.append({
                        "type": "outdated_source",
                        "file": str(md_file.relative_to(WIKI_DIR)),
                        "severity": "info",
                        "message": f"来源页超过 {days_ago} 天未更新: {md_file.name}"
                    })
            except:
                pass
    
    return issues

def check_unreviewed_pages() -> List[Dict]:
    """检查未验收页面"""
    issues = []
    
    for wiki_dir in [WIKI_CONCEPTS, WIKI_SOURCES, WIKI_ENTITIES]:
        if not wiki_dir.exists():
            continue
        for md_file in wiki_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            
            # 检查是否有待验收标记
            if '⏳' in content or '待验收' in content or 'pending' in content.lower():
                issues.append({
                    "type": "unreviewed",
                    "file": str(md_file.relative_to(WIKI_DIR)),
                    "severity": "info",
                    "message": f"待验收页面: {md_file.name}"
                })
    
    return issues

def run_lint() -> Dict:
    """执行所有检查"""
    print("=" * 60)
    print("Karpathy 知识库 Lint 检查 v2")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    all_issues = []
    
    checks = [
        ("孤儿链接", check_orphan_links),
        ("空页面", check_empty_pages),
        ("矛盾说法", check_contradictions),
        ("重复页面", check_duplicate_pages),
        ("过时来源", check_outdated_sources),
        ("未验收页面", check_unreviewed_pages),
    ]
    
    print("\n[检查中...]")
    for name, check_func in checks:
        print(f"  - {name}...")
        try:
            issues = check_func()
            all_issues.extend(issues)
            print(f"    发现 {len(issues)} 个问题")
        except Exception as e:
            print(f"    [ERROR] {e}")
    
    # 统计
    severity_counts = defaultdict(int)
    for issue in all_issues:
        severity_counts[issue['severity']] += 1
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "total_issues": len(all_issues),
        "by_severity": dict(severity_counts),
        "issues": all_issues
    }
    
    # 保存报告
    REPORT_FILE.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    
    # 输出
    print(f"\n[结果]")
    print(f"  总问题: {len(all_issues)}")
    print(f"  🔴 error: {severity_counts.get('error', 0)}")
    print(f"  🟡 warning: {severity_counts.get('warning', 0)}")
    print(f"  🔵 info: {severity_counts.get('info', 0)}")
    
    if all_issues:
        print(f"\n[问题详情]")
        for i, issue in enumerate(all_issues[:20], 1):
            print(f"  {i}. [{issue['severity']}] {issue['message']}")
        if len(all_issues) > 20:
            print(f"  ... 还有 {len(all_issues) - 20} 个问题")
    
    print(f"\n[报告已保存] {REPORT_FILE}")
    
    return result

# ========== CLI ==========

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Karpathy 知识库 Lint 检查')
    parser.add_argument('--json', '-j', action='store_true', help='输出JSON格式')
    parser.add_argument('--watch', '-w', action='store_true', help='持续监控模式')
    
    args = parser.parse_args()
    
    if args.watch:
        import time
        print("[MODE] 持续监控模式 (Ctrl+C 退出)")
        while True:
            run_lint()
            print("\n[WAIT] 60秒后再次检查...")
            time.sleep(60)
    else:
        result = run_lint()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
