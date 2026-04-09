# Karpathy 知识库使用指南

> 基于 Andrej Karpathy 的 LLM Wiki 工作流，让 AI 帮你管理知识。

---

## 🎯 这是什么

一个本地知识管理系统，核心理念：

> **把枯燥的"书记员"工作交给 AI，你只负责提供资料和提好问题。**

- **你负责**：筛选和收集资料、提出好问题、得出结论
- **AI 负责**：阅读提炼、维护链接、整理归档

---

## 📁 目录结构

```
knowledge-base/
├── CLAUDE.md              # AI 说明书（必读）
├── raw/                   # 原始资料（只读）
│   ├── articles/         # 文章
│   ├── papers/           # 论文
│   ├── github/           # GitHub
│   └── datasets/         # 数据集
├── wiki/                 # 知识库（AI 维护）
│   ├── index.md          # 内容索引
│   ├── log.md           # 操作日志
│   ├── 概念/            # 原理/方法论/术语
│   ├── 来源/            # 来源摘要
│   └── 实体/            # 人/公司/产品/工具
├── comparisons/          # 对比分析（A vs B）
└── altpus/              # AI 答案报告
```

---

## 🚀 快速开始

### 第一步：添加资料

将原始资料放入 `raw/` 对应目录：

```bash
# 文章
raw/articles/我的文章.md

# 论文
raw/papers/论文标题.pdf

# GitHub 项目
raw/github/项目笔记.md
```

### 第二步：编译

```bash
cd E:\workspace\knowledge-base
python compile.py
```

### 第三步：提问

```bash
python query.py "我想了解 XXX"
```

---

## 📝 核心脚本

### compile.py — 编译知识库

```bash
python compile.py
```

功能：
- 读取 `raw/` 下的所有资料
- LLM 自动提取概念和实体
- 生成 `wiki/` 下的结构化文章
- 更新索引 `index.md`
- 记录操作日志 `log.md`

### query.py — 问答查询

```bash
# 交互式
python query.py

# 直接查询
python query.py "Karpathy 知识库是什么"
```

功能：
- 读取 `wiki/index.md` 找相关页面
- 读取相关 wiki 页面
- 综合答案回复
- 好答案可选择沉淀回 wiki

### lint.py — 健康检查

```bash
python lint.py
```

检查：
- 孤儿链接（有链接但页面不存在）
- 空/短页面
- 重复内容
- 目录结构完整性

### sync_feishu.py — 同步飞书

```bash
python sync_feishu.py
```

功能：
- 将 `wiki/` 所有文章同步到飞书文档
- 自动创建文档并写入内容

### sync_all.py — 全量同步

```bash
python sync_all.py
```

执行：
1. compile.py 编译
2. sync_feishu.py 飞书同步
3. sync_notion.py Notion 同步
4. upload_mem0.py 云端记忆

---

## 🔄 三阶段工作流

### INGEST（摄入）

添加新资料到 `raw/`，运行 `compile.py`：
- 生成来源摘要 → `wiki/来源/`
- 提取实体 → `wiki/实体/`
- 提取概念 → `wiki/概念/`
- 更新索引

### QUERY（查询）

运行 `query.py`：
- 先读 `index.md` 找相关页面
- 深入阅读相关 wiki 页面
- 综合答案回复
- 好答案 → 可选沉淀回 wiki

### LINT（维护）

定期运行 `lint.py`：
- 检查孤儿链接
- 检查矛盾说法
- 检查空页面
- 追加日志

---

## ⏰ 定时任务

已设置 Cron 定时任务，每天 20:00 自动同步：

```bash
# 查看定时任务
openclaw cron list | findstr knowledge

# 手动触发
openclaw cron run <job-id>
```

---

## 📊 状态统计

| 指标 | 数量 |
|------|------|
| 原始资料 | raw/ 下的文件 |
| Wiki 页面 | wiki/ 下的 md 文件 |
| 概念数 | wiki/概念/ 下的文件 |
| 实体数 | wiki/实体/ 下的文件 |

---

## ⚠️ 重要规则

1. **raw/ 永远只读** — 绝不修改原始资料
2. **先读 CLAUDE.md** — AI 开始工作前必读
3. **从 wiki 回答** — query 不直接读 raw
4. **log.md 只追加** — 不删除历史记录

---

## 🔧 配置

### 飞书

需要权限：`docx:document.block:convert`

### Notion

需要环境变量或文件：
```bash
set NOTION_API_TOKEN=你的token
```
或创建文件 `.notion_token`

### Milvus 云端记忆

已配置：
- 地址：8.137.122.11:19530
- 集合：CaySon_db

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| CLAUDE.md | AI 完整规则手册 |
| karpathy-knowledge-base-SOP.md | 完整 SOP 文档 |

---

*最后更新：2026-04-09*
*由 CaySon 知识库系统自动维护*
