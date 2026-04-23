#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

"""
QUERY 查询脚本 v2 - 统一检索入口
同时查询三个知识系统：
1. Wiki知识库 (local) - knowledge-base/wiki/
2. MAGMA记忆 (Mem0 + Milvus) - scripts/magma_memory/
3. Skills知识库 (local) - knowledge/

使用说明：
    python query.py "检索内容"           # 单次查询
    python query.py --all "检索内容"     # 全系统检索
    python query.py --wiki "检索内容"    # 仅wiki
    python query.py --memory "检索内容"  # 仅记忆
    python query.py --skills "检索内容"  # 仅skills
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# ============== 配置 ==============
WIKI_DIR = Path(__file__).parent / "wiki"
INDEX_FILE = WIKI_DIR / "index.md"
LOG_FILE = WIKI_DIR / "log.md"
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"  # E:\workspace\knowledge
MAGMA_SCRIPT = Path(__file__).parent.parent / "scripts" / "magma_memory" / "cli.py"

# Ollama 配置
OLLAMA_URL = "http://localhost:11434"
LLM_MODEL = "qwen2.5:7b"


# ============== Wiki 检索 ==============

def search_wiki(query: str, max_results: int = 5) -> List[Dict]:
    """从 Wiki 知识库检索"""
    results = []
    query_lower = query.lower()
    query_words = query_lower.replace(' ', '').split()
    
    for md_file in WIKI_DIR.rglob("*.md"):
        if md_file.name in ["index.md", "log.md"]:
            continue
        
        name_lower = md_file.stem.lower()
        content = ""
        try:
            content = md_file.read_text(encoding='utf-8', errors='ignore').lower()
        except:
            pass
        
        # 计算匹配分数
        score = 0
        if query_lower in name_lower:
            score += 20
        name_words = set(name_lower.replace(' ', '').split())
        for word in query_words:
            if word in name_words:
                score += 5
            if word in content:
                score += 2
        
        if score > 0:
            results.append({
                'source': 'wiki',
                'path': str(md_file),
                'name': md_file.stem,
                'score': score,
                'preview': content[:200] if content else ""
            })
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:max_results]


def get_wiki_content(path: str) -> str:
    """读取 Wiki 页面内容"""
    try:
        return Path(path).read_text(encoding='utf-8')
    except:
        return ""


# ============== Skills 知识库检索 ==============

def search_skills(query: str, max_results: int = 5) -> List[Dict]:
    """从 Skills 知识库检索"""
    results = []
    query_lower = query.lower()
    query_words = query_lower.replace(' ', '').split()
    
    if not KNOWLEDGE_DIR.exists():
        return results
    
    for md_file in KNOWLEDGE_DIR.rglob("*.md"):
        name_lower = md_file.stem.lower()
        content = ""
        try:
            content = md_file.read_text(encoding='utf-8', errors='ignore').lower()
        except:
            pass
        
        score = 0
        if query_lower in name_lower:
            score += 20
        name_words = set(name_lower.replace(' ', '').split())
        for word in query_words:
            if word in name_words:
                score += 5
            if word in content:
                score += 2
        
        if score > 0:
            rel_path = str(md_file.relative_to(KNOWLEDGE_DIR))
            results.append({
                'source': 'skills',
                'path': str(md_file),
                'name': md_file.stem,
                'rel_path': rel_path,
                'score': score,
                'preview': content[:200] if content else ""
            })
    
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:max_results]


def get_skills_content(path: str) -> str:
    """读取 Skills 文档内容"""
    try:
        return Path(path).read_text(encoding='utf-8')
    except:
        return ""


# ============== MAGMA 记忆检索 ==============

def search_magma(query: str, max_results: int = 5) -> List[Dict]:
    """从 MAGMA 记忆系统检索（Mem0 + Milvus）"""
    results = []
    
    # 优先使用 Mem0 本地检索
    try:
        import mem0
        config = {"vector_store": {"provider": "chroma", "config": {"collection_name": "cay son_db", "path": str(Path.home() / ".mem0" / "chroma")}}}
        client = mem0.Client(config)
        memories = client.search(query, limit=max_results)
        
        for mem in memories:
            results.append({
                'source': 'magma',
                'id': mem.get('id', ''),
                'text': mem.get('text', '')[:200],
                'score': mem.get('score', 0),
                'created_at': mem.get('created_at', '')
            })
    except Exception as e:
        # Mem0 失败，尝试 Milvus 直连
        try:
            results = search_milvus_fallback(query, max_results)
        except:
            pass
    
    return results


def search_milvus_fallback(query: str, max_results: int = 5) -> List[Dict]:
    """Milvus 直连降级方案"""
    results = []
    
    try:
        from pymilvus import MilvusClient
        client = MilvusClient(uri="http://8.137.122.11:19530", token="MRFzL6@Milvus")
        results = client.search(
            collection_name="CaySon_db",
            query_text=query,
            limit=max_results
        )
        
        formatted = []
        for r in results:
            formatted.append({
                'source': 'milvus',
                'id': r.get('id', ''),
                'text': r.get('text', r.get('entity', {}).get('text', ''))[:200],
                'score': r.get('score', 0)
            })
        return formatted
    except Exception as e:
        return results


# ============== LLM 综合回答 ==============

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


def synthesize_answer(query: str, wiki_results: List, skills_results: List, magma_results: List) -> str:
    """综合三个来源生成回答"""
    
    # 构建上下文
    context_parts = []
    sources = []
    
    # Wiki 来源
    if wiki_results:
        context_parts.append("=== [Wiki知识库] ===")
        for r in wiki_results[:2]:
            content = get_wiki_content(r['path'])
            context_parts.append(f"\n【{r['name']}】\n{content[:800]}")
            sources.append(f"wiki:{r['name']}")
    
    # Skills 来源
    if skills_results:
        context_parts.append("\n=== [Skills知识库] ===")
        for r in skills_results[:2]:
            content = get_skills_content(r['path'])
            context_parts.append(f"\n【{r['name']}】\n{content[:800]}")
            sources.append(f"skills:{r['name']}")
    
    # MAGMA 来源
    if magma_results:
        context_parts.append("\n=== [个人记忆] ===")
        for r in magma_results[:3]:
            context_parts.append(f"\n【记忆 #{r.get('id', '')[:8]}】\n{r.get('text', '')}")
            sources.append(f"memory:{r.get('id', '')[:8]}")
    
    if not context_parts:
        return "在所有知识系统中都没有找到相关内容。", []
    
    context = "\n".join(context_parts)
    
    system_prompt = """你是一个知识库助手，基于三个来源（Wiki/Skills/个人记忆）回答用户问题。

规则：
1. 综合多个来源的信息，不要只依赖一个来源
2. 引用来源时用 [来源:名称] 格式
3. 如果某个来源没有相关信息，跳过它
4. 回答要简洁、有条理，突出关键洞察"""

    prompt = f"""基于以下知识库内容，回答用户问题。

问题: {query}

{context}

请回答问题："""

    answer = call_llm(prompt, system=system_prompt)
    return answer, sources


# ============== 主函数 ==============

def query_unified(query: str, mode: str = "all") -> Dict:
    """
    统一检索入口
    
    modes:
        - "all": 全系统检索（wiki + skills + magma）
        - "wiki": 仅 wiki 知识库
        - "skills": 仅 skills 知识库  
        - "memory": 仅 MAGMA 记忆
    """
    print(f"\n🔍 统一检索: {query}")
    print(f"   模式: {mode}")
    print("-" * 50)
    
    wiki_results = []
    skills_results = []
    magma_results = []
    
    # 根据模式选择检索范围
    if mode in ["all", "wiki"]:
        print("\n[1/3] 检索 Wiki 知识库...")
        wiki_results = search_wiki(query)
        print(f"      找到 {len(wiki_results)} 个相关页面")
    
    if mode in ["all", "skills"]:
        print("\n[2/3] 检索 Skills 知识库...")
        skills_results = search_skills(query)
        print(f"      找到 {len(skills_results)} 个相关文档")
    
    if mode in ["all", "memory"]:
        print("\n[3/3] 检索 MAGMA 记忆...")
        magma_results = search_magma(query)
        print(f"      找到 {len(magma_results)} 条记忆")
    
    # 综合回答
    print("\n[综合] 生成回答...")
    answer, sources = synthesize_answer(query, wiki_results, skills_results, magma_results)
    
    return {
        'query': query,
        'mode': mode,
        'answer': answer,
        'sources': sources,
        'wiki_results': wiki_results,
        'skills_results': skills_results,
        'magma_results': magma_results
    }


def print_result(result: Dict):
    """打印检索结果"""
    print("\n" + "=" * 60)
    print("📝 回答")
    print("=" * 60)
    print(result['answer'])
    
    print("\n📚 来源")
    print("-" * 40)
    
    wiki = result.get('wiki_results', [])
    skills = result.get('skills_results', [])
    magma = result.get('magma_results', [])
    
    if wiki:
        print(f"\n【Wiki知识库】{len(wiki)} 个页面")
        for r in wiki:
            print(f"  • {r['name']} (score: {r['score']})")
    
    if skills:
        print(f"\n【Skills知识库】{len(skills)} 个文档")
        for r in skills:
            print(f"  • {r['rel_path']} (score: {r['score']})")
    
    if magma:
        print(f"\n【个人记忆】{len(magma)} 条")
        for r in magma:
            print(f"  • {r.get('text', '')[:50]}... (score: {r.get('score', 0):.2f})")
    
    print("\n" + "=" * 60)


def log_query(result: Dict):
    """记录查询到日志"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    entry = f"""

## [{timestamp}] query | {result['query'][:50]}
- 模式: {result['mode']}
- 来源数: {len(result['sources'])}
- Wiki: {len(result.get('wiki_results', []))}
- Skills: {len(result.get('skills_results', []))}
- Memory: {len(result.get('magma_results', []))}

"""
    
    if LOG_FILE.exists():
        existing = LOG_FILE.read_text(encoding='utf-8')
    else:
        existing = "# Wiki 操作日志\n\n"
    
    LOG_FILE.write_text(existing + entry, encoding='utf-8')


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n示例:")
        print('  python query.py "什么是 Harness Engineering"')
        print('  python query.py --wiki "OpenClaw"')
        print('  python query.py --memory "昨天的会议"')
        sys.exit(1)
    
    mode = "all"
    query_parts = []
    
    for arg in sys.argv[1:]:
        if arg.startswith("--"):
            mode = arg[2:]
        else:
            query_parts.append(arg)
    
    query = " ".join(query_parts)
    
    if mode == "help":
        print(__doc__)
        sys.exit(0)
    
    result = query_unified(query, mode)
    print_result(result)
    log_query(result)


def query_once(query: str, mode: str = "all") -> Dict:
    """单次查询 API"""
    return query_unified(query, mode)


if __name__ == '__main__':
    main()
