#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Karpathy 知识库编译器 v5 (整合版)
一个文件搞定所有：compile + lint + review + obsidian导出

使用方法：
  python compile.py                  # 增量摄入
  python compile.py --force          # 全量摄入
  python compile.py --lint          # 健康检查
  python compile.py --review         # 验收管理
  python compile.py --export        # 导出Obsidian
  python compile.py --all           # 全部执行
"""

import os
import sys
import json
import hashlib
import shutil
import requests
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Set
from collections import defaultdict
from enum import Enum

# ========== 配置 ==========
RAW_DIR = Path(__file__).parent / "raw"
WIKI_DIR = Path(__file__).parent / "wiki"
WIKI_CONCEPTS = WIKI_DIR / "概念"
WIKI_SOURCES = WIKI_DIR / "来源"
WIKI_ENTITIES = WIKI_DIR / "实体"
LOG_FILE = WIKI_DIR / "log.md"
CACHE_DIR = Path(__file__).parent / ".compile_cache"
OUTPUT_DIR = Path.home() / "Obsidian Vaults" / "Karpathy Wiki"

# LLM 配置
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen2.5:7b")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")

# 编译配置
BATCH_SIZE = 5
MAX_RETRIES = 2
REQUEST_TIMEOUT = 60
SUPPORTED_EXTENSIONS = {'.md', '.txt', '.json', '.csv'}

# ========== 缓存管理 ==========

def get_cache_dir() -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR

def get_file_hash(file_path: Path) -> str:
    m = hashlib.sha256()
    m.update(str(file_path).as_posix().encode())
    m.update(str(file_path.stat().st_mtime).encode())
    return m.hexdigest()[:16]

def load_processed_cache() -> dict:
    cache_file = get_cache_dir() / "processed_files.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding='utf-8'))
    return {}

def save_processed_cache(cache: dict):
    cache_file = get_cache_dir() / "processed_files.json"
    cache_file.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')

# ========== 核心LLM调用 ==========

def call_llm_stream(prompt: str, model: str = LLM_MODEL, system: str = None) -> str:
    url = f"{OLLAMA_URL}/api/generate"
    data = {
        "model": model,
        "prompt": prompt[:8000],
        "stream": True,
        "options": {"temperature": 0.3, "num_predict": 1024}
    }
    if system:
        data["system"] = system[:2000]
    
    try:
        response = requests.post(url, json=data, timeout=REQUEST_TIMEOUT, stream=True)
        response.raise_for_status()
        result = []
        for line in response.iter_lines():
            if line:
                try:
                    obj = json.loads(line)
                    if 'response' in obj:
                        result.append(obj['response'])
                except:
                    pass
        return ''.join(result).strip()
    except Exception as e:
        return f"[LLM Error: {e}]"

def call_llm(prompt: str, model: str = LLM_MODEL, system: str = None) -> str:
    for retry in range(MAX_RETRIES):
        try:
            return call_llm_stream(prompt, model, system)
        except Exception as e:
            if retry < MAX_RETRIES - 1:
                import time; time.sleep(2 ** retry)
            else:
                return f"[LLM Error after {MAX_RETRIES} retries: {e}]"

# ========== 内容分析 ==========

def extract_json_from_response(response: str) -> Optional[dict]:
    patterns = [r'\{[\s\S]*\}', r'```json\n([\s\S]*?)\n```']
    for pattern in patterns:
        m = re.search(pattern, response)
        if m:
            try:
                json_str = m.group(1) if '```' in m.group() else m.group()
                return json.loads(json_str)
            except:
                continue
    return None

SYSTEM_PROMPT = """你是一个知识整理专家。严格输出JSON格式：
{"concepts":["概念1","概念2"],"entities":["实体1","实体2"],"summary":"50字摘要","category":"分类"}"""

# ========== 文件操作 ==========

def read_file_content(file_path: Path) -> str:
    try:
        if file_path.suffix == '.md':
            return file_path.read_text(encoding='utf-8')
        elif file_path.suffix == '.txt':
            return file_path.read_text(encoding='utf-8')
        elif file_path.suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.dumps(json.load(f), ensure_ascii=False, indent=2)
        elif file_path.suffix == '.csv':
            return file_path.read_text(encoding='utf-8')
        return f"[Binary file: {file_path.name}]"
    except Exception as e:
        return f"[Error reading {file_path.name}: {e}]"

def scan_raw_files() -> list:
    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(RAW_DIR.rglob(f"*{ext}"))
    return sorted(files)

# ========== 编译单个文件 ==========

def compile_single_file(file_path: Path) -> Optional[dict]:
    rel_path = file_path.relative_to(RAW_DIR)
    print(f"\n      [{rel_path}]")
    
    content = read_file_content(file_path)
    if len(content) > 15000:
        content = content[:15000] + "\n\n[内容过长已截断...]"
    
    prompt = f"""分析以下文件，提取概念和实体。

文件: {rel_path}

内容:
{content}

严格输出JSON格式。"""

    result_text = call_llm(prompt, system=SYSTEM_PROMPT)
    
    if result_text.startswith("[LLM Error"):
        print(f"      [ERROR] {result_text}")
        return None
    
    data = extract_json_from_response(result_text)
    
    if not data:
        print(f"      [WARN] 无法解析LLM响应")
        data = {"concepts": [], "entities": [], "summary": f"来自 {rel_path}", "category": "其他"}
    
    data['file_name'] = str(rel_path)
    data['raw_content'] = content[:2000]
    
    print(f"      [OK] 概念: {data.get('concepts', [])[:3] or '无'} | 实体: {data.get('entities', [])[:3] or '无'}")
    return data

# ========== 保存Wiki页面 ==========

def save_source_page(entry: dict):
    file_name = entry.get('file_name', 'unknown')
    date_prefix = datetime.now().strftime('%Y-%m-%d')
    safe_name = re.sub(r'[/\\:?*"<>|]', '_', file_name).replace('.md', '')
    filename = f"{date_prefix}-{safe_name}.md"
    
    content = f"""# 来源摘要：{file_name}

> 原始路径：raw/{file_name}
> 摄入时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
> 验收状态：⏳ pending

## 核心观点

{entry.get('summary', '')}

## 关键细节

{entry.get('raw_content', '')[:1000]}

## 相关实体
"""
    for e in entry.get('entities', []):
        content += f"- [[{e}]]\n"
    
    content += "\n## 相关概念\n"
    for c in entry.get('concepts', []):
        content += f"- [[{c}]]\n"
    
    content += f"\n---\n*由 Karpathy 知识库系统自动生成*\n"
    
    WIKI_SOURCES.mkdir(parents=True, exist_ok=True)
    (WIKI_SOURCES / filename).write_text(content, encoding='utf-8')

def save_concept_page(concept: str, entry: dict):
    safe_name = re.sub(r'[/\\:?*"<>|]', '_', concept).replace('[[', '').replace(']]', '')
    if not safe_name:
        return
    
    article = call_llm(f"为概念「{safe_name}」生成简短的 wiki 段落，100字以内，包含定义。",
        system="你是技术文档写作专家，输出简洁的段落。")
    
    if article.startswith("[LLM Error]"):
        article = f"关于 {safe_name} 的概念页。"
    
    content = f"""# {safe_name}

> 分类：概念
> 创建时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
> AI生成：⏳ pending

{article}

## 相关概念
"""
    for c in entry.get('concepts', []):
        if c != concept:
            content += f"- [[{c}]]\n"
    for e in entry.get('entities', []):
        content += f"- [[{e}]]\n"
    
    content += f"""
## 来源
- [[{datetime.now().strftime('%Y-%m-%d')}-{entry.get('file_name', 'unknown')}]]

---
*由 Karpathy 知识库系统自动生成*
"""
    
    WIKI_CONCEPTS.mkdir(parents=True, exist_ok=True)
    (WIKI_CONCEPTS / f"{safe_name}.md").write_text(content, encoding='utf-8')

def save_entity_page(entity: str, entry: dict):
    safe_name = re.sub(r'[/\\:?*"<>|]', '_', entity).replace('[[', '').replace(']]', '')
    if not safe_name:
        return
    
    content = f"""# {safe_name}

> 类型：实体
> 创建时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 简介

{entry.get('summary', '')}

## 相关概念
"""
    for c in entry.get('concepts', []):
        content += f"- [[{c}]]\n"
    for e in entry.get('entities', []):
        if e != entity:
            content += f"- [[{e}]]\n"
    
    content += f"""
## 来源
- [[{datetime.now().strftime('%Y-%m-%d')}-{entry.get('file_name', 'unknown')}]]

---
*由 Karpathy 知识库系统自动生成*
"""
    
    WIKI_ENTITIES.mkdir(parents=True, exist_ok=True)
    (WIKI_ENTITIES / f"{safe_name}.md").write_text(content, encoding='utf-8')

# ========== 索引和日志 ==========

def update_index(entries: list):
    concepts, entities = set(), set()
    for e in entries:
        for c in e.get('concepts', []): concepts.add(c)
        for en in e.get('entities', []): entities.add(en)
    
    content = f"""# 知识库索引

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 统计

- 本次处理：{len(entries)} 个文件
- 总概念数：{len(concepts)}
- 总实体数：{len(entities)}

## 最近来源

"""
    for p in sorted(entries, key=lambda x: x.get('file_name', ''), reverse=True)[:10]:
        content += f"- [[{p.get('file_name', 'unknown')}]]\n"
    
    content += "\n## 概念\n\n"
    for c in sorted(concepts): content += f"- [[{c}]]\n"
    
    content += "\n## 实体\n\n"
    if entities:
        for e in sorted(entities): content += f"- [[{e}]]\n"
    else:
        content += "*（暂无实体）*\n"
    
    (WIKI_DIR / "index.md").write_text(content, encoding='utf-8')
    print(f"\n      [OK] 索引已更新")

def append_log(action: str, details: str):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    entry = f"\n## {timestamp} - {action}\n{details}\n"
    
    if LOG_FILE.exists():
        existing = LOG_FILE.read_text(encoding='utf-8')
    else:
        existing = "# Wiki 操作日志\n\n> 本文件记录所有 wiki 的操作历史。\n"
    
    LOG_FILE.write_text(existing + entry, encoding='utf-8')

# ========== 主摄入流程 ==========

def run_ingest(force: bool = False, batch_size: int = BATCH_SIZE):
    print("=" * 60)
    print("Karpathy 知识库编译器 v5 (整合版)")
    print(f"LLM: {LLM_MODEL}")
    print("=" * 60)
    
    print("\n[1/5] 扫描 raw 目录...")
    raw_files = scan_raw_files()
    print(f"      找到 {len(raw_files)} 个文件")
    
    if not raw_files:
        print("      [WARN] 没有找到文件")
        return
    
    print("\n[2/5] 检查增量文件...")
    cache = load_processed_cache()
    to_process = [f for f in raw_files if force or str(f.relative_to(RAW_DIR)) not in cache or get_file_hash(f) != cache.get(str(f.relative_to(RAW_DIR)))]
    
    if not to_process:
        print("      [SKIP] 所有文件已是最新")
        return
    
    print(f"      模式：{'全量' if force else '增量'} - {len(to_process)}/{len(raw_files)} 文件需要处理")
    
    print(f"\n[3/5] 分批编译 (每批 {batch_size} 个)...")
    entries = []
    total_batches = (len(to_process) + batch_size - 1) // batch_size
    
    for i in range(0, len(to_process), batch_size):
        batch = to_process[i:i+batch_size]
        batch_num = i // batch_size + 1
        print(f"\n      === 批次 {batch_num}/{total_batches} ===")
        
        for file_path in batch:
            entry = compile_single_file(file_path)
            if entry:
                entries.append(entry)
                save_source_page(entry)
                for concept in entry.get('concepts', []): save_concept_page(concept, entry)
                for entity in entry.get('entities', []): save_entity_page(entity, entry)
        
        if i + batch_size < len(to_process):
            print(f"\n      [WAIT] 批次间隔 3秒...")
            import time; time.sleep(3)
    
    print("\n[4/5] 更新处理缓存...")
    for f in to_process:
        cache[str(f.relative_to(RAW_DIR))] = get_file_hash(f)
    save_processed_cache(cache)
    
    print("\n[5/5] 更新索引...")
    update_index(entries)
    
    append_log("INGEST 摄入 (v5整合版)", 
        f"处理 {len(entries)}/{len(to_process)} 个文件，"
        f"概念 {sum(len(e.get('concepts',[])) for e in entries)}，"
        f"实体 {sum(len(e.get('entities',[])) for e in entries)}。"
        f"模式：{'全量' if force else '增量'}")
    
    print(f"\n[DONE] 编译完成! 处理 {len(entries)} 个文件")

# ========== LINT 检查 ==========

def check_orphan_links() -> List[Dict]:
    issues = []
    all_links, existing_pages = set(), set()
    
    for wiki_dir in [WIKI_CONCEPTS, WIKI_SOURCES, WIKI_ENTITIES]:
        if not wiki_dir.exists(): continue
        for md_file in wiki_dir.glob("*.md"):
            existing_pages.add(md_file.stem)
            for link in re.findall(r'\[\[([^\]]+)\]\]', md_file.read_text(encoding='utf-8')):
                all_links.add(link.strip())
    
    for link in all_links:
        if link not in existing_pages:
            issues.append({"type": "orphan_link", "link": link, "severity": "warning",
                          "message": f"链接 [[{link}]] 指向不存在的页面"})
    return issues

def check_empty_pages() -> List[Dict]:
    issues = []
    for wiki_dir in [WIKI_CONCEPTS, WIKI_SOURCES, WIKI_ENTITIES]:
        if not wiki_dir.exists(): continue
        for md_file in wiki_dir.glob("*.md"):
            text = re.sub(r'[#*_\[\]`>\n]', '', md_file.read_text(encoding='utf-8')).strip()
            if len(text) < 100:
                issues.append({"type": "empty_page", "file": str(md_file.relative_to(WIKI_DIR)),
                             "severity": "warning", "message": f"页面过短 ({len(text)} 字符)"})
    return issues

def check_duplicate_titles() -> List[Dict]:
    issues = []
    titles = defaultdict(list)
    
    for wiki_dir in [WIKI_CONCEPTS, WIKI_SOURCES, WIKI_ENTITIES]:
        if not wiki_dir.exists(): continue
        for md_file in wiki_dir.glob("*.md"):
            if m := re.search(r'^#\s+(.+)$', md_file.read_text(encoding='utf-8'), re.MULTILINE):
                titles[m.group(1).strip().lower()].append(str(md_file.relative_to(WIKI_DIR)))
    
    for title, files in titles.items():
        if len(files) > 1:
            issues.append({"type": "duplicate_title", "title": title, "files": files,
                          "severity": "warning", "message": f"标题 '{title}' 重复 {len(files)} 次"})
    return issues

def check_unreviewed_pages() -> List[Dict]:
    issues = []
    for wiki_dir in [WIKI_CONCEPTS, WIKI_SOURCES, WIKI_ENTITIES]:
        if not wiki_dir.exists(): continue
        for md_file in wiki_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            if '⏳' in content or 'pending' in content.lower():
                issues.append({"type": "unreviewed", "file": str(md_file.relative_to(WIKI_DIR)),
                             "severity": "info", "message": f"待验收页面: {md_file.name}"})
    return issues

def run_lint() -> Dict:
    print("=" * 60)
    print("Karpathy 知识库 Lint 检查")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    checks = [
        ("孤儿链接", check_orphan_links),
        ("空页面", check_empty_pages),
        ("重复标题", check_duplicate_titles),
        ("未验收页面", check_unreviewed_pages),
    ]
    
    all_issues = []
    for name, check_func in checks:
        print(f"\n  - {name}...")
        try:
            issues = check_func()
            all_issues.extend(issues)
            print(f"    发现 {len(issues)} 个问题")
        except Exception as e:
            print(f"    [ERROR] {e}")
    
    counts = defaultdict(int)
    for issue in all_issues: counts[issue['severity']] += 1
    
    print(f"\n[结果] 总问题: {len(all_issues)}")
    print(f"  🟡 warning: {counts.get('warning', 0)}")
    print(f"  🔵 info: {counts.get('info', 0)}")
    
    if all_issues:
        print(f"\n[问题详情]")
        for i, issue in enumerate(all_issues[:20], 1):
            print(f"  {i}. [{issue['severity']}] {issue['message']}")
    
    # 保存报告
    report_file = get_cache_dir() / "lint_report.json"
    report_file.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "total_issues": len(all_issues),
        "by_severity": dict(counts),
        "issues": all_issues
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\n[报告已保存] {report_file}")
    
    return {"total": len(all_issues), "issues": all_issues}

# ========== REVIEW 验收 ==========

class ReviewStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

def get_page_status(content: str) -> ReviewStatus:
    if '✅' in content or 'approved' in content.lower(): return ReviewStatus.APPROVED
    elif '❌' in content or 'rejected' in content.lower(): return ReviewStatus.REJECTED
    return ReviewStatus.PENDING

def update_page_status(file_path: Path, new_status: ReviewStatus, note: str = "") -> bool:
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # 替换状态
        icons = {'pending': '⏳', 'approved': '✅', 'rejected': '❌'}
        content = re.sub(r'[⏳✅❌]\s*\w+', f'{icons[new_status.value]} {new_status.value}', content)
        
        if '> 验收状态' in content or '> AI生成' in content:
            content = re.sub(r'(> (?:验收状态|AI生成)[:\s]*).*', 
                           rf'\g<1>{icons[new_status.value]} {new_status.value}', content)
        else:
            content = content.strip() + f"\n> 验收状态：{icons[new_status.value]} {new_status.value}"
        
        if note: content += f"\n> 验收备注：{note}"
        content += f"\n> 验收时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        file_path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def list_pages(status: str = None) -> List[Dict]:
    pages = []
    for wiki_dir in [WIKI_CONCEPTS, WIKI_SOURCES, WIKI_ENTITIES]:
        if not wiki_dir.exists(): continue
        for md_file in wiki_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            page_status = get_page_status(content)
            if status is None or page_status.value == status:
                pages.append({"file": str(md_file.relative_to(WIKI_DIR)), "path": md_file, "status": page_status})
    return sorted(pages, key=lambda x: (x['status'].value, x['file']))

def batch_approve(pattern: str = "*.md") -> int:
    count = 0
    for page in list_pages('pending'):
        if re.match(pattern.replace('*', '.*'), page['file']):
            if update_page_status(page['path'], ReviewStatus.APPROVED):
                count += 1
                print(f"  [OK] ✅ {page['file']}")
    return count

def run_review(args) -> Dict:
    print("=" * 60)
    print("Karpathy 知识库 验收管理")
    print("=" * 60)
    
    if args.list:
        status = args.status
        pages = list_pages(status)
        print(f"\n[页面列表{' (' + status + ')' if status else ''}]")
        icons = {'pending': '⏳', 'approved': '✅', 'rejected': '❌'}
        for page in pages:
            print(f"  {icons[page['status'].value]} {page['file']}")
        print(f"\n共 {len(pages)} 个页面")
        
        # 统计
        all_pages = list_pages()
        stats = {'pending': 0, 'approved': 0, 'rejected': 0}
        for p in all_pages: stats[p['status'].value] += 1
        print(f"\n[统计] ⏳ {stats['pending']} | ✅ {stats['approved']} | ❌ {stats['rejected']} | 总计 {len(all_pages)}")
        
    elif args.approve_all:
        count = batch_approve()
        print(f"\n[DONE] 批量验收 {count} 个页面")
        
    elif args.approve:
        file_path = WIKI_DIR / args.approve
        if file_path.exists():
            if update_page_status(file_path, ReviewStatus.APPROVED, args.note or ""):
                print(f"[OK] ✅ 已验收: {args.approve}")
        else:
            print(f"[ERROR] 文件不存在: {args.approve}")
    
    elif args.generate_report:
        all_pages = list_pages()
        pending = [p for p in all_pages if p['status'].value == 'pending']
        
        report = f"""# 知识库验收报告

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 统计

| 状态 | 数量 | 占比 |
|------|------|------|
| ⏳ 待验收 | {len([p for p in all_pages if p['status'].value == 'pending'])} | {len([p for p in all_pages if p['status'].value == 'pending'])/len(all_pages)*100:.1f}% |
| ✅ 已验收 | {len([p for p in all_pages if p['status'].value == 'approved'])} | {len([p for p in all_pages if p['status'].value == 'approved'])/len(all_pages)*100:.1f}% |
| ❌ 需修改 | {len([p for p in all_pages if p['status'].value == 'rejected'])} | {len([p for p in all_pages if p['status'].value == 'rejected'])/len(all_pages)*100:.1f}% |
| **总计** | **{len(all_pages)}** | 100% |

## 待验收页面

"""
        for page in pending[:50]:
            report += f"- [[{page['file']}]]\n"
        if len(pending) > 50:
            report += f"\n_... 还有 {len(pending) - 50} 个页面_\n"
        
        report += f"\n---\n*由 Karpathy 知识库验收系统自动生成*\n"
        
        report_file = WIKI_DIR / "验收报告.md"
        report_file.write_text(report, encoding='utf-8')
        print(f"\n[报告已保存] {report_file}")
    
    return {}

# ========== OBSIDIAN 导出 ==========

def generate_graph_data() -> Dict:
    nodes, links, seen_nodes, seen_links = [], [], set(), set()
    
    def add_node(name: str, n_type: str):
        if name not in seen_nodes:
            seen_nodes.add(name)
            nodes.append({"id": name, "label": name, "type": n_type})
    
    def add_link(src: str, tgt: str):
        link_id = f"{src}->{tgt}"
        if link_id not in seen_links:
            seen_links.add(link_id)
            links.append({"source": src, "target": tgt})
    
    for wiki_dir, n_type in [(WIKI_CONCEPTS, "concept"), (WIKI_ENTITIES, "entity"), (WIKI_SOURCES, "source")]:
        if not wiki_dir.exists(): continue
        for md_file in wiki_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            add_node(md_file.stem, n_type)
            for link in re.findall(r'\[\[([^\]]+)\]\]', content):
                add_node(link.strip(), "linked")
                add_link(md_file.stem, link.strip())
    
    return {"nodes": nodes, "links": links, "stats": {
        "total_nodes": len(nodes), "total_links": len(links),
        "concepts": len([n for n in nodes if n['type'] == 'concept']),
        "entities": len([n for n in nodes if n['type'] == 'entity']),
    }}

def export_to_obsidian():
    print("=" * 60)
    print("Karpathy Wiki → Obsidian 导出")
    print("=" * 60)
    
    # 备份
    if OUTPUT_DIR.exists() and any(OUTPUT_DIR.iterdir()):
        backup_dir = OUTPUT_DIR.parent / f"Karpathy_Wiki_backup_{datetime.now().strftime('%Y%m%d_%H%M')}"
        print(f"\n[BACKUP] 备份到 {backup_dir}")
        shutil.move(str(OUTPUT_DIR), str(backup_dir))
    
    # 创建目录
    for d in [OUTPUT_DIR, OUTPUT_DIR/"概念", OUTPUT_DIR/"实体", OUTPUT_DIR/"来源"]:
        d.mkdir(parents=True, exist_ok=True)
    
    # 导出
    for wiki_dir, out_dir in [(WIKI_CONCEPTS, OUTPUT_DIR/"概念"), (WIKI_ENTITIES, OUTPUT_DIR/"实体"), (WIKI_SOURCES, OUTPUT_DIR/"来源")]:
        if not wiki_dir.exists(): continue
        for md_file in wiki_dir.glob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            content = re.sub(r'^---\n[\s\S]*?\n---\n', '', content)
            if not content.strip().startswith('#'):
                content = f"# {md_file.stem}\n\n{content}"
            (out_dir / md_file.name).write_text(content, encoding='utf-8')
    
    # Graph数据
    graph_data = generate_graph_data()
    (OUTPUT_DIR / "graph-data.json").write_text(json.dumps(graph_data, ensure_ascii=False, indent=2), encoding='utf-8')
    
    # 索引
    concepts = [f.stem for f in WIKI_CONCEPTS.glob("*.md")] if WIKI_CONCEPTS.exists() else []
    entities = [f.stem for f in WIKI_ENTITIES.glob("*.md")] if WIKI_ENTITIES.exists() else []
    sources = [f.stem for f in WIKI_SOURCES.glob("*.md")] if WIKI_SOURCES.exists() else []
    
    (OUTPUT_DIR / "概念" / "概念索引.md").write_text(
        f"# 概念索引\n\n> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n" +
        "\n".join(f"- [[{c}]]" for c in sorted(concepts)), encoding='utf-8')
    
    (OUTPUT_DIR / "Karpathy_Wiki_索引.md").write_text(
        f"# Karpathy Wiki\n\n> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"## 统计\n- 概念: {len(concepts)}\n- 实体: {len(entities)}\n- 来源: {len(sources)}\n- 节点: {graph_data['stats']['total_nodes']}\n- 链接: {graph_data['stats']['total_links']}\n",
        encoding='utf-8')
    
    print(f"\n[DONE] 导出完成!")
    print(f"[F] 位置: {OUTPUT_DIR}")
    print(f"[=] 概念: {len(concepts)} | 实体: {len(entities)} | 来源: {len(sources)}")
    print(f"[L] 节点: {graph_data['stats']['total_nodes']} | 链接: {graph_data['stats']['total_links']}")

# ========== SKILL 模板生成 ==========

SKILL_TEMPLATE = '''# {name}

> Skill类型：{skill_type}
> 创建时间：{created_at}
> 模式：{pattern}
> 用途：{use_case}

## 触发条件

当用户请求与以下关键词匹配时触发此Skill：
- {keywords}

## 行为控制（核心）

### 阶段1：{stage1_name}
**目标**：{stage1_goal}

**执行步骤**：
1. {step1}
2. {step2}
3. {step3}

**检查清单（Revere模式）**：
- [ ] {check1}
- [ ] {check2}
- [ ] {check3}

### 阶段2：{stage2_name}
**目标**：{stage2_goal}

### 阶段3：{stage3_name}
**目标**：{stage3_goal}

## 输入控制

**允许的输入格式**：
- {input_format}

**禁止的输入格式**：
- {forbidden_input}

## 输出规范

**输出格式**：
- {output_format}

**质量标准**：
- [ ] 符合{standard1}
- [ ] 符合{standard2}

## 异常处理

### 常见错误
| 错误类型 | 解决方案 |
|---------|---------|
| {error1} | {solution1} |
| {error2} | {solution2} |

### 回退策略
当{main_flow}失败时：
1. {fallback1}
2. {fallback2}
3. {fallback3}

## 上下文要求

**必需信息**：
- {required_context}

**可选信息**：
- {optional_context}

## 组合模式

此Skill可与其他Skill组合：
- [[skill-name-1]] - 组合场景：{scenario1}
- [[skill-name-2]] - 组合场景：{scenario2}

## 示例

### 示例1：{example1_title}
**输入**：
```
{example1_input}
```

**输出**：
```
{example1_output}
```

---
*由 Karpathy 知识库系统自动生成*
*基于 Google Agent Skills 五大模式设计*
'''

SKILL_SIMPLE_TEMPLATE = '''# {name}

> Skill类型：{skill_type}
> 创建时间：{created_at}
> 模式：{pattern}

## 触发条件
{keywords}

## 行为流程
{steps}

## 输入输出
**输入**：{input}
**输出**：{output}

## 检查清单
{checklist}

## 示例
{example}

---
*由 Karpathy 知识库系统自动生成*
'''

def generate_skill_template(name, skill_type="通用", pattern="Revere",
                          use_case="", keywords="", steps="",
                          input_format="", output_format="",
                          checklist="", example="", simple=False, output_path=None):
    """生成Skill模板文件"""
    created_at = datetime.now().strftime('%Y-%m-%d')
    
    if simple:
        content = SKILL_SIMPLE_TEMPLATE.format(
            name=name, skill_type=skill_type, created_at=created_at,
            pattern=pattern, keywords=keywords, steps=steps,
            input=input_format, output=output_format,
            checklist=checklist, example=example
        )
    else:
        content = SKILL_TEMPLATE.format(
            name=name, skill_type=skill_type, created_at=created_at,
            pattern=pattern, use_case=use_case, keywords=keywords,
            stage1_name="准备阶段", stage1_goal="",
            step1="", step2="", step3="",
            check1="", check2="", check3="",
            stage2_name="执行阶段", stage2_goal="",
            stage3_name="收尾阶段", stage3_goal="",
            input_format=input_format, forbidden_input="",
            output_format=output_format, standard1="", standard2="",
            error1="", solution1="", error2="", solution2="",
            main_flow="", fallback1="", fallback2="", fallback3="",
            required_context="", optional_context="",
            scenario1="", scenario2="",
            example1_title="", example1_input="", example1_output=""
        )
    
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(content, encoding='utf-8')
        print(f"[OK] Skill模板已生成: {output_path}")
    
    return content

def print_skill_guide():
    """打印Skill写作指南"""
    print("""
================================================================================
Skill 写作规范指南 (基于 Google Agent Skills 五大模式)
================================================================================

[!] 核心观点
--------------------------------------------------------------------------------
1. Skill不是"知识补丁"，而是"行为控制器"
2. Skill从提示工程附件 -> Agent行为工程核心
3. 真正成熟的Skill可能是多个结构的组合

[*] 三种控制模式
--------------------------------------------------------------------------------

[Revere 模式] 检查清单模式
  - 通过Checklist和指令控制模型行为
  - 实现不同审查目标
  - 适用场景：代码审查、文档审核、内容合规检查

[Inversion 模式] 阶段提问模式
  - 强制模型按阶段提问，减少脑补前提问题
  - 适用场景：需求澄清、问题诊断、复杂任务拆解

[Pipeline 模式] 工作流模式
  - 定义工作流，通过关卡控制模型行为
  - 适用场景：多步骤任务、审批流程、数据处理管道

[D] SKILL.md 标准结构
--------------------------------------------------------------------------------

1. 头部元数据（YAML风格）
   - name: 唯一标识符
   - description: 描述（用于意图路由，45%->92%命中率提升）
   - triggers: 触发条件

2. 行为控制（核心）
   - 阶段划分：准备->执行->收尾
   - 检查清单：Revere模式
   - 强制提问：Inversion模式
   - 工作流关卡：Pipeline模式

3. 输入输出规范
   - 允许的输入格式
   - 禁止的输入格式
   - 输出格式和质量标准

4. 异常处理
   - 常见错误和解决方案
   - 回退策略（Fallback）

5. 上下文要求
   - 必需信息
   - 状态维护

6. 组合模式
   - 可与其他Skill组合的场景

[>] 快速生成模板
--------------------------------------------------------------------------------

命令：
  python compile.py --skill "技能名称" [--simple]

示例：
  python compile.py --skill "代码审查" --simple

输出：
  在当前目录生成 skill-name/SKILL.md

================================================================================
""")

# ========== CLI ==========

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Karpathy 知识库编译器 v5 (整合版)')
    parser.add_argument('--force', '-f', action='store_true', help='全量摄入')
    parser.add_argument('--batch', '-b', type=int, default=BATCH_SIZE, help=f'每批数量')
    parser.add_argument('--lint', '-l', action='store_true', help='执行Lint检查')
    parser.add_argument('--review', action='store_true', help='验收管理')
    parser.add_argument('--list', action='store_true', help='列出页面')
    parser.add_argument('--status', choices=['pending', 'approved', 'rejected'], help='按状态筛选')
    parser.add_argument('--approve', type=str, help='验收指定文件')
    parser.add_argument('--approve-all', action='store_true', help='批量验收')
    parser.add_argument('--note', '-n', type=str, default='', help='验收备注')
    parser.add_argument('--generate-report', action='store_true', help='生成验收报告')
    parser.add_argument('--export', '-e', action='store_true', help='导出Obsidian')
    parser.add_argument('--all', '-a', action='store_true', help='执行全部操作')
    parser.add_argument('--model', '-m', type=str, default=LLM_MODEL, help='LLM模型')
    parser.add_argument('--skill', '-s', type=str, help='生成Skill模板')
    parser.add_argument('--simple', action='store_true', help='使用简化模板')
    parser.add_argument('--guide', action='store_true', help='显示Skill写作指南')
    
    args = parser.parse_args()
    globals()['LLM_MODEL'] = args.model
    
    if args.guide:
        print_skill_guide()
    elif args.skill:
        skill_name = args.skill.lower().replace(' ', '-').replace('_', '-')
        output_path = Path(skill_name) / "SKILL.md"
        generate_skill_template(
            name=args.skill,
            simple=args.simple,
            output_path=str(output_path)
        )
    elif args.all:
        run_ingest(force=args.force, batch_size=args.batch)
        print()
        run_lint()
        print()
        export_to_obsidian()
    elif args.lint:
        run_lint()
    elif args.review or args.list or args.approve or args.approve_all or args.generate_report:
        run_review(args)
    elif args.export:
        export_to_obsidian()
    else:
        run_ingest(force=args.force, batch_size=args.batch)

if __name__ == '__main__':
    main()
