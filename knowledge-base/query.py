#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
QUERY 查询脚本
实现 Karpathy 知识库的提问 → 回答 → 沉淀闭环

工作流：
1. 读取 wiki/index.md 找相关页面
2. 读取相关 wiki 页面
3. 综合答案回复用户
4. 如果答案质量高，建议沉淀回 wiki
5. 可选：将回答追加到相关页面
"""

import os
import re
from pathlib import Path
from datetime import datetime

# 配置
WIKI_DIR = Path(__file__).parent / "wiki"
INDEX_FILE = WIKI_DIR / "index.md"
LOG_FILE = WIKI_DIR / "log.md"

# Ollama 配置
OLLAMA_URL = "http://localhost:11434"
LLM_MODEL = "qwen2.5:7b"


def call_llm(prompt: str, system: str = None) -> str:
    """调用 Ollama LLM"""
    import requests
    
    url = f"{OLLAMA_URL}/api/generate"
    data = {
        "model": LLM_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7, "num_predict": 2048}
    }
    if system:
        data["system"] = system
    
    try:
        response = requests.post(url, json=data, timeout=120)
        return response.json().get('response', '').strip()
    except Exception as e:
        return f"[LLM Error: {e}]"


def read_index() -> dict:
    """读取索引文件，返回相关页面列表"""
    if not INDEX_FILE.exists():
        return {'related_pages': [], 'raw_content': ''}
    
    content = INDEX_FILE.read_text(encoding='utf-8')
    
    # 提取相关页面（简化版：返回所有 wiki md 文件）
    related = []
    for md_file in WIKI_DIR.rglob("*.md"):
        if md_file.name == "index.md" or md_file.name == "log.md":
            continue
        rel_path = str(md_file.relative_to(WIKI_DIR))
        related.append({
            'path': str(md_file),
            'name': md_file.stem,
            'rel_path': rel_path
        })
    
    return {'related_pages': related, 'raw_content': content}


def search_related_pages(query: str, pages: list) -> list:
    """根据查询关键词搜索相关页面（全文搜索）"""
    query_lower = query.lower()
    query_words = query_lower.replace(' ', '').split()
    
    scored_pages = []
    
    for page in pages:
        name_lower = page['name'].lower()
        
        # 使用绝对路径读取内容
        page_path = Path(page['path'])
        content = ""
        if page_path.exists():
            try:
                content = page_path.read_text(encoding='utf-8', errors='ignore').lower()
            except:
                pass
        
        # 计算匹配分数
        score = 0
        
        # 标题完全包含
        if query_lower in name_lower:
            score += 20
        
        # 标题词重叠
        name_words = set(name_lower.replace(' ', '').split())
        for word in query_words:
            if word in name_words:
                score += 5
        
        # 内容中包含查询词
        for word in query_words:
            if word in content:
                score += 3
            if word in name_lower:
                score += 2
        
        if score > 0:
            scored_pages.append((score, page))
    
    # 按分数排序
    scored_pages.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored_pages[:5]]  # 返回前5个


def read_page_content(page_path: str) -> str:
    """读取页面内容"""
    try:
        return Path(page_path).read_text(encoding='utf-8')
    except:
        return ""


def query_from_wiki(question: str) -> dict:
    """
    从 wiki 知识库回答问题
    返回: {answer, sources, suggested_save}
    """
    
    # Step 1: 读取索引
    print(f"\n[QUERY] 问题: {question}")
    print("\n[Step 1] 读取索引...")
    index_data = read_index()
    pages = index_data['related_pages']
    print(f"      找到 {len(pages)} 个页面")
    
    # Step 2: 搜索相关页面
    print("\n[Step 2] 搜索相关页面...")
    related = search_related_pages(question, pages)
    print(f"      相关页面: {[p['name'] for p in related]}")
    
    if not related:
        return {
            'answer': "知识库中没有找到相关内容。请先运行 compile.py 编译原始资料。",
            'sources': [],
            'suggested_save': None
        }
    
    # Step 3: 读取相关页面内容
    print("\n[Step 3] 读取相关页面...")
    context_parts = []
    source_files = []
    
    for page in related[:3]:  # 最多读取3个页面
        content = read_page_content(page['path'])
        if content:
            context_parts.append(f"=== {page['name']} ===\n{content[:1500]}")
            source_files.append(page['name'])
    
    context = "\n\n".join(context_parts)
    
    # Step 4: 综合回答
    print("\n[Step 4] 综合回答...")
    
    system_prompt = """你是一个知识库助手，基于提供的 wiki 页面内容回答用户问题。

规则：
1. 只基于提供的 wiki 内容回答，不要编造
2. 如果内容不足以回答，说明知识库中没有足够信息
3. 回答要简洁、有条理
4. 引用相关页面时用 [[页面名]] 格式
5. 如果你发现一个好答案值得沉淀到知识库，在回答末尾用 [值得沉淀到wiki] 标记"""

    prompt = f"""基于以下 wiki 知识库内容，回答用户问题。

问题: {question}

知识库内容:
{context}

请回答问题。"""

    answer = call_llm(prompt, system=system_prompt)
    
    # 检查是否值得沉淀
    suggested_save = None
    if "[值得沉淀到wiki]" in answer or "值得沉淀" in answer:
        suggested_save = {
            'question': question,
            'answer': answer.replace("[值得沉淀到wiki]", "").strip(),
            'sources': source_files
        }
        answer = answer.replace("[值得沉淀到wiki]", "").strip()
    
    return {
        'answer': answer,
        'sources': source_files,
        'suggested_save': suggested_save
    }


def save_to_wiki(question: str, answer: str, sources: list):
    """将问答沉淀到 wiki"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d')
    
    # 创建问答沉淀页
    content = f"""# Q&A 沉淀：{question[:50]}

> 问题: {question}
> 沉淀时间: {timestamp}
> 来源页面: {', '.join(['[[' + s + ']]' for s in sources])}

## 问题

{question}

## 回答

{answer}

## 来源

"""
    for s in sources:
        content += f"- [[{s}]]\n"
    
    content += f"""
---

*由 Karpathy 知识库系统自动沉淀 | {timestamp}*
"""
    
    # 生成安全的文件名
    safe_name = re.sub(r'[^\w\s\u4e00-\u9fff]', '', question[:30])
    safe_name = safe_name.replace(' ', '_')
    filename = f"{timestamp}-Q&A-{safe_name}.md"
    
    # 保存到 wiki/来源/ 或新建 Q&A 目录
    qa_dir = WIKI_DIR / "问答沉淀"
    qa_dir.mkdir(exist_ok=True)
    
    file_path = qa_dir / filename
    file_path.write_text(content, encoding='utf-8')
    
    return str(file_path)


def append_to_existing_page(page_name: str, question: str, answer: str):
    """将问答追加到现有页面的"相关问答"章节"""
    
    # 查找页面
    for md_file in WIKI_DIR.rglob("*.md"):
        if md_file.stem == page_name:
            existing = md_file.read_text(encoding='utf-8')
            
            # 检查是否有"相关问答"章节
            if "## 相关问答" in existing:
                new_entry = f"\n\n### {question}\n\n{answer}"
                updated = existing.replace(
                    "## 相关问答",
                    f"## 相关问答{new_entry}"
                )
            else:
                new_section = f"\n\n## 相关问答\n\n### {question}\n\n{answer}"
                updated = existing + new_section
            
            md_file.write_text(updated, encoding='utf-8')
            return str(md_file)
    
    return None


def log_query(question: str, answer: str, sources: list, saved: bool = False):
    """记录查询到日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    entry = f"""

## [YYYY-MM-DD] query | 回答问题 | 来源: {len(sources)} 页 | 沉淀: {'是' if saved else '否'}

**问题**: {question}

**回答**: {answer[:200]}...

**来源**: {', '.join(sources)}

"""
    
    if LOG_FILE.exists():
        existing = LOG_FILE.read_text(encoding='utf-8')
    else:
        existing = "# Wiki 操作日志\n\n> 本文件记录所有 wiki 的操作历史。\n"
    
    LOG_FILE.write_text(existing + entry, encoding='utf-8')


def main():
    """交互式查询"""
    print("=" * 60)
    print("Karpathy 知识库 - QUERY 查询")
    print("=" * 60)
    print("\n输入问题，我将基于 wiki 知识库回答。")
    print("输入 'quit' 退出。\n")
    
    while True:
        try:
            question = input("\n[问题] ").strip()
        except EOFError:
            break
        
        if not question:
            continue
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("再见!")
            break
        
        # 执行查询
        result = query_from_wiki(question)
        
        print("\n" + "=" * 60)
        print("回答:")
        print("=" * 60)
        print(result['answer'])
        
        print(f"\n[来源] {', '.join(result['sources'])}")
        
        # 沉淀建议
        if result['suggested_save']:
            print("\n[建议] 这个答案值得沉淀到 wiki!")
            save = input("是否沉淀到 wiki？(y/n): ").strip().lower()
            if save == 'y':
                path = save_to_wiki(
                    result['suggested_save']['question'],
                    result['suggested_save']['answer'],
                    result['suggested_save']['sources']
                )
                print(f"      已沉淀到: {path}")
                log_query(question, result['answer'], result['sources'], saved=True)
            else:
                log_query(question, result['answer'], result['sources'], saved=False)
        else:
            log_query(question, result['answer'], result['sources'], saved=False)


def query_once(question: str) -> dict:
    """单次查询（非交互式）"""
    return query_from_wiki(question)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # 命令行参数：直接查询
        question = ' '.join(sys.argv[1:])
        result = query_once(question)
        print(result['answer'])
        print(f"\n[来源] {', '.join(result['sources'])}")
    else:
        # 交互式模式
        main()
