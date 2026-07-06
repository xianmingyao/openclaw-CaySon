# Graphify 深度调研报告

> 日期：2026-05-07
> 源码：https://github.com/safishamsi/graphify
> PyPI包名：`graphifyy`（双y），CLI命令：`graphify`

---

## 一、核心架构

### 1.1 Pipeline 流程

```
detect() → extract() → build_graph() → cluster() → analyze() → report() → export()
```

| 模块 | 功能 | 成本 |
|------|------|------|
| `detect.py` | 扫描文件类型统计 | $0 |
| `extract.py` | AST提取代码 / LLM提取语义 | AST=$0 / LLM=API |
| `build.py` | 构建NetworkX图 | $0 |
| `cluster.py` | Leiden社区检测 | $0 |
| `analyze.py` | 发现God Nodes | $0 |
| `report.py` | 生成GRAPH_REPORT.md | $0 |
| `export.py` | 输出7种格式 | $0 |

### 1.2 输出格式

| 格式 | 文件 | 用途 |
|------|------|------|
| 浏览器可交互 | `graph.html` | 双击查看图谱 |
| 文字报告 | `GRAPH_REPORT.md` | Claude Code自动读取 |
| 程序查询 | `graph.json` | MCP工具查询 |
| 矢量图 | `graph.svg` | 嵌入Notion/GitHub |
| 图数据库 | `cypher.txt` | Neo4j导入 |
| Obsidian库 | `obsidian/` | Obsidian打开 |
| Canvas图 | `graph.canvas` | Obsidian Canvas |

---

## 二、接入配置（OpenClaw）

### 2.1 安装步骤

```bash
# 1. 安装 Python 包（包名是 graphifyy 双y）
uv tool install graphifyy

# 2. 安装 OpenClaw 平台集成
graphify install --platform claw

# 3. 配置 API Key（用于语义提取）
export GEMINI_API_KEY=xxx    # 默认用 Gemini
# 或
export ANTHROPIC_API_KEY=xxx # Claude
export OPENAI_API_KEY=xxx    # GPT
export MOONSHOT_API_KEY=xxx  # Kimi
```

### 2.2 OpenClaw Skill 配置

安装后会在 OpenClaw skill 目录创建 `graphify` skill，包含：
- `skill.md` - 主技能定义
- `skill-claw.md` - OpenClaw 专用版本（顺序处理）

触发命令：`/graphify`

---

## 三、触发存入数据

### 3.1 触发方式

| 方式 | 命令 | 说明 |
|------|------|------|
| **手动触发** | `/graphify .` | 当前目录 |
| **指定路径** | `/graphify ./src` | 特定目录 |
| **GitHub仓库** | `/graphify https://github.com/xxx/yyy` | 自动clone |
| **Git Hook自动** | `graphify hook install` | commit后自动增量 |
| **Watch监控** | `/graphify ./src --watch` | 监控变化 |
| **增量更新** | `/graphify . --update` | 只重提取变化文件 |

### 3.2 语义提取策略

**代码文件（AST提取 - $0本地）：**
- tree-sitter 解析28种编程语言
- 提取函数/类/变量节点
- 构建calls/imports边

**文档/图片/视频（LLM提取 - 消耗API）：**
- 图片用视觉模型理解
- 视频用faster-whisper转录（本地$0）
- 文档用LLM提取实体关系

### 3.3 缓存机制

```bash
# 检查缓存命中
Cache: 10 files hit, 3 files need extraction

# 增量更新（只处理变化文件）
/graphify . --update
```

---

## 四、读取图谱数据

### 4.1 MCP 服务（推荐方式）

```bash
# 启动 MCP stdio 服务器
python -m graphify.serve graphify-out/graph.json
# 或
graphify ./src --mcp
```

**暴露的工具：**

| 工具 | 功能 | 示例 |
|------|------|------|
| `query_graph` | BFS/DFS遍历查询 | query_graph("auth连接哪些？") |
| `get_node` | 获取节点详情 | get_node("Session") |
| `get_neighbors` | 获取邻居节点 | get_neighbors("RateLimiter") |
| `get_community` | 获取社区成员 | get_community(3) |
| `god_nodes` | 最重要节点 | god_nodes(top_n=10) |
| `graph_stats` | 图谱统计 | graph_stats() |
| `shortest_path` | 最短路径 | shortest_path("A","B") |

### 4.2 命令行查询

```bash
# 语义查询（BFS广度优先）
graphify query "what connects auth to database?"

# 深度查询（DFS深度优先）
graphify query "..." --dfs

# 最短路径
graphify path "AuthService" "DatabasePool"

# 解释节点
graphify explain "RateLimiter"
```

### 4.3 graph.json 结构

```json
{
  "nodes": [
    {
      "id": "session_validatetoken",
      "label": "Session.validateToken()",
      "source_file": "src/auth/session.py",
      "source_location": "L42",
      "community": 3,
      "file_type": "code"
    }
  ],
  "edges": [
    {
      "source": "session_validatetoken",
      "target": "db_user_repository",
      "relation": "calls",
      "confidence": "EXTRACTED",
      "confidence_score": 1.0
    }
  ],
  "hyperedges": [...]
}
```

---

## 五、Claude Code / OpenClaw 读取机制

### 5.1 自动读取原理

```bash
# 安装后，Claude Code/OpenClaw 会：
# 1. 在 skill 配置中指定读取 GRAPH_REPORT.md
# 2. 每次回答代码问题前自动读取该文件
# 3. skill.md 中的 trigger 规则触发
```

**skill.md 关键配置：**
```markdown
trigger: /graphify
description: "any input (code, docs, papers, images, videos) to knowledge graph"
```

### 5.2 OpenClaw 顺序处理

`skill-claw.md` 中说明：
> "OpenClaw platform: Multi-agent support is still early on OpenClaw. Extraction runs sequentially — you read and extract each file yourself."

**这意味着：**
- OpenClaw 不能并行启动多个 subagent
- 文档提取是顺序处理（较慢）
- 代码AST提取仍然是并行的

---

## 六、完整数据流图

```
┌─────────────────────────────────────────────────────────────┐
│                    Graphify 完整数据流                      │
└─────────────────────────────────────────────────────────────┘

【阶段1：存入数据】

  用户输入 /graphify .
       │
       ▼
  ┌─────────────────────────────────────┐
  │  Step 0: GitHub Clone（如果是URL）  │
  └─────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────┐
  │  Step 1: detect()                   │
  │  扫描文件类型统计                    │
  │  → .graphify_detect.json            │
  └─────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────┐
  │  Step 2: video转录（如有视频）       │
  │  faster-whisper 本地转录             │
  │  → .graphify_transcripts.json       │
  └─────────────────────────────────────┘
       │
       ▼
  ┌──────────────────┬──────────────────┐
  │  Part A: AST提取  │  Part B: 语义提取│
  │  （代码文件）      │  （文档/图片）   │
  │  tree-sitter      │  LLM API调用     │
  │  $0 本地          │  消耗API        │
  │  → .graphify_ast.json │ → 子agent并行 │
  └──────────────────┴──────────────────┘
       │
       ▼
  ┌─────────────────────────────────────┐
  │  Step 3: build_graph()              │
  │  构建NetworkX图                     │
  │  → 内存中的G                        │
  └─────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────┐
  │  Step 4: cluster()                  │
  │  Leiden社区检测                      │
  │  → communities{}                   │
  └─────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────┐
  │  Step 5: analyze()                  │
  │  God Nodes + 跨文件关系             │
  │  → analysis{}                       │
  └─────────────────────────────────────┘
       │
       ▼
  ┌─────────────────────────────────────┐
  │  Step 6: report() + export()        │
  │  生成多种格式输出                    │
  └─────────────────────────────────────┘
       │
       ▼
  graphify-out/
  ├── graph.html        ← 浏览器打开
  ├── GRAPH_REPORT.md   ← Claude Code自动读
  ├── graph.json       ← MCP程序查询
  ├── manifest.json    ← 缓存用
  ├── graph.svg        ← 嵌入文档
  ├── graph.graphml    ← Gephi打开
  ├── cypher.txt       ← Neo4j导入
  ├── obsidian/        ← Obsidian库
  └── graph.canvas     ← Obsidian Canvas


【阶段2：读取使用】

  方式1：命令行查询
  $ graphify query "auth连接哪些？"
       │
       ▼
  BFS遍历graph.json → 返回结构化答案

  方式2：MCP工具
  mcp__graphify__query_graph("auth连接哪些？")
       │
       ▼
  serve.py 读取graph.json → 返回结果

  方式3：Claude Code/OpenClaw 自动读取
  用户问代码问题
       │
       ▼
  skill触发 → 读取GRAPH_REPORT.md → 增强回答

  方式4：Neo4j图数据库
  graphify --neo4j-push bolt://localhost:7687
       │
       ▼
  直接推送节点边到Neo4j
```

---

## 七、与现有系统的关系

### 7.1 三个知识系统的分工

| 系统 | 数据来源 | 节点类型 | 用途 |
|------|---------|---------|------|
| **Graphify** | AST代码提取 | 函数/类/文件 | 代码导航、理解架构 |
| **MAGMA** | 用户交互积累 | 记忆片段 | 记忆检索、因果关系 |
| **Karpathy KB** | 文档/截图/视频 | 概念/来源 | 知识积累、学习 |

### 7.2 数据流转

```
用户使用代码/文档/视频
       │
       ├─────────────────┬─────────────────┐
       ▼                 ▼                 ▼
   Graphify          Karpathy KB         MAGMA
   (代码级)           (文档级)           (记忆级)
       │                 │                 │
       └─────────────────┴─────────────────┘
                         │
                         ▼
              Karpathy 知识库 (Milvus)
```

---

## 八、Token 节省效果

根据官方测试（52文件）：

| 指标 | 直接读全部 | Graphify | 节省 |
|------|----------|----------|------|
| Token消耗 | ~500K | ~7K | **71.5x** |

**原理：**
- 直接读取：每次问题都读全量文件
- Graphify：只读 GRAPH_REPORT.md 或 graph.json
- 社区检测：找到关键节点和高权重边

---

## 九、OpenClaw 集成的当前限制

### 9.1 skill-claw.md 明确说明

> "OpenClaw platform: Multi-agent support is still early on OpenClaw. Extraction runs sequentially — you read and extract each file yourself."

**影响：**
- 语义提取（文档/图片）不能并行
- 处理速度比 Claude Code 慢
- 但代码AST提取仍然很快（本地）

### 9.2 建议工作流

```bash
# 1. 先用 AST 提取代码（图谱免费）
/graphify . --no-viz

# 2. 单独处理文档（消耗API但可观察）
# 在 OpenClaw 中手动分批处理

# 3. MCP 查询（图谱始终可用）
graphify query "xxx"
```

---

## 十、最佳实践

### 10.1 Git Hook 自动触发

```bash
# 安装 post-commit hook
graphify hook install

# 每次 git commit 后自动增量更新图谱
# 只更新变化的文件（AST提取，$0成本）
```

### 10.2 团队协作

```bash
# 1. 一个人运行并提交图谱
/graphify .
git add graphify-out/ && git commit

# 2. 其他人 pull 后自动获得图谱
git pull

# 3. 团队共享同一份图谱
```

### 10.3 Neo4j 集成

```bash
# 生成 Cypher 文件
graphify ./src --neo4j

# 或直接推送
graphify ./src --neo4j-push bolt://localhost:7687
```

---

## 十一、总结：各环节详解

| 环节 | 怎么接入 | 怎么配置 | 怎么使用 | 成本 |
|------|---------|---------|---------|------|
| **触发存入** | `/graphify .` | skill已注册 | 输入命令 | AST=$0 / LLM=API |
| **增量更新** | `--update` | manifest缓存 | 自动检测变化 | 同上 |
| **Git Hook** | `hook install` | 自动配置 | commit触发 | AST=$0 |
| **MCP查询** | `--mcp` | serve.py | mcp工具调用 | $0 |
| **Claude Code** | skill自动 | install后生效 | 自动读报告 | $0 |
| **Neo4j** | `--neo4j-push` | Neo4j运行中 | 直接推送 | $0 |

---

## 📅 报告生成时间
2026-05-07
