# Graphify 完整使用流程分析报告

> 分析日期：2026-05-07
> 源码：https://github.com/safishamsi/graphify

---

## 一、核心定位

Graphify 是**代码知识图谱构建工具**，将任意代码/文档/视频/图片文件夹转换为可查询的知识图谱。

**与 MAGMA 图谱的关系：**
- Graphify = **代码/文档级图谱**（代码结构、跨文件关系）
- MAGMA = **记忆/知识级图谱**（用户交互、学习积累）

---

## 二、安装与配置

### 2.1 安装

```bash
# 官方包名是 graphifyy（双y）
uv tool install graphifyy && graphify install

# 可选依赖
pip install 'graphifyy[office]'    # docx/xlsx 支持
pip install 'graphifyy[video]'     # YouTube/视频转录
pip install 'graphifyy[mcp]'       # MCP 服务
```

### 2.2 OpenClaw 平台配置

```bash
# 安装 OpenClaw 集成
graphify install --platform claw

# 这会在 OpenClaw 中注册 skill，使其可以被触发
```

### 2.3 API Key 配置（用于语义提取）

```bash
# 语义提取（文档/图片）需要以下任一 Key
export GEMINI_API_KEY=xxx      # 默认用 Gemini
export ANTHROPIC_API_KEY=xxx   # 可选 Claude
export OPENAI_API_KEY=xxx      # 可选 GPT
export MOONSHOT_API_KEY=xxx   # 可选 Kimi

# 指定模型
export GRAPHIFY_GEMINI_MODEL=gemini-3-pro-preview
```

**注意：代码 AST 提取完全本地进行，无需 API Key**

---

## 三、触发图谱构建（存入数据）

### 3.1 完整 Pipeline 流程

```
用户触发 → detect() → extract() → build_graph() → cluster() → analyze() → report() → export()
```

| 步骤 | 模块 | 操作 | 成本 |
|------|------|------|------|
| 1 | detect | 扫描文件，统计类型 | $0 |
| 2 | extract | AST提取代码结构 | $0 |
| 3 | build | 构建 NetworkX 图 | $0 |
| 4 | cluster | Leiden 社区检测 | $0 |
| 5 | analyze | 发现 God Nodes | $0 |
| 6 | report | 生成 GRAPH_REPORT.md | $0 |
| 7 | export | 输出 HTML/JSON | $0 |

**语义提取（可选，文档/图片/视频）：**
- Pass 3 使用 LLM 提取，需要 API 调用
- 视频用 faster-whisper 本地转录，$0

### 3.2 触发方式

#### 方式1：命令行触发
```bash
/graphify .                           # 当前目录
/graphify ./src                       # 指定目录
/graphify https://github.com/xxx/yyy   # GitHub URL（自动 clone）
```

#### 方式2：增量更新
```bash
/graphify ./src --update              # 只重新提取变化的文件
```

#### 方式3：Git Hook 自动触发
```bash
graphify hook install                 # 安装 post-commit hook
# 每次 git commit 后自动增量更新图谱
```

#### 方式4：Watch 模式
```bash
graphify ./src --watch               # 监控文件夹变化，debounce 3s 后重建
```

### 3.3 输出文件

```
graphify-out/
├── graph.html       # 可交互的 HTML 图谱（浏览器打开）
├── GRAPH_REPORT.md  # 文字报告（God Nodes、跨文件关系）
├── graph.json       # 完整图数据（可程序查询）
├── manifest.json    # 文件清单（mtime 记录，增量用）
└── cache/          # SHA256 缓存
```

---

## 四、读取与使用图谱数据

### 4.1 图谱数据结构 (graph.json)

```json
{
  "nodes": [
    {
      "id": "session_validatetoken",
      "label": "Session.validateToken()",
      "source_file": "src/auth/session.py",
      "source_location": "L42",
      "community": 3
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
  ]
}
```

### 4.2 读取方式

#### 方式1：命令行查询
```bash
# 语义查询（BFS 遍历）
graphify query "auth 模块连接哪些？"

# 最短路径
graphify path "AuthService" "Database"

# 解释节点
graphify explain "RateLimiter"
```

#### 方式2：直接读取 JSON
```python
import json
with open('graphify-out/graph.json') as f:
    graph = json.load(f)
# graph["nodes"], graph["edges"] 直接使用
```

#### 方式3：MCP 服务（推荐）
```bash
graphify ./src --mcp
# 启动 MCP stdio 服务器，暴露工具：
# - query_graph
# - get_node
# - get_neighbors
# - shortest_path
# - god_nodes
# - graph_stats
```

---

## 五、不同工具的集成方式

### 5.1 Claude Code 集成

```bash
# 安装
graphify install                       # 自动检测 Claude Code
# 或
graphify install --platform claude

# 触发使用
/graphify .                            # 在 Claude Code 对话中输入
```

**读取图谱机制：**
1. 运行 `/graphify .` 生成 `GRAPH_REPORT.md`
2. Claude Code 的 skill 系统会在**每次回答代码问题前自动读取** `GRAPH_REPORT.md`
3. Skill 配置（`~/.claude/skills/`）告诉 Claude："回答代码问题时先读这个文件"

```markdown
# ~/.claude/skills/graphify/SKILL.md
# 告诉 Claude Code 读取 graphify-out/GRAPH_REPORT.md
```

### 5.2 Codex 集成

```bash
# 安装
graphify install --platform codex

# Codex 使用 $graphify 而不是 /graphify
$graphify .
```

### 5.3 OpenClaw (当前环境) 集成

```bash
# 安装
graphify install --platform claw

# 在 OpenClaw 中触发
/graphify .
```

**OpenClaw Skill 配置（skill.md）：**
```markdown
trigger: /graphify
description: "any input to knowledge graph"

# 触发后会执行完整的 pipeline
# 输出 graph.html + GRAPH_REPORT.md + graph.json
```

### 5.4 MCP 工具调用（通用方式）

无论哪个工具，都可以通过 MCP 协议访问图谱：

```bash
# 启动 MCP 服务
graphify ./src --mcp

# MCP 暴露的工具：
mcp__graphify__query_graph("what connects auth to database?")
mcp__graphify__get_node("Session_validateToken")
mcp__graphify__get_neighbors("RateLimiter")
mcp__graphify__shortest_path("AuthService", "Database")
mcp__graphify__god_nodes()  # 获取最重要的节点
```

---

## 六、完整使用流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    Graphify 使用流程                         │
└─────────────────────────────────────────────────────────────┘

【阶段1：构建图谱】
                                    
  用户输入                          工具执行
     │                               │
     ▼                               │
  /graphify .  ──────────────────────▶│
     │                               │
     │                    ┌──────────┴──────────┐
     │                    │   detect()           │
     │                    │   扫描文件类型         │
     │                    └──────────┬──────────┘
     │                               │
     │                    ┌──────────┴──────────┐
     │                    │   extract()          │
     │                    │   AST 提取节点+边    │  ← 本地执行，$0
     │                    └──────────┬──────────┘
     │                               │
     │                    ┌──────────┴──────────┐
     │                    │   build_graph()       │
     │                    │   构建 NetworkX 图    │
     │                    └──────────┬──────────┘
     │                               │
     │                    ┌──────────┴──────────┐
     │                    │   cluster()          │
     │                    │   Leiden 社区检测    │
     │                    └──────────┬──────────┘
     │                               │
     │                    ┌──────────┴──────────┐
     │                    │   analyze()          │
     │                    │   God Nodes + 关系   │
     │                    └──────────┬──────────┘
     │                               │
     │                    ┌──────────┴──────────┐
     │                    │   report() + export()│
     │                    │   生成报告+HTML       │
     │                    └──────────┬──────────┘
     │                               │
     ▼                               ▼
  graphify-out/
  ├── graph.html     ← 浏览器打开，可交互
  ├── GRAPH_REPORT.md ← 文字报告
  └── graph.json     ← 程序查询

【阶段2：查询图谱】

  用户问："auth 模块怎么连接数据库？"
                    │
                    ▼
  ┌─────────────────────────────────────┐
  │  读取 GRAPH_REPORT.md              │
  │  或 MCP query_graph()              │
  │  或直接读 graph.json               │
  └─────────────────────────────────────┘
                    │
                    ▼
  返回结构化答案 + 关键节点 + 路径
```

---

## 七、与其他知识库的集成

### 7.1 与 Karpathy 知识库对比

| 维度 | Graphify | Karpathy KB |
|------|----------|-------------|
| **输入** | 代码+文档+视频+图片 | 文档为主 |
| **提取** | AST + LLM | LLM 直接提取 |
| **增量** | SHA256 cache + git hook | 手动 |
| **图关系** | calls/imports/语义相似 | 概念+引用 |
| **Token 节省** | 71.5x（52文件测试） | 未测 |

### 7.2 与 MAGMA 记忆系统对比

| 维度 | Graphify | MAGMA |
|------|----------|-------|
| **节点** | 函数/类/文件 | 记忆片段 |
| **边** | calls/imports | 因果/时间 |
| **用途** | 代码理解 | 记忆检索 |
| **触发** | /graphify 命令 | 23:00 cron |

### 7.3 三者关系

```
┌─────────────┐     代码理解      ┌─────────────┐
│  Graphify   │ ────────────────▶ │  MAGMA 图谱  │
│  (代码级)   │                  │  (记忆级)   │
└─────────────┘                  └─────────────┘
        │                                ▲
        │ 知识积累                        │ 检索
        ▼                                │
┌─────────────┐                         │
│ Karpathy KB  │ ────────────────────────┘
│  (文档级)   │    知识同步
└─────────────┘
```

---

## 八、OpenClaw 中 Graphify 的最佳实践

### 8.1 触发方式

```bash
# 在 OpenClaw 对话中输入
/graphify E:\workspace
```

### 8.2 读取图谱

```bash
# 查询（通过 MCP 或直接读文件）
type graphify-out\GRAPH_REPORT.md
type graphify-out\graph.json | jq ".nodes[:5]"
```

### 8.3 Neo4j 集成（可选）

```bash
# 导出为 Neo4j 可读的 cypher
graphify ./src --neo4j

# 直接推送
graphify ./src --neo4j-push bolt://localhost:7687
```

---

## 九、总结

| 问题 | 答案 |
|------|------|
| **怎么接入** | `uv tool install graphifyy && graphify install --platform claw` |
| **怎么配置** | 设置 GEMINI_API_KEY，配置 skill |
| **怎么触发存数据** | `/graphify .` 或 git hook 自动触发 |
| **怎么读取** | graph.html 浏览器查看 / GRAPH_REPORT.md / graph.json / MCP |
| **Claude Code 怎么用** | 安装 skill 后自动读取 GRAPH_REPORT.md |
| **数据在哪** | `graphify-out/` 目录 |
| **增量怎么搞** | `--update` 参数或 git hook |
| **成本多少** | 代码提取 $0，语义提取消耗 API |

---

## 📅 报告生成时间
2026-05-07
