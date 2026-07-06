# 来源摘要：graphify-deep-analysis-2026-05-07.md

> 原始路径：raw/graphify-deep-analysis-2026-05-07.md
> 摄入时间：2026-05-14 09:27
> 验收状态：[~] pending

## 核心观点

报告详细分析了Graphify的架构、数据流程和与现有系统的集成，强调了其在代码导航和知识积累方面的优势。

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
- [[detect.py]]
- [[extract.py]]
- [[build.py]]
- [[cluster.py]]
- [[analyze.py]]
- [[report.py]]
- [[export.py]]
- [[graph.html]]
- [[GRAPH_REPORT.md]]
- [[graph.json]]
- [[obsidian/]]
- [[cypher.txt]]
- [[graph.canvas]]
- [[GitHub]]
- [[tree-sitter]]
- [[LLM]]
- [[Claude Code]]
- [[OpenClaw]]
- [[skill.md]]
- [[skill-claw.md]]
- [[MAGMA]]
- [[Karpathy KB]]
- [[Milvus]]

## 相关概念
- [[Graphify]]
- [[Pipeline流程]]
- [[输出格式]]
- [[OpenClaw]]
- [[存入数据]]
- [[读取图谱数据]]
- [[知识系统分工]]
- [[Token节省效果]]
- [[OpenClaw集成限制]]

---
*由 Karpathy 知识库系统自动生成*
