# 来源摘要：graphify-deep-analysis-2026-05-07.md

> 原始路径：raw/graphify-deep-analysis-2026-05-07.md
> 摄入时间：2026-06-03 08:50
> 验收状态：[~] pending

## 核心观点

Graphify 是一个开源代码与文档知识图谱工具，支持多格式输出、LLM语义提取、社区检测与MCP查询，显著节省Token并集成OpenClaw平台。

## 关键细节

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

#

## 相关实体
- [[graphifyy]]
- [[graphify]]
- [[NetworkX]]
- [[tree-sitter]]
- [[faster-whisper]]
- [[Gemini]]
- [[Claude]]
- [[GPT]]
- [[Kimi]]
- [[Neo4j]]
- [[Obsidian]]
- [[Notion]]
- [[GitHub]]
- [[MAGMA]]
- [[Karpathy KB]]
- [[Milvus]]
- [[GRAPH_REPORT.md]]
- [[graph.json]]
- [[graph.html]]
- [[graph.svg]]
- [[cypher.txt]]
- [[graph.canvas]]
- [[graph.graphml]]

## 相关概念
- [[Graphify]]
- [[知识图谱]]
- [[AST提取]]
- [[LLM语义提取]]
- [[Leiden社区检测]]
- [[God Nodes]]
- [[MCP服务]]
- [[OpenClaw集成]]
- [[Claude Code读取]]
- [[Token节省]]
- [[增量更新]]
- [[缓存机制]]
- [[多格式输出]]

---
*由 Karpathy 知识库系统自动生成*
