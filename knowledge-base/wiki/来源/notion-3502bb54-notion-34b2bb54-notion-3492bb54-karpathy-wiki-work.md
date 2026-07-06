# Karpathy 知识库工作流：OpenClaw + Obsidian 落地实现

> 研究日期：2026-04-08

> 理论支撑：Karpathy 知识库编译工作流

---

## 1. 🎯 工作流总览

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

---

## 2. 🏗️ 目录结构设计

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

---

## 3. 🔧 工具实现

### 3.1 收集器（Collector）

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