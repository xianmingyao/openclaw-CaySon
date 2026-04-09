#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Karpathy 知识库编译脚本 v3
适配新的目录结构：
- wiki/概念/ - 原理/方法论/术语
- wiki/来源/ - 每篇原始资料的提炼
- wiki/实体/ - 人/公司/产品/工具
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime
import re

# 配置
RAW_DIR = Path(__file__).parent / "raw"
WIKI_DIR = Path(__file__).parent / "wiki"
WIKI_CONCEPTS = WIKI_DIR / "概念"
WIKI_SOURCES = WIKI_DIR / "来源"
WIKI_ENTITIES = WIKI_DIR / "实体"
LOG_FILE = WIKI_DIR / "log.md"

# Ollama 配置
OLLAMA_URL = "http://localhost:11434"
LLM_MODEL = "qwen2.5:7b"
EMBED_MODEL = "nomic-embed-text"

SUPPORTED_EXTENSIONS = {'.md', '.txt', '.pdf', '.json', '.csv'}


def scan_raw_files():
    """扫描 raw 目录下的所有文件"""
    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(RAW_DIR.rglob(f"*{ext}"))
    return sorted(files)


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


def call_llm(prompt: str, model: str = LLM_MODEL, system: str = None) -> str:
    """调用 Ollama LLM"""
    import requests
    
    url = f"{OLLAMA_URL}/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 2048}
    }
    if system:
        data["system"] = system
    
    try:
        response = requests.post(url, json=data, timeout=120)
        return response.json().get('response', '').strip()
    except Exception as e:
        return f"[LLM Error: {e}]"


def classify_entity(concept: str) -> str:
    """判断是实体还是概念"""
    # 实体关键词
    entity_keywords = ['公司', '产品', '工具', '平台', '人名', 'AI', 'LLM', 'Model', 'Agent', 'SDK']
    
    for kw in entity_keywords:
        if kw in concept:
            return '实体'
    
    # 概念关键词
    concept_keywords = ['原理', '方法', '论', '技术', '系统', '架构', '设计', '模式', 'Workflow', 'Engineering']
    for kw in concept_keywords:
        if kw in concept:
            return '概念'
    
    return '概念'  # 默认是概念


def compile_with_llm(raw_content: str, file_name: str) -> dict:
    """使用 LLM 编译原始内容"""
    
    system_prompt = """你是一个知识整理专家。输出 JSON：
{
    "concepts": ["概念1", "概念2"],
    "entities": ["实体1", "实体2"],
    "summary": "50字摘要",
    "category": "AI/编程/工具/科研/其他"
}"""

    prompt = f"""分析以下文件，提取概念和实体。

文件: {file_name}

内容:
{raw_content[:4000]}

输出 JSON。"""

    try:
        result = call_llm(prompt, system=system_prompt)
        import re
        m = re.search(r'\{[\s\S]*\}', result)
        if m:
            data = json.loads(m.group())
            return {
                "concepts": data.get("concepts", []),
                "entities": data.get("entities", []),
                "summary": data.get("summary", f"来自 {file_name}"),
                "category": data.get("category", "其他"),
                "raw_content": raw_content[:1000]
            }
    except:
        pass
    
    return {
        "concepts": [],
        "entities": [],
        "summary": f"来自 {file_name}",
        "category": "其他",
        "raw_content": raw_content[:500]
    }


def save_source_page(entry: dict, file_name: str):
    """保存来源摘要页"""
    date_prefix = datetime.now().strftime('%Y-%m-%d')
    safe_name = file_name.replace('/', '_').replace('\\', '_').replace('.md', '')
    filename = f"{date_prefix}-{safe_name}.md"
    
    content = f"""# 来源摘要：{file_name}

> 原始路径：raw/{file_name}
> 摄入时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 核心观点

{entry.get('summary', '')}

## 关键细节

{entry.get('raw_content', '')[:500]}

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
    print(f"      [来源] {path.name}")


def save_concept_page(concept: str, entry: dict):
    """保存概念页"""
    safe_name = concept.replace('/', '_').replace('\\', '_').replace('[[', '').replace(']]', '')
    if not safe_name:
        return
    
    article = call_llm(f"""为概念「{safe_name}」生成简短的 wiki 段落，100-200字，包含定义和关键要点。""",
        system="你是技术文档写作专家，输出简洁的段落文字。")
    
    content = f"""# {safe_name}

> 分类：概念
> 创建时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

{article if article else f"关于 {safe_name} 的概念页。"}

## 相关概念
"""
    for c in entry.get('concepts', []):
        if c != concept:
            content += f"- [[{c}]]\n"
    
    for e in entry.get('entities', []):
        content += f"- [[{e}]]\n"
    
    if not entry.get('concepts') and not entry.get('entities'):
        content += "- 暂无相关概念\n"
    
    content += f"""
## 来源
- [[{datetime.now().strftime('%Y-%m-%d')}-{entry.get('file_name', 'unknown')}]]

---
*由 Karpathy 知识库系统自动生成*
"""
    
    WIKI_CONCEPTS.mkdir(parents=True, exist_ok=True)
    path = WIKI_CONCEPTS / f"{safe_name}.md"
    path.write_text(content, encoding='utf-8')
    print(f"      [概念] {path.name}")


def save_entity_page(entity: str, entry: dict):
    """保存实体页"""
    safe_name = entity.replace('/', '_').replace('\\', '_').replace('[[', '').replace(']]', '')
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
    print(f"      [实体] {path.name}")


def update_index(pages: list):
    """更新索引页"""
    content = f"""# 知识库索引

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

## 统计

- 总文件数：{len(pages)}
- 总概念数：{sum(len(p.get('concepts', [])) for p in pages)}
- 总实体数：{sum(len(p.get('entities', [])) for p in pages)}

## 来源列表

"""
    for p in pages:
        content += f"- [[{datetime.now().strftime('%Y-%m-%d')}-{p.get('file_name', 'unknown')}]]\n"
    
    content += "\n## 概念\n\n"
    concept_files = list(WIKI_CONCEPTS.glob("*.md"))
    for f in concept_files:
        content += f"- [[{f.stem}]]\n"
    
    content += "\n## 实体\n\n"
    entity_files = list(WIKI_ENTITIES.glob("*.md"))
    if entity_files:
        for f in entity_files:
            content += f"- [[{f.stem}]]\n"
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


async def main():
    print("=" * 50)
    print("Karpathy 知识库编译器 v3")
    print(f"LLM: {LLM_MODEL}")
    print("=" * 50)
    
    # 扫描
    print("\n[1/4] 扫描 raw 目录...")
    raw_files = scan_raw_files()
    print(f"      找到 {len(raw_files)} 个文件")
    
    if not raw_files:
        print("      [WARN] 没有找到文件")
        return
    
    # 编译
    print(f"\n[2/4] 编译 {len(raw_files)} 个文件...")
    entries = []
    
    for file_path in raw_files:
        rel_path = file_path.relative_to(RAW_DIR)
        print(f"\n      [{raw_files.index(file_path)+1}/{len(raw_files)}] {rel_path}")
        
        content = read_file_content(file_path)
        entry = compile_with_llm(content, str(rel_path))
        entry['file_name'] = str(rel_path)
        entries.append(entry)
        
        # 保存来源页
        save_source_page(entry, str(rel_path))
        
        # 保存概念页
        for concept in entry.get('concepts', []):
            save_concept_page(concept, entry)
        
        # 保存实体页
        for entity in entry.get('entities', []):
            save_entity_page(entity, entry)
        
        print(f"      概念: {entry.get('concepts', []) or ['(无)']}")
        print(f"      实体: {entry.get('entities', []) or ['(无)']}")
    
    # 更新索引
    print(f"\n[3/4] 更新索引...")
    update_index(entries)
    
    # 记录日志
    print(f"\n[4/4] 记录日志...")
    append_log("INGEST 摄入", f"处理 {len(raw_files)} 个文件，提取 {sum(len(e.get('concepts',[])) for e in entries)} 个概念，{sum(len(e.get('entities',[])) for e in entries)} 个实体。")
    
    print(f"\n[DONE] 编译完成!")
    print(f"      来源: {len(raw_files)}")
    print(f"      概念: {sum(len(e.get('concepts',[])) for e in entries)}")
    print(f"      实体: {sum(len(e.get('entities',[])) for e in entries)}")
    print(f"\n运行 lint.py 检查知识库健康状况")


if __name__ == '__main__':
    asyncio.run(main())
