#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Karpathy 知识库 验收机制
支持页面的待验收→已验收流程
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

# ========== 配置 ==========
WIKI_DIR = Path(__file__).parent / "wiki"
WIKI_CONCEPTS = WIKI_DIR / "概念"
WIKI_SOURCES = WIKI_DIR / "来源"
WIKI_ENTITIES = WIKI_DIR / "实体"
REVIEW_LOG = Path(__file__).parent / ".review_log.json"

# ========== 状态枚举 ==========

class ReviewStatus(Enum):
    PENDING = "pending"      # ⏳ 待验收
    APPROVED = "approved"    # ✅ 已验收
    REJECTED = "rejected"   # ❌ 需修改

STATUS_ICONS = {
    ReviewStatus.PENDING: "⏳",
    ReviewStatus.APPROVED: "✅",
    ReviewStatus.REJECTED: "❌"
}

# ========== 验收日志 ==========

def load_review_log() -> dict:
    """加载验收日志"""
    if REVIEW_LOG.exists():
        return json.loads(REVIEW_LOG.read_text(encoding='utf-8'))
    return {"pages": {}, "history": []}

def save_review_log(log: dict):
    """保存验收日志"""
    REVIEW_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')

def add_history(log: dict, action: str, page: str, old_status: str, new_status: str, note: str = ""):
    """添加历史记录"""
    log["history"].append({
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "page": page,
        "old_status": old_status,
        "new_status": new_status,
        "note": note
    })

# ========== 页面验收操作 ==========

def get_page_status(content: str) -> ReviewStatus:
    """从页面内容中提取验收状态"""
    if '✅' in content or 'approved' in content.lower():
        return ReviewStatus.APPROVED
    elif '❌' in content or 'rejected' in content.lower():
        return ReviewStatus.REJECTED
    elif '⏳' in content or 'pending' in content.lower():
        return ReviewStatus.PENDING
    return ReviewStatus.PENDING  # 默认待验收

def update_page_status(file_path: Path, new_status: ReviewStatus, note: str = "") -> bool:
    """更新页面验收状态"""
    try:
        content = file_path.read_text(encoding='utf-8')
        old_status = get_page_status(content)
        
        # 替换状态标记
        for status in ReviewStatus:
            icon = STATUS_ICONS[status]
            content = re.sub(rf'{re.escape(icon)}\s*\w+', f'{icon} {status.value}', content)
            content = re.sub(rf'status[:\s]*\w+', f'status: {status.value}', content, flags=re.IGNORECASE)
        
        # 添加新的状态标记
        if '> 验收状态' in content or '> AI生成' in content:
            # 替换现有状态行
            content = re.sub(
                r'(> (?:验收状态|AI生成)[:\s]*).*',
                rf'\g<1>{STATUS_ICONS[new_status]} {new_status.value}',
                content
            )
        else:
            # 添加状态行
            content = content.strip()
            content += f"\n> 验收状态：{STATUS_ICONS[new_status]} {new_status.value}"
        
        # 添加备注
        if note:
            content += f"\n> 验收备注：{note}"
        
        # 添加验收时间
        content += f"\n> 验收时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        file_path.write_text(content, encoding='utf-8')
        
        # 更新日志
        log = load_review_log()
        add_history(log, "update_status", str(file_path.relative_to(WIKI_DIR)), 
                   old_status.value, new_status.value, note)
        log["pages"][str(file_path.relative_to(WIKI_DIR))] = {
            "status": new_status.value,
            "updated_at": datetime.now().isoformat(),
            "note": note
        }
        save_review_log(log)
        
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def list_pages_by_status(status: Optional[ReviewStatus] = None) -> List[Dict]:
    """列出所有页面，按状态分组"""
    pages = []
    
    for wiki_dir in [WIKI_CONCEPTS, WIKI_SOURCES, WIKI_ENTITIES]:
        if not wiki_dir.exists():
            continue
        
        for md_file in wiki_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            page_status = get_page_status(content) if status is None else status
            
            if status is None or page_status == status:
                pages.append({
                    "file": str(md_file.relative_to(WIKI_DIR)),
                    "path": md_file,
                    "status": page_status,
                    "title": md_file.stem
                })
    
    return sorted(pages, key=lambda x: (x['status'].value, x['file']))

def approve_page(file_path: Path, note: str = "") -> bool:
    """验收通过页面"""
    return update_page_status(file_path, ReviewStatus.APPROVED, note)

def reject_page(file_path: Path, note: str = "") -> bool:
    """拒绝页面"""
    return update_page_status(file_path, ReviewStatus.REJECTED, note)

def pending_page(file_path: Path, note: str = "") -> bool:
    """标记为待验收"""
    return update_page_status(file_path, ReviewStatus.PENDING, note)

# ========== 批量操作 ==========

def batch_approve(pattern: str = "*.md", dry_run: bool = False) -> int:
    """批量验收通过"""
    count = 0
    pages = list_pages_by_status(ReviewStatus.PENDING)
    
    for page in pages:
        if re.match(pattern.replace('*', '.*'), page['file']):
            if not dry_run:
                if approve_page(page['path']):
                    count += 1
                    print(f"  [OK] ✅ {page['file']}")
            else:
                print(f"  [DRY] ✅ {page['file']}")
                count += 1
    
    return count

def batch_set_status(pattern: str, new_status: ReviewStatus, dry_run: bool = False) -> int:
    """批量设置状态"""
    count = 0
    pages = list_pages_by_status()
    
    for page in pages:
        if re.match(pattern.replace('*', '.*'), page['file']):
            if not dry_run:
                if update_page_status(page['path'], new_status):
                    count += 1
                    print(f"  [OK] {STATUS_ICONS[new_status]} {page['file']}")
            else:
                print(f"  [DRY] {STATUS_ICONS[new_status]} {page['file']}")
                count += 1
    
    return count

# ========== 统计和报告 ==========

def get_review_stats() -> Dict:
    """获取验收统计"""
    pages = list_pages_by_status()
    
    stats = {
        "total": len(pages),
        "pending": 0,
        "approved": 0,
        "rejected": 0,
        "by_type": {
            "concept": {"total": 0, "pending": 0, "approved": 0, "rejected": 0},
            "entity": {"total": 0, "pending": 0, "approved": 0, "rejected": 0},
            "source": {"total": 0, "pending": 0, "approved": 0, "rejected": 0}
        }
    }
    
    for page in pages:
        stats[page['status'].value] += 1
        
        # 按类型统计
        if '概念' in page['file']:
            page_type = "concept"
        elif '实体' in page['file']:
            page_type = "entity"
        elif '来源' in page['file']:
            page_type = "source"
        else:
            page_type = "other"
        
        if page_type in stats["by_type"]:
            stats["by_type"][page_type]["total"] += 1
            stats["by_type"][page_type][page['status'].value] += 1
    
    return stats

def generate_review_report() -> str:
    """生成验收报告"""
    stats = get_review_stats()
    
    report = f"""# 知识库验收报告

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 总体统计

| 状态 | 数量 | 占比 |
|------|------|------|
| ⏳ 待验收 | {stats['pending']} | {stats['pending']/stats['total']*100:.1f}% |
| ✅ 已验收 | {stats['approved']} | {stats['approved']/stats['total']*100:.1f}% |
| ❌ 需修改 | {stats['rejected']} | {stats['rejected']/stats['total']*100:.1f}% |
| **总计** | **{stats['total']}** | 100% |

## 按类型统计

### 概念页
| 状态 | 数量 |
|------|------|
| ⏳ 待验收 | {stats['by_type']['concept']['pending']} |
| ✅ 已验收 | {stats['by_type']['concept']['approved']} |
| ❌ 需修改 | {stats['by_type']['concept']['rejected']} |

### 实体页
| 状态 | 数量 |
|------|------|
| ⏳ 待验收 | {stats['by_type']['entity']['pending']} |
| ✅ 已验收 | {stats['by_type']['entity']['approved']} |
| ❌ 需修改 | {stats['by_type']['entity']['rejected']} |

### 来源页
| 状态 | 数量 |
|------|------|
| ⏳ 待验收 | {stats['by_type']['source']['pending']} |
| ✅ 已验收 | {stats['by_type']['source']['approved']} |
| ❌ 需修改 | {stats['by_type']['source']['rejected']} |

## 待验收页面列表

"""
    
    pending_pages = list_pages_by_status(ReviewStatus.PENDING)
    if pending_pages:
        for page in pending_pages[:50]:
            report += f"- [[{page['file']}]]\n"
        if len(pending_pages) > 50:
            report += f"\n_... 还有 {len(pending_pages) - 50} 个页面_\n"
    else:
        report += "*（所有页面已验收！）*\n"
    
    report += f"""
---
*由 Karpathy 知识库验收系统自动生成*
"""
    
    return report

# ========== CLI ==========

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Karpathy 知识库验收工具')
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # list命令
    list_parser = subparsers.add_parser('list', help='列出页面')
    list_parser.add_argument('--status', '-s', choices=['pending', 'approved', 'rejected'], help='按状态筛选')
    
    # approve命令
    approve_parser = subparsers.add_parser('approve', help='验收通过')
    approve_parser.add_argument('file', nargs='?', help='文件路径')
    approve_parser.add_argument('--all', '-a', action='store_true', help='验收所有待验收页面')
    approve_parser.add_argument('--note', '-n', type=str, default='', help='备注')
    
    # reject命令
    reject_parser = subparsers.add_parser('reject', help='标记需修改')
    reject_parser.add_argument('file', nargs='?', help='文件路径')
    reject_parser.add_argument('--note', '-n', type=str, default='', help='备注')
    
    # report命令
    subparsers.add_parser('report', help='生成验收报告')
    
    # stats命令
    subparsers.add_parser('stats', help='显示统计')
    
    args = parser.parse_args()
    
    if args.command == 'list' or args.command is None:
        status = ReviewStatus(args.status) if args.status else None
        pages = list_pages_by_status(status)
        
        if not pages:
            print("[INFO] 没有找到页面")
            return
        
        print(f"\n[页面列表]")
        for page in pages:
            icon = STATUS_ICONS[page['status']]
            print(f"  {icon} {page['file']}")
        
        print(f"\n共 {len(pages)} 个页面")
    
    elif args.command == 'approve':
        if args.all:
            count = batch_approve()
            print(f"\n[DONE] 批量验收 {count} 个页面")
        elif args.file:
            file_path = WIKI_DIR / args.file
            if file_path.exists():
                if approve_page(file_path, args.note):
                    print(f"[OK] ✅ 已验收: {args.file}")
                else:
                    print(f"[ERROR] 验收失败")
            else:
                print(f"[ERROR] 文件不存在: {args.file}")
        else:
            print("[ERROR] 请指定文件或使用 --all")
    
    elif args.command == 'reject':
        if args.file:
            file_path = WIKI_DIR / args.file
            if file_path.exists():
                if reject_page(file_path, args.note):
                    print(f"[OK] ❌ 已标记需修改: {args.file}")
                else:
                    print(f"[ERROR] 操作失败")
            else:
                print(f"[ERROR] 文件不存在: {args.file}")
        else:
            print("[ERROR] 请指定文件")
    
    elif args.command == 'report':
        report = generate_review_report()
        print(report)
        
        # 保存报告
        report_file = WIKI_DIR / "验收报告.md"
        report_file.write_text(report, encoding='utf-8')
        print(f"\n[报告已保存] {report_file}")
    
    elif args.command == 'stats':
        stats = get_review_stats()
        print(f"\n[验收统计]")
        print(f"  ⏳ 待验收: {stats['pending']}")
        print(f"  ✅ 已验收: {stats['approved']}")
        print(f"  ❌ 需修改: {stats['rejected']}")
        print(f"  总计: {stats['total']}")

if __name__ == '__main__':
    main()
