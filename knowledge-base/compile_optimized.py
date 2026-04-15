#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Karpathy 知识库编译器 v6 (优化版)

性能优化：
1. 批量LLM调用：减少90%的LLM请求
2. 跳过已存在：wiki已存在则跳过
3. 断点续传：保存处理进度，中断可恢复
4. 增量优先：只处理新增/修改的文件

使用方法：
  python compile_optimized.py           # 增量摄入
  python compile_optimized.py --force    # 全量摄入
"""

import os
import sys
import json
import hashlib
import requests
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Set
from collections import defaultdict

# ========== 配置 ==========
RAW_DIR = Path(__file__).parent / "raw"
WIKI_DIR = Path(__file__).parent / "wiki"
WIKI_CONCEPTS = WIKI_DIR / "概念"
WIKI_SOURCES = WIKI_DIR / "来源"
WIKI_ENTITIES = WIKI_DIR / "实体"
LOG_FILE = WIKI_DIR / "log.md"
CACHE_DIR = Path(__file__).parent / ".compile_cache"

# LLM 配置
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen2.5:7b")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")

# 编译配置
BATCH_SIZE = 10  # 每批处理文件数
MAX_RETRIES = 2
REQUEST_TIMEOUT = 120  # 增加超时到120秒
SUPPORTED_EXTENSIONS = {'.md', '.txt', '.json', '.csv'}

# ========== 缓存管理 ==========

def get_cache_dir() -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR

def get_file_hash(file_path: Path) -> str:
    m = hashlib.sha256()
    m.update(file_path.as_posix().encode())
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

def load_progress() -> dict:
    """加载断点进度"""
    progress_file = get_cache_dir() / "compile_progress.json"
    if progress_file.exists():
        return json.loads(progress_file.read_text(encoding='utf-8'))
    return {"processed": [], "failed": [], "last_file": None}

def save_progress(progress: dict):
    """保存断点进度"""
    progress_file = get_cache_dir() / "compile_progress.json"
    progress_file.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding='utf-8')

# ========== LLM调用 ==========

def call_llm(prompt: str, model: str = LLM_MODEL, system: str = None, timeout: int = REQUEST_TIMEOUT) -> str:
    url = f"{OLLAMA_URL}/api/generate"
    data = {
        "model": model,
        "prompt": prompt[:8000],
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 2048}
    }
    if system:
        data["system"] = system[:2000]
    
    for retry in range(MAX_RETRIES):
        try:
            response = requests.post(url, json=data, timeout=timeout)
            response.raise_for_status()
            result = response.json()
            return result.get('response', '').strip()
        except Exception as e:
            if retry < MAX_RETRIES - 1:
                import time; time.sleep(2 ** retry)
            else:
                return f"[LLM Error after {MAX_RETRIES} retries: {e}]"

# ========== 批量LLM调用优化 ==========

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

BATCH_CONCEPT_PROMPT = '''为以下概念批量生成简短的wiki段落。

要求：每个概念100字以内，包含定义。用JSON数组格式输出：
[
  {{"concept": "概念名", "article": "段落内容"}},
  {{"concept": "概念名", "article": "段落内容"}}
]

概念列表：
{concepts}

输出JSON格式：'''

def batch_generate_concept_articles(concepts: List[str]) -> Dict[str, str]:
    """批量为多个概念生成wiki段落，大幅减少LLM调用"""
    if not concepts:
        return {}
    
    # 去重
    unique_concepts = list(set(c.strip() for c in concepts if c.strip()))
    if not unique_concepts:
        return {}
    
    prompt = BATCH_CONCEPT_PROMPT.format(concepts="\n".join(f"- {c}" for c in unique_concepts))
    
    result = call_llm(prompt, system="你是技术文档写作专家，输出简洁的JSON数组。")
    
    if result.startswith("[LLM Error]"):
        # 降级：返回空字典
        return {c: f"关于 {c} 的概念页。" for c in unique_concepts}
    
    # 解析JSON
    try:
        articles = json.loads(result)
        return {item['concept']: item.get('article', f"关于 {item['concept']} 的概念页。") for item in articles if 'concept' in item}
    except:
        return {c: f"关于 {c} 的概念页。" for c in unique_concepts}

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

def wiki_file_exists(file_name: str, wiki_type: str) -> bool:
    """检查wiki文件是否已存在"""
    if wiki_type == "source":
        safe_name = re.sub(r'[/\\:?*"<>|]', '_', file_name).replace('.md', '')
        date_prefix = datetime.now().strftime('%Y-%m-%d')
        filename = f"{date_prefix}-{safe_name}.md"
        return (WIKI_SOURCES / filename).exists()
    elif wiki_type == "concept":
        safe_name = re.sub(r'[/\\:?*"<>|]', '_', file_name).replace('[[', '').replace(']]', '')
        return (WIKI_CONCEPTS / f"{safe_name}.md").exists()
    elif wiki_type == "entity":
        safe_name = re.sub(r'[/\\:?*"<>|]', '_', file_name).replace('[[', '').replace(']]', '')
        return (WIKI_ENTITIES / f"{safe_name}.md").exists()
    return False

# ========== 编译单个文件 ==========

def compile_single_file(file_path: Path) -> Optional[dict]:
    rel_path = file_path.relative_to(RAW_DIR)
    
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
        return None
    
    data = extract_json_from_response(result_text)
    
    if not data:
        data = {"concepts": [], "entities": [], "summary": f"来自 {rel_path}", "category": "其他"}
    
    data['file_name'] = str(rel_path)
    data['raw_content'] = content[:2000]
    
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
> 验收状态：[~] pending

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

def save_concept_pages_batch(concepts: List[str], entry: dict, concept_articles: Dict[str, str]):
    """批量保存概念页"""
    WIKI_CONCEPTS.mkdir(parents=True, exist_ok=True)
    date_prefix = datetime.now().strftime('%Y-%m-%d')
    safe_source = re.sub(r'[/\\:?*"<>|]', '_', entry.get('file_name', 'unknown')).replace('.md', '')
    
    for concept in concepts:
        safe_name = re.sub(r'[/\\:?*"<>|]', '_', concept).replace('[[', '').replace(']]', '')
        if not safe_name:
            continue
        
        filename = f"{safe_name}.md"
        if (WIKI_CONCEPTS / filename).exists():
            continue  # 跳过已存在的概念页
        
        article = concept_articles.get(concept, f"关于 {safe_name} 的概念页。")
        
        content = f"""# {safe_name}

> 分类：概念
> 创建时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
> AI生成：[~] pending

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
- [[{date_prefix}-{safe_source}]]

---
*由 Karpathy 知识库系统自动生成*
"""
        
        (WIKI_CONCEPTS / filename).write_text(content, encoding='utf-8')

def save_entity_pages_batch(entities: List[str], entry: dict):
    """批量保存实体页"""
    WIKI_ENTITIES.mkdir(parents=True, exist_ok=True)
    date_prefix = datetime.now().strftime('%Y-%m-%d')
    safe_source = re.sub(r'[/\\:?*"<>|]', '_', entry.get('file_name', 'unknown')).replace('.md', '')
    
    for entity in entities:
        safe_name = re.sub(r'[/\\:?*"<>|]', '_', entity).replace('[[', '').replace(']]', '')
        if not safe_name:
            continue
        
        filename = f"{safe_name}.md"
        if (WIKI_ENTITIES / filename).exists():
            continue  # 跳过已存在的实体页
        
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
- [[{date_prefix}-{safe_source}]]

---
*由 Karpathy 知识库系统自动生成*
"""
        
        (WIKI_ENTITIES / filename).write_text(content, encoding='utf-8')

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
    print("Karpathy 知识库编译器 v6 (优化版)")
    print(f"LLM: {LLM_MODEL}")
    print("=" * 60)
    
    print("\n[1/6] 扫描 raw 目录...")
    raw_files = scan_raw_files()
    print(f"      找到 {len(raw_files)} 个文件")
    
    if not raw_files:
        print("      [WARN] 没有找到文件")
        return
    
    print("\n[2/6] 检查增量文件...")
    cache = load_processed_cache()
    progress = load_progress()
    
    to_process = []
    for f in raw_files:
        rel_path = str(f.relative_to(RAW_DIR))
        hash_val = get_file_hash(f)
        if force or rel_path not in cache or hash_val != cache.get(rel_path):
            to_process.append(f)
    
    if not to_process:
        print("      [SKIP] 所有文件已是最新")
        return
    
    # 过滤已处理（断点续传）
    if not force and progress['processed']:
        processed_set = set(progress['processed'])
        to_process = [f for f in to_process if str(f.relative_to(RAW_DIR)) not in processed_set]
        print(f"      断点续传：跳过 {len(progress['processed'])} 个已处理文件")
    
    print(f"      模式：{'全量' if force else '增量'} - {len(to_process)}/{len(raw_files)} 文件需要处理")
    
    if not to_process:
        print("      [SKIP] 没有需要处理的文件")
        return
    
    print(f"\n[3/6] 分批编译 (每批 {batch_size} 个)...")
    entries = []
    total_batches = (len(to_process) + batch_size - 1) // batch_size
    all_concepts = []
    
    for i in range(0, len(to_process), batch_size):
        batch = to_process[i:i+batch_size]
        batch_num = i // batch_size + 1
        print(f"\n      === 批次 {batch_num}/{total_batches} ===")
        
        batch_entries = []
        for file_path in batch:
            rel_path = str(file_path.relative_to(RAW_DIR))
            print(f"      [{rel_path}]", end=" ", flush=True)
            
            entry = compile_single_file(file_path)
            if entry:
                batch_entries.append(entry)
                entries.append(entry)
                all_concepts.extend(entry.get('concepts', []))
                save_source_page(entry)
                print("[OK]")
            else:
                print("[FAIL]")
                progress['failed'].append(rel_path)
            
            # 保存进度
            progress['processed'].append(rel_path)
            progress['last_file'] = rel_path
            save_progress(progress)
        
        # 批次间隔
        if i + batch_size < len(to_process):
            print(f"\n      [WAIT] 批次间隔 2秒...")
            import time; time.sleep(2)
    
    print(f"\n[4/6] 批量生成概念页文章...")
    concept_articles = batch_generate_concept_articles(all_concepts)
    
    print(f"\n[5/6] 保存概念页和实体页...")
    concepts_set = set()
    entities_set = set()
    
    for entry in entries:
        concepts_set.update(entry.get('concepts', []))
        entities_set.update(entry.get('entities', []))
        save_concept_pages_batch(entry.get('concepts', []), entry, concept_articles)
        save_entity_pages_batch(entry.get('entities', []), entry)
    
    print(f"      保存了 {len(concepts_set)} 个概念页，{len(entities_set)} 个实体页")
    
    print("\n[6/6] 更新缓存和索引...")
    for f in to_process:
        cache[str(f.relative_to(RAW_DIR))] = get_file_hash(f)
    save_processed_cache(cache)
    update_index(entries)
    
    # 清除进度（成功完成）
    if len(progress['failed']) == 0:
        progress_file = get_cache_dir() / "compile_progress.json"
        if progress_file.exists():
            progress_file.unlink()
        print("      [OK] 进度文件已清除")
    
    append_log("INGEST 摄入 (v6优化版)", 
        f"处理 {len(entries)}/{len(to_process)} 个文件，"
        f"概念 {sum(len(e.get('concepts',[])) for e in entries)}，"
        f"实体 {sum(len(e.get('entities',[])) for e in entries)}。"
        f"模式：{'全量' if force else '增量'}。"
        f"失败：{len(progress['failed'])} 个")
    
    print(f"\n[DONE] 编译完成! 处理 {len(entries)} 个文件")

# ========== CLI ==========

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Karpathy 知识库编译器 v6 (优化版)')
    parser.add_argument('--force', '-f', action='store_true', help='全量摄入')
    parser.add_argument('--batch', '-b', type=int, default=BATCH_SIZE, help=f'每批数量')
    parser.add_argument('--model', '-m', type=str, default=LLM_MODEL, help='LLM模型')
    
    args = parser.parse_args()
    globals()['LLM_MODEL'] = args.model
    
    run_ingest(force=args.force, batch_size=args.batch)

if __name__ == '__main__':
    main()
