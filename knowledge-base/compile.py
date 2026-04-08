#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Karpathy 知识库编译脚本
将 raw/ 目录下的原始资料编译成 wiki/ 知识库
"""

import os
import json
import asyncio
from pathlib import Path
from datetime import datetime

# 配置
RAW_DIR = Path(__file__).parent / "raw"
WIKI_DIR = Path(__file__).parent / "wiki"
ALTPUS_DIR = Path(__file__).parent / "altpus"

# 支持的文件扩展名
SUPPORTED_EXTENSIONS = {'.md', '.txt', '.pdf', '.json', '.csv'}


def scan_raw_files():
    """扫描 raw 目录下的所有文件"""
    files = []
    for ext in SUPPORTED_EXTENSIONS:
        files.extend(RAW_DIR.rglob(f"*{ext}"))
    return files


def read_file_content(file_path: Path) -> str:
    """读取文件内容"""
    try:
        if file_path.suffix == '.md':
            return file_path.read_text(encoding='utf-8')
        elif file_path.suffix == '.txt':
            return file_path.read_text(encoding='utf-8')
        elif file_path.suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return json.dumps(data, ensure_ascii=False, indent=2)
        elif file_path.suffix == '.csv':
            return file_path.read_text(encoding='utf-8')
        else:
            return f"[Binary file: {file_path.name}]"
    except Exception as e:
        return f"[Error reading {file_path.name}: {str(e)}]"


async def compile_with_llm(raw_content: str, file_name: str) -> dict:
    """
    使用 LLM 编译原始内容为 wiki 格式
    返回: {concepts: [], wiki_content: str, links: []}
    """
    # 这里需要接入 LLM API
    # 暂时使用本地模拟，后续接入 Ollama/GPT
    
    prompt = f"""你是一个知识整理专家。请分析以下文件并提取核心概念。

文件名: {file_name}

内容:
{raw_content[:3000]}

请以 JSON 格式输出：
{{
    "concepts": ["概念1", "概念2", "概念3"],
    "summary": "50字以内的摘要",
    "links": ["相关概念1", "相关概念2"],
    "category": "所属分类（AI/编程/工具/其他）"
}}

只输出 JSON，不要有其他内容。"""

    # TODO: 接入实际 LLM API
    # 目前返回模拟数据
    return {
        "concepts": [],
        "summary": f"来自 {file_name} 的内容",
        "links": [],
        "category": "其他",
        "raw_content": raw_content[:500]
    }


def generate_wiki_index(entries: list) -> str:
    """生成 wiki 索引页面"""
    index_content = f"""# 知识库索引

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 统计

- 总文件数: {len(entries)}
- 总概念数: {sum(len(e.get('concepts', [])) for e in entries)}

## 分类

"""

    categories = {}
    for entry in entries:
        cat = entry.get('category', '其他')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(entry)

    for cat, items in categories.items():
        index_content += f"### {cat} ({len(items)})\n\n"
        for item in items:
            concepts = item.get('concepts', [])
            if concepts:
                index_content += f"- [[{concepts[0]}]] - {item.get('summary', '')[:50]}\n"
            else:
                index_content += f"- {item.get('file_name', 'unknown')}\n"
        index_content += "\n"

    return index_content


def save_wiki_entry(entry: dict, wiki_dir: Path):
    """保存单个 wiki 条目"""
    concepts = entry.get('concepts', [])
    if not concepts:
        # 如果没有概念，用文件名
        file_name = entry.get('file_name', 'unknown').replace('/', '_').replace('\\', '_')
        safe_name = Path(file_name).stem
    else:
        main_concept = concepts[0]
        safe_name = main_concept.replace('/', '_').replace('\\', '_')
    
    # 创建概念目录
    concept_dir = wiki_dir / "concepts"
    concept_dir.mkdir(exist_ok=True)
    
    # 写入概念文章
    content = f"""# {safe_name}

> 来源: {entry.get('file_name', 'unknown')}
> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 摘要

{entry.get('summary', '')}

## 相关概念

"""
    for link in entry.get('links', []):
        content += f"- [[{link}]]\n"
    
    if entry.get('raw_content'):
        content += f"""
## 原始内容

```
{entry.get('raw_content', '')[:500]}...
```

"""

    content += f"""
---

*由 Karpathy 知识库系统自动生成*
"""
    
    file_path = concept_dir / f"{safe_name}.md"
    file_path.write_text(content, encoding='utf-8')
    print(f"  [OK] 创建: {file_path.name}")


async def main():
    """主函数"""
    print("[START] Karpathy 知识库编译器")
    print("=" * 50)
    
    # 1. 扫描 raw 文件
    print("\n[SCAN] 扫描 raw 目录...")
    raw_files = scan_raw_files()
    print(f"   找到 {len(raw_files)} 个文件")
    
    if not raw_files:
        print("   WARNING: 没有找到文件，请在 raw/ 目录添加内容")
        return
    
    # 2. 读取并编译每个文件
    print("\n[COMPILE] 编译中...")
    entries = []
    
    for file_path in raw_files:
        print(f"\n   处理: {file_path.relative_to(RAW_DIR)}")
        content = read_file_content(file_path)
        
        entry = await compile_with_llm(content, file_path.name)
        entry['file_name'] = str(file_path.relative_to(RAW_DIR))
        entries.append(entry)
        
        # 保存到 wiki
        save_wiki_entry(entry, WIKI_DIR)
    
    # 3. 生成索引
    print("\n[INDEX] 生成索引...")
    index_content = generate_wiki_index(entries)
    (WIKI_DIR / "index.md").write_text(index_content, encoding='utf-8')
    print(f"   [OK] 索引已生成: {WIKI_DIR / 'index.md'}")
    
    print("\n[DONE] 编译完成!")
    print(f"   知识库位置: {WIKI_DIR}")
    print(f"   条目数量: {len(entries)}")


if __name__ == '__main__':
    asyncio.run(main())
