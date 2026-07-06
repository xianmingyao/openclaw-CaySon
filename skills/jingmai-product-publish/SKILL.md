---
name: jm-ufo-agent
description: "京麦（京东卖家后台）商品上架自动化 CLI。基于 LangGraph 工作流 + UFO 桌面自动化，支持 dry-run 模拟、Excel 批量导入、MiniMax AI 评审、MySQL 持久化。提供 14 个子命令：dry-run、run、dashboard、live-dashboard、tail-dashboard、inspect-ufo、inspect-jingmai-window、capture-halt-evidence、import-excel、production-readiness、validate-small-batch、minimax-preflight、mysql-preflight、mysql-apply-schema。所有触达真实京麦窗口的操作都有显式安全门控。Use when user mentions '京麦', 'jingmai', '商品上架', 'product publish', 'jm-ufo-agent', '京麦CLI', '自动化上架', '商品审核', '京麦窗口', 'UFO桌面自动化', 'jinguo', '京东卖家后台'."
---

# jm-ufo-agent - 京麦商品上架自动化 CLI

**描述:** 京麦（京东卖家后台）商品上架自动化工具。基于 LangGraph 工作流 + UFO 桌面自动化，支持 dry-run 模拟、Excel 批量导入、MiniMax AI 评审、MySQL 持久化。
**安全设计:** 所有会触达真实京麦窗口的操作都挂在安全门控之后，默认 observe-only，防止误操作生产环境。
**跨平台:** Windows 桌面自动化（UFO/Win32），CLI 在任意平台可用（dry-run 模式）。

## TL;DR — 命令速查表

| 我想... | 用这个命令 | 是否触碰真实环境 |
|---------|-----------|----------------|
| 跑一个商品的模拟工作流 | `dry-run` | ❌ 完全模拟 |
| 启动真实任务（默认 dry-run） | `run --backend ufo-observe` | ⚠️ 加 `--confirm-real-jingmai` 才真 |
| 查看一次执行快照 | `dashboard` | ❌ 只读 |
| 实时跟踪运行中的任务 | `tail-dashboard --rich-live` | ❌ 只读 |
| 采集现场证据（截图/OCR） | `capture-halt-evidence` | ❌ 只读 |
| 解析 Excel 验收 | `import-excel` | ❌ 默认 dry-run |
| 写 Excel 到 MySQL | `import-excel --write-mysql --confirm-write-mysql` | ✅ 双重确认 |
| 评估生产就绪度 | `production-readiness` | ❌ 只读 |
| 预检 MiniMax / MySQL | `minimax-preflight` / `mysql-preflight` | ❌ 只读 |
| 应用数据库 DDL | `mysql-apply-schema --confirm-apply-schema` | ✅ 显式确认 |

## 典型用户故事 → 命令映射

| 场景 | 路径 |
|------|------|
| **新接入开发者**：第一次跑通工作流 | `dry-run` → `import-excel`（dry-run）→ `production-readiness` |
| **数据工程师**：把 Excel 导入数据库 | `mysql-preflight` → `mysql-apply-schema --confirm-apply-schema` → `import-excel --write-mysql --confirm-write-mysql` |
| **运维**：上线前确认依赖就绪 | `minimax-preflight` + `mysql-preflight` + `production-readiness` |
| **故障排查**：某个 row 卡住需要现场证据 | `capture-halt-evidence --use-tesseract` → `tail-dashboard` 跟 JSONL |
| **小批量灰度**：row5-row7 验证 | `validate-small-batch`（全部通过才放行 row82） |
| **CI/CD 流水线**：dry-run 跑回归 | `dry-run --task-id <id> --row-index <n>` + `--max-frames` 限制 tail |

## 环境安装（pip/poetry）

```bash
# 安装项目
cd jingmai-product-publish
pip install -e .

# 可选依赖组
pip install -e ".[storage]"    # MySQL + Redis + Milvus
pip install -e ".[ocr]"        # Pillow + pytesseract
# Tesseract OCR 系统依赖（必须单独安装）：
#   winget install --id UB-Mannheim.TesseractOCR -e --silent --accept-package-agreements --accept-source-agreements
# 中文语言包：下载 chi_sim.traineddata 到 C:\Program Files\Tesseract-OCR\tessdata\
#   https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata
pip install -e ".[rich-ui]"    # Rich 进度面板
pip install -e ".[all]"        # 全部可选依赖

# 或使用 poetry
poetry install --extras all
```

安装后即可使用 `jm-ufo-agent` 命令。

## 快速开始

```bash
# 单行商品 dry-run（不触碰京麦）
jm-ufo-agent dry-run --task-id T001 --row-index 5 --product-json '{"title":"测试商品"}'

# 也可以用 @文件 传入复杂 JSON（Windows PowerShell 友好）
jm-ufo-agent dry-run --task-id T001 --row-index 5 --product-json @product.json

# 查看 CLI 帮助
jm-ufo-agent --help
jm-ufo-agent dry-run --help
```

## 工作流命令

### `jm-ufo-agent dry-run` — 单行商品 dry-run 工作流

纯模拟执行，不连接京麦窗口，不写入数据库。适合开发调试和验收测试。

```bash
jm-ufo-agent dry-run --task-id T001 --row-index 5 --product-json '{"title":"纯棉T恤","price":"29.9"}'
```

**参数：**
- `--task-id` — 任务 ID（必需）
- `--row-index` — 行号（必需）
- `--product-json` — 商品 JSON，支持 `@path.json` 文件引用（必需）

### `jm-ufo-agent run` — 按文档入口启动任务

默认使用 dry-run backend，可通过 `--backend` 切换。真实 backend 必须显式确认。

```bash
# 默认 dry-run backend
jm-ufo-agent run --task-id T001 --row-index 82

# UFO 观察模式（只读，不点击不输入）
jm-ufo-agent run --task-id T001 --row-index 82 --backend ufo-observe

# 真实京麦操作（必须双重确认）
jm-ufo-agent run --task-id T001 --row-index 82 --backend ufo-observe --confirm-real-jingmai
```

**参数：**
- `--task-id` — 任务 ID（必需）
- `--row-index` — 行号，默认 `82`
- `--product-json` — 商品 JSON，默认 `{}`
- `--backend` — 后端：`dry-run` | `ufo-observe`，默认 `dry-run`
- `--confirm-real-jingmai` — 确认操作真实京麦窗口（安全门控）
- `--observe-only` / `--no-observe-only` — 是否只读观察，默认只读

## Dashboard 进度面板命令

### `jm-ufo-agent dashboard` — 渲染一次进度面板

从 JSON 状态文件渲染 Rich/text 进度面板，适合查看单次快照。

```bash
jm-ufo-agent dashboard --state-json @state.json
```

**参数：**
- `--state-json` — 状态 JSON，支持 `@path.json` 文件引用（必需）

### `jm-ufo-agent live-dashboard` — 渲染多帧进度面板

从 JSONL 状态流文件渲染多帧进度，适合回放历史运行记录。

```bash
jm-ufo-agent live-dashboard --states-jsonl run_20260610.jsonl
```

**参数：**
- `--states-jsonl` — JSONL 状态流文件路径（必需）

### `jm-ufo-agent tail-dashboard` — 实时跟随进度面板

持续读取 JSONL 状态流并实时渲染，适合跟踪正在运行的任务。

```bash
# 持续跟随
jm-ufo-agent tail-dashboard --states-jsonl run_live.jsonl --rich-live

# 限制帧数（CI/验收用）
jm-ufo-agent tail-dashboard --states-jsonl run_live.jsonl --max-frames 10
```

**参数：**
- `--states-jsonl` — JSONL 状态流文件路径（必需）
- `--poll-interval-sec` — 轮询间隔（秒），默认 `1.0`
- `--max-frames` — 最大渲染帧数，不设则持续跟随
- `--rich-live` — 启用 Rich Live 交互式 UI（需 `rich` 依赖）

## 窗口检查命令

### `jm-ufo-agent inspect-ufo` — 检查 UFO 适配源码路径

检查本机 UFO v1 源码路径是否可用，输出源码文件和能力报告。

```bash
jm-ufo-agent inspect-ufo --ufo-root E:/PY/UFO/ufo
```

**参数：**
- `--ufo-root` — UFO 项目根目录，默认 `E:/PY/UFO/ufo`

### `jm-ufo-agent inspect-jingmai-window` — 只读枚举京麦窗口技术事实

枚举京麦窗口的技术属性（窗口句柄、类名、子控件数等），**不点击、不输入**。

```bash
jm-ufo-agent inspect-jingmai-window
```

无额外参数。

### `jm-ufo-agent capture-halt-evidence` — 采集京麦现场 halt 证据

只读采集京麦窗口截图和可选 OCR 结果，用于人工审核或 AI 评审。**不执行点击、输入或保存草稿。**

```bash
# 基础截图采集
jm-ufo-agent capture-halt-evidence --task-id T001 --row-index 82 --node MANUAL_CHECK

# 附带 OCR 识别
jm-ufo-agent capture-halt-evidence --task-id T001 --row-index 82 --node MANUAL_CHECK --use-tesseract

# 自定义证据目录
jm-ufo-agent capture-halt-evidence --task-id T001 --row-index 82 --artifact-dir ./evidence
```

**参数：**
- `--task-id` — 任务 ID（必需）
- `--row-index` — 行号（必需）
- `--node` — 工作流节点名，默认 `MANUAL_CHECK`
- `--reason` — 采集原因，默认 `manual_capture`
- `--artifact-dir` — 证据输出目录，默认 `artifacts`
- `--use-tesseract` — 启用 Tesseract OCR（需 `ocr` 可选依赖）

## Excel 导入命令

### `jm-ufo-agent import-excel` — 解析 xlsx 并导入商品数据

解析 Excel 商品表并输出验收摘要，可选写入 MySQL。

```bash
# 仅解析验收（dry-run）
jm-ufo-agent import-excel --xlsx products.xlsx

# 指定工作表
jm-ufo-agent import-excel --xlsx products.xlsx --sheet-name "Sheet1"

# 写入 MySQL（双重确认）
jm-ufo-agent import-excel --xlsx products.xlsx --write-mysql --confirm-write-mysql --env-file .env
```

**参数：**
- `--xlsx` — Excel 文件路径（必需）
- `--sheet-name` — 工作表名，默认第一个工作表
- `--write-mysql` — 启用 MySQL 写入
- `--confirm-write-mysql` — 确认写入 MySQL（安全门控，需同时指定 `--write-mysql`）
- `--env-file` — 环境配置文件路径，默认 `.env`

## 生产就绪检查命令

### `jm-ufo-agent production-readiness` — 评估生产环境就绪度

根据能力开关评估是否可以启动真实 E2E 流程。

```bash
jm-ufo-agent production-readiness --capabilities-json @capabilities.json
```

**参数：**
- `--capabilities-json` — 能力开关 JSON，支持 `@path.json`（必需）

### `jm-ufo-agent validate-small-batch` — 校验小批量闭环证据

校验 row5-row7 草稿闭环证据，全部通过才允许进入 row82 正式流程。

```bash
jm-ufo-agent validate-small-batch --evidence-json @evidence.json
```

**参数：**
- `--evidence-json` — 闭环证据 JSON，支持 `@path.json`（必需）

## 外部服务预检命令

### `jm-ufo-agent minimax-preflight` — MiniMax API 预检

显式预检 MiniMax-M3 `/models` 端点是否可用。配置从 `.env` 读取，不在命令行暴露 API key。

```bash
jm-ufo-agent minimax-preflight --env-file .env
```

**参数：**
- `--env-file` — 环境配置文件路径，默认 `.env`

### `jm-ufo-agent mysql-preflight` — MySQL schema 预检

只读检查 Excel 导入所需的 MySQL schema 是否就绪，不写入商品数据。

```bash
jm-ufo-agent mysql-preflight --env-file .env
```

**参数：**
- `--env-file` — 环境配置文件路径，默认 `.env`

### `jm-ufo-agent mysql-apply-schema` — 应用 MySQL schema

显式应用 MySQL DDL schema 文件。**该命令会修改数据库结构，必须显式确认。**

```bash
# 预览（不实际执行）
jm-ufo-agent mysql-apply-schema --env-file .env

# 确认执行
jm-ufo-agent mysql-apply-schema --env-file .env --confirm-apply-schema

# 自定义 schema 文件
jm-ufo-agent mysql-apply-schema --env-file .env --schema custom_schema.sql --confirm-apply-schema
```

**参数：**
- `--env-file` — 环境配置文件路径，默认 `.env`
- `--schema` — SQL schema 文件路径，默认 `jm_ufo_agent/storage/schema/mysql.sql`
- `--confirm-apply-schema` — 确认应用 schema（安全门控）

## 配置

配置从 `.env` 文件加载，所有字段都有保守默认值，缺少 `.env` 时也可以运行 dry-run 测试。

### 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `JINGMAI_MYSQL_HOST` | `127.0.0.1` | MySQL 主机 |
| `JINGMAI_MYSQL_PORT` | `3306` | MySQL 端口 |
| `JINGMAI_MYSQL_USER` | `root` | MySQL 用户 |
| `JINGMAI_MYSQL_PASSWORD` | | MySQL 密码 |
| `JINGMAI_MYSQL_DB` | `jingmai_agent` | MySQL 数据库名 |
| `JINGMAI_REDIS_HOST` | `127.0.0.1` | Redis 主机 |
| `JINGMAI_REDIS_PORT` | `6379` | Redis 端口 |
| `JINGMAI_REDIS_PASSWORD` | | Redis 密码 |
| `JINGMAI_MILVUS_HOST` | `127.0.0.1` | Milvus 主机 |
| `JINGMAI_MILVUS_PORT` | `19530` | Milvus 端口 |
| `JINGMAI_LLM_PROVIDER` | `ollama` | LLM 提供商 |
| `JINGMAI_LLM_BASE_URL` | `http://localhost:11434` | LLM API 地址 |
| `JINGMAI_LLM_API_KEY` | `ollama` | LLM API Key |
| `JINGMAI_LLM_MODEL` | `qwen3-vl:8b-instruct` | LLM 模型名 |
| `JINGMAI_REVIEW_SCORER_API_KEY` | | MiniMax API Key |
| `JINGMAI_REVIEW_SCORER_MODEL` | `MiniMax-M3` | 评审模型 |
| `JINGMAI_ARTIFACT_DIR` | `artifacts` | 证据输出目录 |
| `JINGMAI_FORM_COMPLETION_THRESHOLD` | `0.90` | 表单完成阈值 |

### @文件引用

所有 JSON 参数支持 `@path.json` 语法，从文件读取内容而非命令行传入。这对 Windows PowerShell 特别友好，避免引号二次转义问题。

```bash
# 命令行内联 JSON
jm-ufo-agent dry-run --task-id T001 --row-index 5 --product-json '{"title":"商品"}'

# 文件引用（推荐复杂场景）
jm-ufo-agent dry-run --task-id T001 --row-index 5 --product-json @product.json
```

## 安全门控

所有涉及真实京麦窗口、数据库写入、外部 API 调用的操作，都设计了显式确认机制：

| 操作 | 安全门控 | 说明 |
|------|----------|------|
| 真实京麦操作 | `--confirm-real-jingmai` | 防止误操作生产环境 |
| MySQL 数据写入 | `--write-mysql` + `--confirm-write-mysql` | 双重确认，避免误导入 |
| MySQL schema 变更 | `--confirm-apply-schema` | DDL 操作必须显式确认 |
| MiniMax API 调用 | 独立 `minimax-preflight` 命令 | 只在显式调用时才连接 |
| 窗口检查 | 默认 observe-only | inspect/capture 只读，不点击不输入 |

## 输出格式

所有命令输出统一使用 JSON 格式，便于 CI、PowerShell 和人工查看：

```json
{
  "completion_score": 0.85,
  "current_node": "FILL_FORM",
  "row_index": 5,
  "status": "running",
  "task_id": "T001",
  "verified_fields": ["title", "price"],
  "blockers": []
}
```

Dashboard 命令输出 Rich 表格（有 `rich` 依赖时）或纯文本（兜底）。

## 故障排查与边界条件

### 常见错误与降级行为

| 场景 | 触发条件 | 实际行为 | 用户处置 |
|------|----------|----------|----------|
| `--product-json` 传入非法 JSON | JSON 解析失败 | 抛出 `json.JSONDecodeError`，exit code 1 | 检查引号转义或改用 `@file.json` |
| `--product-json` 是数组/字符串 | 传入非 object | 抛出 `ValueError: JSON 参数必须是 object` | 确保顶层是 `{}` |
| `@file.json` 文件不存在 | 路径错误 | 抛出 `FileNotFoundError` | 检查路径和 CWD |
| `@file.json` 含 BOM | Windows `Set-Content` 写入 | 自动用 `utf-8-sig` 解码 | 无需手动处理 |
| `--states-jsonl` 含非 object 行 | 手工拼接或脏数据 | 抛出 `ValueError: JSONL 每行必须是 object` | 清洗 JSONL |
| `rich` 依赖缺失 | 未安装 `[rich-ui]` | Dashboard 自动回落到纯文本（`task_id:` / `status:` 等键值行） | `pip install -e ".[rich-ui]"` 可获得表格 |
| Tesseract 不可用 | 未装 `tesseract-ocr` 系统包 | `--use-tesseract` 在 evidence 中暴露错误，不崩溃 | 装系统包或去掉 `--use-tesseract` |
| MySQL 连接失败 | host/port/密码错误 | preflight 返回 `ok=false` + 错误摘要，exit 1 | 检查 `.env` 中 `JINGMAI_MYSQL_*` 变量 |
| MiniMax API key 缺失 | `.env` 未设 | preflight 返回 auth 错误，**不打印 key** | 编辑 `.env`，不要把 key 写进命令行 |
| 真实京麦窗口未运行 | UFO 启动时找不到窗口 | `run` 命令断言失败并退出 | 先手动启动京麦桌面客户端 |
| `--confirm-real-jingmai` 漏传 | 想操作真实窗口 | `assert_production_allowed` 阻止 | 重新传 `--confirm-real-jingmai`（这是有意的安全门控） |
| `--write-mysql` 单传 `--confirm-write-mysql` | 缺一 | 解析参数时不报错，但 `import-excel` 走 dry-run 分支 | 必须两个开关同时传 |

### Windows PowerShell 特殊处理

```powershell
# ❌ PowerShell 引号会被二次处理
jm-ufo-agent dry-run --product-json '{"title":"x"}'

# ✅ 用 @文件 永远安全
jm-ufo-agent dry-run --product-json @product.json

# ✅ 或用单引号 + 转义
jm-ufo-agent dry-run --product-json '{\"title\":\"x\"}'
```

### 退出码约定

| 退出码 | 含义 |
|--------|------|
| `0` | 成功（包括预检 pass / dry-run 正常返回） |
| `1` | 业务失败（参数非法、依赖缺失、断言失败） |
| `2` | 未知子命令（argparse 默认） |

JSON 输出始终走 `stdout`，错误信息走 `stderr`，便于管道处理。

## 相关资源

### 源码与配置

| 路径 | 用途 |
|------|------|
| `jm_ufo_agent/cli/command.py` | CLI 入口（`argparse` + 子命令分发） |
| `jm_ufo_agent/cli/interactive.py` | 交互式 dashboard 渲染（重导出） |
| `jm_ufo_agent/cli/progress.py` | 进度面板数据模型（重导出） |
| `jm_ufo_agent/runtime/app.py` | dry-run 实际工作流 |
| `jm_ufo_agent/runtime/production.py` | 生产断言 `assert_production_allowed` |
| `jm_ufo_agent/core/settings.py` | `.env` 加载 + 强类型配置对象 |
| `jm_ufo_agent/storage/schema/mysql.sql` | MySQL DDL（默认被 `mysql-apply-schema` 应用） |
| `pyproject.toml` | 依赖与 `[project.scripts]` 入口声明 |

### MySQL Schema 关键表

`storage/schema/mysql.sql` 主要包含：

| 表名 | 用途 | 关键字段 |
|------|------|----------|
| `products` | 商品主表 | `id`, `sku`, `title`, `price`, `status`, `created_at` |
| `product_drafts` | 工作流中间态 | `task_id`, `row_index`, `node`, `payload_json` |
| `halt_evidence` | 现场证据归档 | `task_id`, `row_index`, `screenshot_path`, `ocr_text` |
| `review_scores` | MiniMax 评审结果 | `task_id`, `score`, `dimension`, `reasoning` |

> ⚠️ 字段为高层摘要，apply 之前请直接查阅 SQL 文件确认列定义。

### 相关 Skill / 项目

- **`opc-cli`** — OPC 兄弟项目（语音工具），本 SKILL.md 风格参考来源
- **`gstack/browse`** — 桌面浏览器自动化（与 UFO 共用底座）
- **`darwin-skill`** — 用于本 SKILL.md 的评分与持续优化
- **`MiniMax-M3`** — 需求评审模型（评审维度 8 实测表现）

### 内部依赖（pyproject.toml）

| extras | 包含 | 何时需要 |
|--------|------|----------|
| `storage` | `asyncmy`, `redis`, `pymilvus` | `import-excel --write-mysql` / Milvus 经验库 |
| `ocr` | `Pillow`, `pytesseract` | `capture-halt-evidence --use-tesseract` |
| `rich-ui` | `rich>=13.0.0` | `dashboard` / `tail-dashboard --rich-live` 表格输出 |
| `test` | `pytest`, `pytest-asyncio` | `poetry run pytest` |
| `all` | 上述全部 | 一键装齐 |

## 实战经验 / 避坑指南

实战沉淀（2026-06-08 ~ 2026-06-09 京麦真实保存草稿）。详见 `docs/live-operations/` 目录的 5 篇 runbook。

### 真实操作的硬边界

- **只允许保存草稿，禁止点击 `发布商品`**。底部按钮区左 `x≈1315` 是发布，右 `x≈1424` 是草稿，自动化把发布区域视为禁区。
- **不能把"点击了"当成"成功了"**。每个关键动作后必须截图或读回验证。
- **WebView 内部 HTML 控件不假设 UIA/DOM/CDP 可用**。原生层（UFO/UIA/Win32/WinCOM）优先；WebView 走截图/OCR/坐标/剪贴板 fallback。
- **运行前校验前台窗口**：`GetForegroundWindow()` 检查标题含 `jd_465d1abd3ee76`，不是京麦立即停止。
- **真实进度只看 `data/live_runs/jingmai_autonomous_state.json`**，不看 `data/breakpoints`（断点可能来自 dry-run，不能证明真实草稿已保存）。

### 字段操作高频坑

| 卡壳现象 | 真实原因 | 修复动作 |
|----------|----------|----------|
| 找不到 `+发布商品` | WebView 不暴露 UIA | 截图后用坐标 fallback（按分辨率） |
| 类目搜索词是纯数字 | 把 Excel `category_id` 当关键词 | 用标题词典推断；Excel 增加 `category_keyword` 列 |
| 输入类目后下一步不可用 | 只搜索未选中结果 | 点结果行让 `已选类目` 出现，再下一步 |
| 图文详情报 `高级编辑内容为空` | 没维护文本层 | 切 `图文编辑` → `添加文本` → 下方输入框粘贴文案；验证 `已添加 1/50张` |
| 下拉看似输入但未选中 | Ant/CEF 下拉 `Ctrl+V+Enter` 不一定选 | 点下拉 → 粘贴 → 截图候选项 → 点候选项 → 截图确认 |
| `电线长度` 等无 Excel 真实值 | 平台枚举范围有限 | 走平台枚举（用户授权），真实值写进标题/详情，冲突留痕 |
| 危险品字段乱勾 | 弹出危险类型多选 | 不为消红星乱选；让平台校验决定 |
| SKU 图片无文件框 | 走京麦图片空间，非系统文件框 | SKU `+ 添加` → `本地上传` → 文件框出现再粘路径 |
| 找不到 SKU 尺寸/重量字段 | 表格横向滚动条隐藏 | 拖横向滚动条到尺寸/重量列 |
| 保存后不知道成功 | 没建立成功判定 | 回草稿箱核对：标题匹配 + 编辑时间为本次运行时间 |

### Verified Action Ladder（WebView 字段必走）

L1 Native（UIA/Win32/WinCOM 控件定位 + `set_edit_text`）→ L2 WebView（坐标 + 剪贴板粘贴 + focused-text 读回）→ L3 UFO-style（`set_text`/`type_keys`/剪贴板三连，参考 `E:\PY\UFO\ufo` 模式）。只有 verified action 报告成功才能标记 `FILLED`；否则截图到 `data/screenshots/verify_*` 留证，workflow 不能 set `FILLED`。

### 实战文档索引

| 文档 | 主题 |
|------|------|
| `2026-06-08-jingmai-product-publish-live-runbook.md` | row4 草稿全流程 + 坐标 fallback（2560x1440 验证） |
| `2026-06-08-jingmai-verified-actions.md` | Verified Action Ladder + 字段配置 fallback_coord 范式 |
| `2026-06-09-jingmai-live-skill-practice-training.md` | row5/6/7 复盘 + 6 个避坑 + 平台枚举 vs Excel 字面值 |
| `2026-06-09-autonomous-save-draft-workflow.md` | 自主循环 Observe→Decide→Act→Verify→Record + 中止条件 |

