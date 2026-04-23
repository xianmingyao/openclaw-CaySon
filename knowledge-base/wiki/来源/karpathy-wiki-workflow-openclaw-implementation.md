# Karpathy 知识库工作流：OpenClaw + Obsidian 落地实现

> 研究日期：2026-04-08
> 理论支撑：Karpathy 知识库编译工作流

---

## 1. 🎯 工作流总览

```
┌─────────────────────────────────────────────────────────────┐
│                    知识管理工作流                            │
│                                                             │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐            │
│  │  收集   │ ──► │  编译   │ ──► │  查询   │            │
│  │ Collect │     │Compile │     │  Query  │            │
│  └─────────┘     └─────────┘     └─────────┘            │
│       ↓               ↓               ↓                   │
│   raw/           wiki/            LLM 直接              │
│   原始资料         知识库           查找答案              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 🏗️ 目录结构设计

```
knowledge-workspace/
├── raw/                    # 原始资料（收集阶段）
│   ├── papers/            # 论文 PDF + 笔记
│   ├── articles/          # 文章 Markdown
│   ├── github/            # 代码片段 + README
│   ├── datasets/          # 数据文件
│   └── screenshots/       # 截图
│
├── wiki/                   # 知识库（编译阶段）
│   ├── .obsidian/        # Obsidian 配置
│   ├── _index.md          # 知识库索引
│   ├── concepts/          # 概念文章
│   │   ├── concept-1.md
│   │   └── concept-2.md
│   ├── categories/        # 分类目录
│   │   ├── ai-ml.md
│   │   └── tools.md
│   └── _templates/        # 模板
│
├── workspace/             # OpenClaw 工作区
│   └── knowledge-agent/
│       ├── collector.py   # 收集器
│       ├── compiler.py    # 编译器
│       ├── query.py       # 查询器
│       └── config.yaml    # 配置
│
└── config.yaml            # 全局配置
```

---

## 3. 🔧 工具实现

### 3.1 收集器（Collector）

```python
# collector.py
import os
import json
from datetime import datetime
from pathlib import Path

class KnowledgeCollector:
    """
    知识收集器：收集原始资料到 raw/ 目录
    """
    
    def __init__(self, raw_dir: str):
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        self.categories = ['papers', 'articles', 'github', 'datasets', 'screenshots']
        for cat in self.categories:
            (self.raw_dir / cat).mkdir(exist_ok=True)
    
    def collect_from_url(self, url: str, category: str = 'articles') -> dict:
        """
        从 URL 收集网页内容
        """
        # 使用 web_fetch 获取内容
        from openclaw.tools import web_fetch
        
        content = web_fetch(url)
        filename = self._url_to_filename(url)
        filepath = self.raw_dir / category / filename
        
        # 保存为 Markdown
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"---\n")
            f.write(f"source: {url}\n")
            f.write(f"collected_at: {datetime.now().isoformat()}\n")
            f.write(f"category: {category}\n")
            f.write(f"---\n\n")
            f.write(content)
        
        return {
            "status": "success",
            "filepath": str(filepath),
            "category": category
        }
    
    def collect_from_file(self, filepath: str, category: str) -> dict:
        """
        从本地文件收集
        """
        import shutil
        
        src = Path(filepath)
        dst = self.raw_dir / category / src.name
        
        shutil.copy2(src, dst)
        
        return {
            "status": "success",
            "filepath": str(dst),
            "category": category
        }
    
    def collect_github_repo(self, repo_url: str) -> dict:
        """
        收集 GitHub 仓库
        """
        # 解析 repo URL
        # 使用 git clone 或直接下载 README
        pass
    
    def _url_to_filename(self, url: str) -> str:
        """URL 转安全的文件名"""
        import hashlib
        import re
        
        # 取 URL 最后部分作为基础名
        name = url.split('/')[-1]
        name = re.sub(r'[^\w\-_.]', '_', name)
        
        # 添加 hash 确保唯一
        hash_suffix = hashlib.md5(url.encode()).hexdigest()[:8]
        
        return f"{name}_{hash_suffix}.md"
    
    def get_collection_stats(self) -> dict:
        """获取收集统计"""
        stats = {}
        for cat in self.categories:
            cat_path = self.raw_dir / cat
            stats[cat] = len(list(cat_path.glob('*')))
        
        stats['total'] = sum(stats.values())
        return stats
```

---

### 3.2 编译器（Compiler）

```python
# compiler.py
import os
from pathlib import Path
from typing import List, Dict

class WikiCompiler:
    """
    Wiki 编译器：将 raw/ 目录编译成 wiki 知识库
    """
    
    SYSTEM_PROMPT = """你是一个知识整理专家。请将 raw/ 目录下的所有资料编译成一个 wiki 知识库。

要求：
1. 读取所有 .md 文件
2. 提取每个文件的核心概念
3. 为每个概念写一篇简短的解释文章
4. 建立分类目录结构
5. 添加双向链接（bidirectional links）关联相关概念
6. 输出格式：Markdown

重要：
- 概念文章应该简洁，100-300 字
- 使用 [[双向链接]] 关联相关概念
- 在末尾添加 #相关概念 标签"""

    def __init__(self, raw_dir: str, wiki_dir: str, llm_client):
        self.raw_dir = Path(raw_dir)
        self.wiki_dir = Path(wiki_dir)
        self.llm = llm_client
        
        # 创建 wiki 目录结构
        self.wiki_dir.mkdir(parents=True, exist_ok=True)
        (self.wiki_dir / 'concepts').mkdir(exist_ok=True)
        (self.wiki_dir / 'categories').mkdir(exist_ok=True)
    
    def compile(self) -> dict:
        """
        执行编译
        """
        # 1. 读取 raw/ 所有文件
        raw_files = list(self.raw_dir.rglob('*.md'))
        
        # 2. 读取所有内容
        contents = []
        for f in raw_files:
            with open(f, 'r', encoding='utf-8') as fp:
                contents.append(fp.read())
        
        # 3. 构建编译 Prompt
        prompt = self.SYSTEM_PROMPT + "\n\n"
        prompt += f"共 {len(contents)} 个文件：\n\n"
        for i, content in enumerate(contents[:20]):  # 限制数量
            prompt += f"--- 文件 {i+1} ---\n{content[:2000]}\n\n"
        
        # 4. 调用 LLM
        response = self.llm.generate(prompt)
        
        # 5. 解析响应，生成概念文章
        concepts = self._parse_response(response)
        
        # 6. 写入 wiki/
        for concept in concepts:
            self._write_concept(concept)
        
        # 7. 生成索引
        self._generate_index(concepts)
        
        return {
            "status": "success",
            "concepts_count": len(concepts),
            "wiki_dir": str(self.wiki_dir)
        }
    
    def _parse_response(self, response: str) -> List[Dict]:
        """解析 LLM 响应，提取概念"""
        # 简化实现：按标题拆分
        concepts = []
        lines = response.split('\n')
        current_concept = None
        current_content = []
        
        for line in lines:
            if line.startswith('## '):
                if current_concept:
                    concepts.append({
                        "title": current_concept,
                        "content": '\n'.join(current_content)
                    })
                current_concept = line[3:].strip()
                current_content = []
            elif line.startswith('# '):
                if current_concept:
                    concepts.append({
                        "title": current_concept,
                        "content": '\n'.join(current_content)
                    })
                current_concept = line[2:].strip()
                current_content = []
            else:
                current_content.append(line)
        
        if current_concept:
            concepts.append({
                "title": current_concept,
                "content": '\n'.join(current_content)
            })
        
        return concepts
    
    def _write_concept(self, concept: Dict):
        """写入单个概念文件"""
        filename = concept['title'].lower().replace(' ', '-') + '.md'
        filepath = self.wiki_dir / 'concepts' / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {concept['title']}\n\n")
            f.write(concept['content'])
        
        # 添加反向链接索引
        self._add_backlink(concept['title'], filename)
    
    def _add_backlink(self, title: str, filename: str):
        """添加反向链接"""
        # 简单实现：维护一个链接索引
        # 完整实现需要双向链接解析
        pass
    
    def _generate_index(self, concepts: List[Dict]):
        """生成知识库索引"""
        index_path = self.wiki_dir / '_index.md'
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# 知识库索引\n\n")
            f.write(f"共 {len(concepts)} 个概念\n\n")
            f.write("## 概念列表\n\n")
            for concept in concepts:
                link = concept['title'].lower().replace(' ', '-')
                f.write(f"- [[{concept['title']}]]\n")
```

---

### 3.3 查询器（Query）

```python
# query.py
from pathlib import Path
from typing import List, Dict

class KnowledgeQuery:
    """
    知识查询器：在 wiki 中查找答案
    """
    
    def __init__(self, wiki_dir: str, llm_client):
        self.wiki_dir = Path(wiki_dir)
        self.llm = llm_client
        self._cache = {}
    
    def query(self, question: str, top_k: int = 5) -> Dict:
        """
        查询问题
        
        策略：
        1. 如果 wiki 规模小（< 100 篇），直接全部加载到 context
        2. 如果规模大，使用向量搜索召回
        """
        # 检查 wiki 规模
        concept_files = list((self.wiki_dir / 'concepts').glob('*.md'))
        
        if len(concept_files) < 100:
            # 小规模：全部加载
            context = self._load_all_concepts()
        else:
            # 大规模：向量搜索召回
            context = self._search_concepts(question, top_k)
        
        # 构建查询 Prompt
        prompt = f"""你是一个知识库助手。请在以下知识中查找问题的答案。

问题：{question}

知识内容：
{context}

要求：
1. 如果找到答案，直接回答
2. 如果找到相关但不完全匹配的内容，提供参考
3. 如果没有找到，说明未找到

回答："""
        
        # 调用 LLM
        response = self.llm.generate(prompt)
        
        # 检查答案质量
        quality = self._evaluate_answer(question, response)
        
        return {
            "question": question,
            "answer": response,
            "concepts_used": self._extract_links(response),
            "quality_score": quality,
            "should_archive": quality > 0.8  # 高质量答案归档
        }
    
    def _load_all_concepts(self) -> str:
        """加载所有概念"""
        concepts_dir = self.wiki_dir / 'concepts'
        all_content = []
        
        for f in concepts_dir.glob('*.md'):
            with open(f, 'r', encoding='utf-8') as fp:
                all_content.append(fp.read())
        
        return '\n\n'.join(all_content)
    
    def _search_concepts(self, query: str, top_k: int) -> str:
        """向量搜索召回"""
        # 使用 embedding 搜索
        # 简化实现：关键词匹配
        concepts_dir = self.wiki_dir / 'concepts'
        query_words = set(query.lower().split())
        
        scored = []
        for f in concepts_dir.glob('*.md'):
            with open(f, 'r', encoding='utf-8') as fp:
                content = fp.read()
                content_words = set(content.lower().split())
                score = len(query_words & content_words)
                scored.append((score, content))
        
        scored.sort(reverse=True)
        return '\n\n'.join([c[1] for c in scored[:top_k]])
    
    def _evaluate_answer(self, question: str, answer: str) -> float:
        """评估答案质量"""
        # 简化实现：检查答案长度和关键词
        if len(answer) < 20:
            return 0.0
        
        # 检查是否包含问题关键词
        question_words = set(question.lower().split())
        answer_words = set(answer.lower().split())
        
        overlap = len(question_words & answer_words)
        return min(1.0, overlap / len(question_words))
    
    def _extract_links(self, text: str) -> List[str]:
        """提取双向链接"""
        import re
        return re.findall(r'\[\[([^\]]+)\]\]', text)
```

---

## 4. 🔄 OpenClaw Skill 封装

### 4.1 knowledge-workflow Skill

```markdown
# knowledge-workflow

## 描述
个人知识库管理工作流：收集 → 编译 → 查询

## 触发条件
- "收集知识"
- "整理知识库"
- "编译 wiki"
- "查询知识"

## 指令（Instructions）
你是一个知识管理助手。当用户要求管理知识时：

### 收集模式
当用户说"收集"或"保存"时：
1. 识别知识来源（URL/文件/文本）
2. 使用 collector 工具收集到 raw/ 目录
3. 确认收集完成

### 编译模式
当用户说"编译"或"整理"时：
1. 读取 raw/ 目录所有内容
2. 调用 LLM 编译成 wiki
3. 生成概念文章和双向链接
4. 输出编译结果

### 查询模式
当用户提出问题时：
1. 在 wiki/ 中搜索相关内容
2. 调用 LLM 在上下文中回答
3. 如果答案质量高，建议归档

## 工具（Tools）
- collector.collect_from_url: 收集网页
- collector.collect_from_file: 收集文件
- compiler.compile: 编译知识库
- query.query: 查询知识

## 目录结构
- raw/: 原始资料
- wiki/: 知识库

## 注意事项
- 每次收集后更新统计
- 编译前检查 raw/ 内容
- 查询时记录质量分数
```

---

## 5. 📊 监控指标

### 5.1 知识库健康度

| 指标 | 计算方式 | 健康阈值 |
|------|---------|---------|
| 收集数量 | raw/ 文件数 | > 0 |
| 概念数量 | wiki/concepts/ 文件数 | > 10 |
| 平均链接数 | 每篇概念的链接数 | > 2 |
| 查询成功率 | 有答案的查询比例 | > 80% |
| 归档率 | 高质量答案归档比例 | > 10% |

### 5.2 成长趋势

```
知识库成长 = f(收集数量, 编译频率, 查询反馈)

目标：
- 每周收集 10+ 新资料
- 每周编译 1 次
- 每月归档 5+ 高质量问答
```

---

## 6. 🚀 使用流程

### 6.1 日常使用

```
用户：帮我收集这篇论文的摘要
Agent：使用 collector 工具
      ↓
用户：整理成知识库
Agent：使用 compiler.compile()
      ↓
用户：什么是 RAG？
Agent：使用 query.query()
      ↓
Agent：找到答案，建议归档
      ↓
用户：归档
Agent：更新 wiki/
```

### 6.2 定期维护

```
每周：
1. 收集新资料到 raw/
2. 执行编译更新 wiki/
3. 检查知识库健康度

每月：
1. 清理过时内容
2. 优化链接结构
3. 归档高质量查询
```

---

## 7. 📊 总结

| 维度 | 评分 |
|------|------|
| 可实施性 | ⭐⭐⭐⭐ |
| 实用性 | ⭐⭐⭐⭐⭐ |
| 自动化程度 | ⭐⭐⭐ |

### 一句话总结
> **Obsidian 收集 + LLM 编译 + OpenClaw 查询 = 个人知识库自动化工作流，让知识在 wiki 中自生长。**

### 行动清单

- [ ] 搭建目录结构
- [ ] 实现 Collector 收集器
- [ ] 实现 Compiler 编译器
- [ ] 实现 Query 查询器
- [ ] 封装为 OpenClaw Skill
- [ ] 配置定时编译任务

