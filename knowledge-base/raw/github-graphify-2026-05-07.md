# Graphify - 项目知识图谱工具

> 来源：GitHub https://github.com/safishamsi/graphify
> PyPI: `graphifyy` (double-y)
> License: MIT
> Python: 3.10+

## 📌 一句话定位

> **将任何代码/文档/论文/图片/视频文件夹转换为可查询的知识图谱** — 通过 AST 提取 + LLM 语义提取 + 社区检测，自动发现跨文件的连接关系

## 🎯 核心价值

| 维度 | 描述 |
|------|------|
| **输入** | 代码(28语言)、文档、图片、视频、PDF、网页 |
| **输出** | graph.html(可交互) + GRAPH_REPORT.md(报告) + graph.json(图数据) |
| **Token节省** | 52文件 corpus 查询节省 **71.5x** tokens |
| **隐私** | 代码 AST 本地处理，视频用 faster-whisper 本地转录 |

## 🏗️ 架构解析

### Pipeline 流程

```
detect() → extract() → build_graph() → cluster() → analyze() → report() → export()
```

| 模块 | 职责 |
|------|------|
| `detect.py` | 扫描文件，支持 .graphifyignore |
| `extract.py` | tree-sitter AST 提取节点+边（25种语言） |
| `build.py` | 合并多个提取结果，构建 NetworkX 图 |
| `cluster.py` | Leiden/Louvain 社区检测 |
| `analyze.py` | 发现 God Nodes、Surprising Connections |
| `report.py` | 生成 GRAPH_REPORT.md |
| `export.py` | 输出 HTML、Obsidian、Neo4j、GraphML |
| `ingest.py` | 抓取 URL（YouTube/arXiv/PDF/Twitter） |
| `cache.py` | SHA256 内容缓存，增量更新 |
| `serve.py` | MCP stdio 服务器 |

### 三阶段提取

| Pass | 内容 | 成本 |
|------|------|------|
| Pass 1 | **代码结构** — tree-sitter AST，免费，无 API 调用 | $0 |
| Pass 2 | **视频/音频** — faster-whisper 本地转录 | $0 |
| Pass 3 | **文档/论文/图片** — LLM 语义提取（Claude subagents） | $$$ |

## 🔧 核心设计

### 节点+边 Schema

```json
{
  "nodes": [
    {"id": "unique_id", "label": "Human Name", "file_type": "code|document|paper|image|rationale", "source_file": "path", "source_location": "L42"}
  ],
  "edges": [
    {"source": "id_a", "target": "id_b", "relation": "calls|imports|uses|semantically_similar_to", "confidence": "EXTRACTED|INFERRED|AMBIGUOUS", "confidence_score": 1.0}
  ]
}
```

### 置信度标签

| 标签 | 含义 | Score |
|------|------|-------|
| EXTRACTED | 源码直接关系（import、call） | 1.0 |
| INFERRED | LLM 推断（0.95/0.85/0.75/0.65/0.55） | 0.55-0.95 |
| AMBIGUOUS | 不确定，需人工审核 | 0.1-0.3 |

### 增量更新机制

1. **SHA256 Cache** — 按内容 hash 缓存，只重提取变化文件
2. **git commit hook** — `graphify hook install` 自动在每次 commit 后增量更新
3. **--watch 模式** — 监控文件夹变化，debounce 3s 后触发重建
4. **manifest.json** — 记录每个文件的 mtime，检测删除文件

### JS/TS 模块路径解析

`extract.py` 实现完整的 Vite/TypeScript 解析器：
- 相对路径：`./foo` → 尝试 `foo.ts` / `foo.tsx` / `index.ts`
- TypeScript ESM 约定：`.js` → `.ts`（写的是 .js，实际是 .ts）
- Svelte 5 Rune 文件：`foo.svelte` → `foo.svelte.ts`
- tsconfig.json path aliases：`@/` → `src/`
- 动态 `import()` 支持

### 社区检测算法

```python
# Leiden (graspologic) > Louvain (networkx 内置)
# 超大社区（>25%节点）二次分割
# 支持 directed/undirected 图
```

## 📊 对比 Karpathy 知识库

| 维度 | Graphify | Karpathy KB |
|------|----------|-------------|
| **输入** | 代码+文档+视频+图片 | 文档+截图 |
| **提取方式** | AST + LLM 双阶段 | LLM 直接提取 |
| **图关系** | calls/imports/语义相似 | 概念+引用 |
| **Token节省** | 71.5x（52文件测试） | 未测 |
| **社区检测** | Leiden 自动 | 无 |
| **增量更新** | SHA256 cache + git hook | 手动 |
| **输出格式** | HTML + JSON + MD报告 | MD文档 |
| **支持平台** | 15+ AI coding工具 | 主要 Claude Code |

## 🔗 OpenClaw 集成

```bash
# 安装
uv tool install graphifyy && graphify install --platform claw

# 使用
/graphify .                          # 当前目录构建图谱
/graphify ./src --update             # 增量更新
/graphify query "auth 模块连接哪些？" # BFS 查询
/graphify path "AuthService" "DB"   # 最短路径
/graphify --mcp                       # 启动 MCP 服务
```

### MCP 服务暴露的工具

- `query_graph` — 语义查询
- `get_node` — 获取节点详情
- `get_neighbors` — 邻居节点
- `get_community` — 社区成员
- `god_nodes` — 最关键节点
- `graph_stats` — 图统计
- `shortest_path` — 两节点路径

## 💡 与 MAGMA 图谱关系

**Graphify 是代码级图谱，MAGMA 是记忆/知识图谱：**

| 维度 | Graphify | MAGMA |
|------|----------|-------|
| **节点** | 函数/类/文件/概念 | 记忆片段/实体 |
| **边** | calls/imports/语义相似 | 因果/时间/实体关联 |
| **用途** | 代码理解/导航 | 记忆检索/推理 |
| **来源** | AST + LLM | 用户交互/知识库 |

**可以结合**：用 Graphify 理解代码结构，用 MAGMA 管理记忆

## 🚀 安装方式

```bash
# 官方包名是 graphifyy（双y）
uv tool install graphifyy && graphify install

# OpenClaw 平台
graphify install --platform claw

# 可选依赖
pip install 'graphifyy[office]'    # docx/xlsx
pip install 'graphifyy[video]'     # YouTube/视频转录
pip install 'graphifyy[mcp]'       # MCP 服务
```

## ⚠️ 已知限制

1. **Python 3.10+** 才支持 `graphify clone`
2. **PyPI 包名是 `graphifyy`**，不是 `graphify`
3. **语义提取默认用 Gemini**，需设置 `GEMINI_API_KEY`
4. **Windows PowerShell 5.1** — graspologic 输出会干扰滚动缓冲

## 📂 源码结构

```
graphify/
├── extract.py      # 800+行，核心 AST 提取，支持25种语言
├── build.py        # 图构建，三级去重
├── cluster.py      # Leiden 社区检测
├── analyze.py      # God Nodes + Surprising Connections
├── report.py       # Markdown 报告生成
├── export.py       # HTML/JSON/Obsidian/Neo4j/GraphML
├── detect.py       # 文件扫描，支持 .graphifyignore
├── cache.py        # SHA256 缓存管理
├── ingest.py       # URL 抓取（YouTube/arXiv/PDF）
├── transcribe.py   # faster-whisper 视频转录
├── serve.py        # MCP stdio 服务器
├── skill.md        # Claude Code Skill 完整 Prompt
├── skill-claw.md   # OpenClaw 集成
├── skill-codex.md  # Codex 集成
└── ...
```

## 🎯 适用场景

1. **大仓库理解** — 快速发现跨模块连接
2. **代码审查** — Surprising Connections 发现隐藏依赖
3. **文档生成** — 自动生成 GRAPH_REPORT.md
4. **知识管理** — 代码+文档+视频统一图谱
5. **Agent 记忆** — MCP 服务供其他 Agent 查询

## 📅 研究时间
2026-05-07
