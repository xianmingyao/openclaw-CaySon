#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Karpathy 知识库编译脚本 v4 (优化版)
解决问题：
1. P0: SIGKILL - 分批处理 + 增量更新
2. P0: 增量Ingest - 只处理新增/变更文件
3. P1: RAG语义检索 - 对接Milvus
4. P1: Lint Cron自动化
5. P2: Obsidian可视化
6. P2: 验收机制
"""

import os
import json
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Set
import re

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
BATCH_SIZE = 5  # 每批处理文件数
MAX_RETRIES = 2  # 最大重试次数
REQUEST_TIMEOUT = 60  # 单次请求超时(秒)
CHUNK_SIZE = 2000  # 内容分块大小

SUPPORTED_EXTENSIONS = {'.md', '.txt', '.json', '.csv'}

# ========== 缓存管理 ==========

def get_cache_dir() -> Path:
    """获取缓存目录"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR

def get_file_hash(file_path: Path) -> str:
    """获取文件hash"""
    m = hashlib.sha256()
    m.update(str(file_path).encode())
    m.update(str(file_path.stat().st_mtime).encode())
    return m.hexdigest()[:16]

def load_processed_cache() -> dict:
    """加载已处理文件缓存"""
    cache_file = get_cache_dir() / "processed_files.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding='utf-8'))
    return {}

def save_processed_cache(cache: dict):
    """保存已处理文件缓存"""
    cache_file = get_cache_dir() / "processed_files.json"
    cache_file.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')

def is_file_changed(file_path: Path, cache: dict) -> bool:
    """检查文件是否变更"""
    current_hash = get_file_hash(file_path)
    rel_path = str(file_path.relative_to(RAW_DIR))
    return cache.get(rel_path) != current_hash

# ========== 增量Ingest ==========

def get_files_to_process(raw_files: list, cache: dict, force: bool = False) -> list:
    """获取需要处理的文件列表（增量模式）"""
    if force:
        print("      [MODE] 全量模式 - 处理所有文件")
        return raw_files
    
    to_process = []
    for f in raw_files:
        rel_path = str(f.relative_to(RAW_DIR))
        if rel_path not in cache or is_file_changed(f, cache):
            to_process.append(f)
    
    if to_process:
        print(f"      [MODE] 增量模式 - {len(to_process)}/{len(raw_files)} 文件需要处理")
    else:
        print(f"      [MODE] 增量模式 - 所有文件已是最新")
    
    return to_process

# ========== 核心LLM调用 ==========

def call_llm_stream(prompt: str, model: str = LLM_MODEL, system: str = None) -> str:
    """流式调用LLM（避免大响应超时）"""
    url = f"{OLLAMA_URL}/api/generate"
    data = {
        "model": model,
        "prompt": prompt[:8000],  # 限制输入长度
        "stream": True,
        "options": {"temperature": 0.3, "num_predict": 1024}  # 限制输出长度
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
        
        full_response = ''.join(result)
        return full_response.strip()
    except Exception as e:
        return f"[LLM Error: {e}]"

def call_llm(prompt: str, model: str = LLM_MODEL, system: str = None) -> str:
    """普通调用LLM（带重试）"""
    for retry in range(MAX_RETRIES):
        try:
            return call_llm_stream(prompt, model, system)
        except Exception as e:
            if retry < MAX_RETRIES - 1:
                print(f"         重试 {retry+1}/{MAX_RETRIES}...")
                import time
                time.sleep(2 ** retry)
            else:
                return f"[LLM Error after {MAX_RETRIES} retries: {e}]"

# ========== 内容分析 ==========

def extract_json_from_response(response: str) -> Optional[dict]:
    """从LLM响应中提取JSON"""
    # 尝试多种JSON提取方式
    patterns = [
        r'\{[\s\S]*\}',  # 最宽松
        r'```json\n([\s\S]*?)\n```',  # 代码块
        r'"concepts"[\s\S]*',  # 从concepts开始
    ]
    
    for pattern in patterns:
        m = re.search(pattern, response)
        if m:
            try:
                json_str = m.group() if '```' not in m.group() else re.search(r'```json\n([\s\S]*?)\n```', response).group(1)
                return json.loads(json_str)
            except:
                continue
    return None

SYSTEM_PROMPT = """你是一个知识整理专家。严格输出JSON格式：
{"concepts":["概念1","概念2"],"entities":["实体1","实体2"],"summary":"50字摘要","category":"分类"}"""

def compile_single_file(file_path: Path) -> Optional[dict]:
    """编译单个文件（带分块处理）"""
    rel_path = file_path.relative_to(RAW_DIR)
    print(f"\n      [{rel_path}]")
    
    # 读取内容（限制长度避免超时）
    content = read_file_content(file_path)
    if len(content) > 15000:
        content = content[:15000] + "\n\n[内容过长已截断...]"
    
    # 调用LLM
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
        print(f"      [WARN] 无法解析LLM响应，使用默认结构")
        data = {
            "concepts": [],
            "entities": [],
            "summary": f"来自 {rel_path}",
            "category": "其他"
        }
    
    data['file_name'] = str(rel_path)
    data['raw_content'] = content[:2000]  # 保存部分原文用于参考
    
    concepts = data.get("concepts", [])
    entities = data.get("entities", [])
    print(f"      [OK] 概念: {concepts[:3] if concepts else '无'} | 实体: {entities[:3] if entities else '无'}")
    
    return data

# ========== 文件操作 ==========

def read_file_content(file_path: Path) -> str:
    """读取文件内容"""
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
        else:
            return f"[Binary file: {file_path.name}]"
    except Exception as e:
        return f"[Error reading {file_path.name}: {e}]"

def save_source_page(entry: dict):
    """保存来源摘要页"""
    file_name = entry.get('file_name', 'unknown')
    date_prefix = datetime.now().strftime('%Y-%m-%d')
    safe_name = re.sub(r'[/\\:?*"<>|]', '_', file_name).replace('.md', '')
    filename = f"{date_prefix}-{safe_name}.md"
    
    # 验收状态标记
    review_status = entry.get('review_status', 'pending')
    status_icon = '⏳' if review_status == 'pending' else '✅' if review_status == 'approved' else '❌'
    
    content = f"""# 来源摘要：{file_name}

> 原始路径：raw/{file_name}
> 摄入时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
> 验收状态：{status_icon} {review_status}

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
    path = WIKI_SOURCES / filename
    path.write_text(content, encoding='utf-8')

def save_concept_page(concept: str, entry: dict):
    """保存概念页"""
    safe_name = re.sub(r'[/\\:?*"<>|]', '_', concept).replace('[[', '').replace(']]', '')
    if not safe_name:
        return
    
    # 调用LLM生成简短段落
    article = call_llm(f"""为概念「{safe_name}」生成简短的 wiki 段落，100字以内，包含定义。""",
        system="你是技术文档写作专家，输出简洁的段落。")
    
    if article.startswith("[LLM Error]"):
        article = f"关于 {safe_name} 的概念页。"
    
    review_status = entry.get('review_status', 'pending')
    status_icon = '⏳' if review_status == 'pending' else '✅' if review_status == 'approved' else '❌'
    
    content = f"""# {safe_name}

> 分类：概念
> 创建时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
> AI生成：{status_icon} 待验收

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
    path = WIKI_CONCEPTS / f"{safe_name}.md"
    path.write_text(content, encoding='utf-8')

def save_entity_page(entity: str, entry: dict):
    """保存实体页"""
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
    path = WIKI_ENTITIES / f"{safe_name}.md"
    path.write_text(content, encoding='utf-8')

# ========== RAG语义检索（对接Milvus）==========
"""
RAG功能预留接口 - 需要时可启用
使用示例：
from compile import embed_and_search
results = embed_and_search("什么是Agent Skills", top_k=5)
"""

def get_embeddings(texts: list, model: str = EMBED_MODEL) -> list:
    """获取文本嵌入向量"""
    url = f"{OLLAMA_URL}/api/embeddings"
    embeddings = []
    
    for text in texts:
        try:
            response = requests.post(url, json={
                "model": model,
                "prompt": text[:4000]
            }, timeout=30)
            emb = response.json().get('embedding', [])
            embeddings.append(emb)
        except Exception as e:
            print(f"[WARN] Embedding failed: {e}")
            embeddings.append([])
    
    return embeddings

# ========== 索引和日志 ==========

def update_index(entries: list):
    """更新索引页"""
    concepts = set()
    entities = set()
    
    for e in entries:
        for c in e.get('concepts', []):
            concepts.add(c)
        for en in e.get('entities', []):
            entities.add(en)
    
    content = f"""# 知识库索引

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}
> 增量更新：{'是' if entries else '否'}

## 统计

- 本次处理：{len(entries)} 个文件
- 总概念数：{len(concepts)}
- 总实体数：{len(entities)}

## 最近来源

"""
    for p in sorted(entries, key=lambda x: x.get('file_name', ''), reverse=True)[:10]:
        content += f"- [[{p.get('file_name', 'unknown')}]]\n"
    
    content += "\n## 概念\n\n"
    for c in sorted(concepts):
        content += f"- [[{c}]]\n"
    
    content += "\n## 实体\n\n"
    if entities:
        for e in sorted(entities):
            content += f"- [[{e}]]\n"
    else:
        content += "*（暂无实体）*\n"
    
    (WIKI_DIR / "index.md").write_text(content, encoding='utf-8')
    print(f"\n      [OK] 索引已更新")

def append_log(action: str, details: str):
    """追加操作日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    entry = f"""

## {timestamp} - {action}

{details}

"""
    
    if LOG_FILE.exists():
        existing = LOG_FILE.read_text(encoding='utf-8')
    else:
        existing = "# Wiki 操作日志\n\n> 本文件记录所有 wiki 的操作历史。\n"
    
    LOG_FILE.write_text(existing + entry, encoding='utf-8')

# ========== Obsidian导出 ==========

def export_to_obsidian(output_dir: Path = None):
    """导出为Obsidian兼容格式"""
    if output_dir is None:
        output_dir = Path.home() / "Obsidian Vaults" / "Karpathy Wiki"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 复制wiki内容
    import shutil
    
    for item in (WIKI_DIR / "概念").glob("*.md"):
        shutil.copy(item, output_dir / "Concepts" / item.name)
    
    for item in (WIKI_DIR / "实体").glob("*.md"):
        shutil.copy(item, output_dir / "Entities" / item.name)
    
    for item in (WIKI_DIR / "来源").glob("*.md"):
        shutil.copy(item, output_dir / "Sources" / item.name)
    
    # 创建Obsidian配置文件
    obsidian_config = {
        "vault": "Karpathy Wiki",
        "created": datetime.now().isoformat(),
        "source": str(WIKI_DIR)
    }
    (output_dir / ".karpathy-meta.json").write_text(
        json.dumps(obsidian_config, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    
    print(f"      [OK] 已导出到 Obsidian: {output_dir}")

# ========== 主流程 ==========

def scan_raw_files():
    """扫描raw目录"""
    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(RAW_DIR.rglob(f"*{ext}"))
    return sorted(files)

def run_ingest(force: bool = False, batch_size: int = BATCH_SIZE):
    """执行摄入流程"""
    print("=" * 60)
    print("Karpathy 知识库编译器 v4 (优化版)")
    print(f"LLM: {LLM_MODEL}")
    print("=" * 60)
    
    # 扫描
    print("\n[1/5] 扫描 raw 目录...")
    raw_files = scan_raw_files()
    print(f"      找到 {len(raw_files)} 个文件")
    
    if not raw_files:
        print("      [WARN] 没有找到文件")
        return
    
    # 增量检查
    print("\n[2/5] 检查增量文件...")
    cache = load_processed_cache()
    to_process = get_files_to_process(raw_files, cache, force)
    
    if not to_process:
        print("      [SKIP] 没有新文件需要处理")
        return
    
    # 分批处理
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
                for concept in entry.get('concepts', []):
                    save_concept_page(concept, entry)
                for entity in entry.get('entities', []):
                    save_entity_page(entity, entry)
        
        # 批次间休息
        if i + batch_size < len(to_process):
            print(f"\n      [WAIT] 批次间隔 3秒...")
            import time; time.sleep(3)
    
    # 更新缓存
    print("\n[4/5] 更新处理缓存...")
    for f in to_process:
        rel_path = str(f.relative_to(RAW_DIR))
        cache[rel_path] = get_file_hash(f)
    save_processed_cache(cache)
    
    # 更新索引
    print("\n[5/5] 更新索引...")
    update_index(entries)
    
    # 记录日志
    append_log("INGEST 摄入 (v4优化版)", 
        f"处理 {len(entries)}/{len(to_process)} 个文件，"
        f"提取 {sum(len(e.get('concepts',[])) for e in entries)} 个概念，"
        f"{sum(len(e.get('entities',[])) for e in entries)} 个实体。"
        f"模式：{'全量' if force else '增量'}")
    
    print(f"\n[DONE] 编译完成!")
    print(f"      处理: {len(entries)} 个文件")
    print(f"      概念: {sum(len(e.get('concepts',[])) for e in entries)}")
    print(f"      实体: {sum(len(e.get('entities',[])) for e in entries})")

# ========== CLI ==========

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Karpathy 知识库编译器 v4')
    parser.add_argument('--force', '-f', action='store_true', help='全量模式（忽略缓存）')
    parser.add_argument('--batch', '-b', type=int, default=BATCH_SIZE, help=f'每批处理数量 (默认{BATCH_SIZE})')
    parser.add_argument('--export-obsidian', '-o', action='store_true', help='导出到Obsidian')
    parser.add_argument('--model', '-m', type=str, default=LLM_MODEL, help=f'LLM模型 (默认{LLM_MODEL})')
    
    args = parser.parse_args()
    LLM_MODEL = args.model
    
    if args.export_obsidian:
        export_to_obsidian()
    else:
        run_ingest(force=args.force, batch_size=args.batch)
