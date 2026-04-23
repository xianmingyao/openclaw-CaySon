# Karpathy 知识库完整 SOP

> 基于 Andrej Karpathy 的 LLM Wiki 工作流

---

## 🎯 这是什么

**Karpathy 风格 AI 知识库** — 用 LLM 将原始资料编译成结构化 wiki 知识库。

**核心理念**：不用 RAG，直接让 LLM 编译 wiki，直接问直接答。

---

## 📝 核心功能点

1. **收集 (Collect)**: `raw/` 目录存放原始资料
2. **编译 (Compile)**: LLM 读取 raw → 生成结构化 wiki
3. **查询 (Query)**: 直接问 LLM，答案归档回 wiki
4. **同步**: 飞书文档 + Notion + 云端 Milvus 记忆

---

## ⚡ 怎么使用

### 每日使用流程

#### 1. 添加原始资料

将资料放入 `raw/` 对应目录：

```
raw/
├── papers/           # 论文 (PDF/md)
├── articles/        # 文章 (md)
├── github/          # GitHub 代码 (md/txt)
├── datasets/        # 数据集 (csv/json)
└── screenshots/     # 截图 (md)
```

**推荐方式**：使用 Obsidian Web Clipper 保存网页为 md

#### 2. 手动同步

```bash
cd E:\workspace\knowledge-base
python sync_all.py
```

#### 3. 自动同步（Cron）

每天 20:00 自动运行，详情：
```
openclaw cron list | findstr knowledge-base
```

---

## ✅ 优点

1. **零 RAG**：100 篇/40 万字规模下，LLM 上下文窗口足够大
2. **结构清晰**：wiki 格式，双向链接，知识可沉淀
3. **自动化**：raw → wiki 全自动
4. **多端同步**：飞书 + Notion + 云端记忆

---

## ❌ 缺点

1. **飞书内容写入**：需要 `docx:document.block:convert` 权限
2. **Notion**：需要 `NOTION_API_TOKEN`
3. **规模限制**：超过 1000 篇需要分层索引

---

## 🎬 使用场景

- 科研文献管理
- 技术博客知识沉淀
- AI 资讯收集整理
- 个人知识管理系统

---

## 🔧 运行依赖环境

| 依赖 | 说明 |
|------|------|
| Python 3.10+ | 运行环境 |
| Ollama | LLM + Embedding |
| Milvus | 云端记忆存储 |
| Feishu | 文档同步 |
| Notion | 笔记同步（需 API Token） |

---

## 🚀 部署使用注意点

### 目录结构

```
E:\workspace\knowledge-base\
├── CLAUDE.md           # Schema 规则手册
├── raw/                # 原始资料（不修改）
├── wiki/               # 编译后的知识库
├── comparisons/        # 对比分析
├── altpus/             # AI 答案报告
├── compile.py          # 编译脚本
├── lint.py             # 健康检查
├── query.py            # 问答查询
├── sync_feishu.py      # 飞书同步
├── sync_notion.py      # Notion 同步
└── sync_all.py         # 全量同步
```

### LLM 配置

- **模型**: qwen2.5:7b（编译用）
- **Embedding**: nomic-embed-text
- **Ollama 地址**: http://localhost:11434

### Milvus 配置

- **地址**: 8.137.122.11:19530
- **集合**: CaySon_db

---

## 🕳️ 避坑指南

### 🔴 坑1：Feishu 文档内容写入失败

**问题**：`docx:document.block:convert` 权限缺失
**解决**：在飞书开放平台 → 应用权限 → 申请 `docx:document.block:convert`

### 🔴 坑2：Notion 同步无法使用

**问题**：`NOTION_API_TOKEN` 未配置
**解决**：
```bash
set NOTION_API_TOKEN=your_token
```

### 🔴 坑3：Ollama 连接失败

**问题**：Ollama 服务未启动
**解决**：
```bash
ollama serve
```

---

## 📊 总结

**学习价值**：⭐⭐⭐⭐⭐（5星）
**推荐指数**：⭐⭐⭐⭐（4星）
**自动化程度**：⭐⭐⭐⭐（4星）

**适用人群**：需要管理大量研究资料的技术人/科研人员

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| README.md | 快速开始指南 |
| CLAUDE.md | AI 完整规则手册 |
| raw/README.md | 原始资料说明 |

---

*最后更新：2026-04-09*

