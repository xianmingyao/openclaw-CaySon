# jingmai-agent - 京麦智能体自动化系统

**描述:** 京麦商家后台桌面自动化 CLI 工具，支持 UIA 控件交互、CEF 混合页面适配、多级类目联动、商品全流程自动发布。集成 RAG 知识库、记忆管理和可执行 Skill 注册机制。
**架构:** Processor + Strategy + MiddlewareChain 三层解耦，UFO Agent 调度。

## 环境安装（uv 管理）

本项目使用 uv 管理依赖。

```bash
# 安装 uv（如果还没有）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装依赖
cd jingmai-cli
uv sync

# 后续所有命令通过 uv run 执行
uv run python cli.py --help
```

首次运行需要配置 `.env` 文件（参考 `config.py` 中的环境变量）。

## 快速开始

```bash
# 查看系统状态
uv run python cli.py status

# 初始化服务后查看状态
uv run python cli.py status -i

# 运行单个任务
uv run python cli.py run "打开京麦并发布商品"

# 进入交互式模式
uv run python cli.py interactive

# 批量执行任务
uv run python cli.py batch tasks.txt
```

## 命令总览

| 命令 | 说明 |
|------|------|
| `jingmai run` | 运行单个任务 |
| `jingmai interactive` | 交互式 REPL 模式 |
| `jingmai batch` | 批量执行任务 |
| `jingmai status` | 查看系统状态 |
| `jingmai memory` | 记忆管理（子命令组） |
| `jingmai rag` | RAG 知识库（子命令组） |
| `jingmai skills` | 技能管理（子命令组） |

---

## 核心命令

### `jingmai run <description>` — 运行单个任务

```bash
# 基础用法
uv run python cli.py run "打开记事本并输入Hello World"

# 指定任务标题、复杂度、优先级
uv run python cli.py run "整理桌面文件" -t "文件整理" -c simple -p 3

# 指定 Agent 类型和最大步数
uv run python cli.py run "京麦商品发布" -a ufo_agent -s 30
```

**参数：**

| 参数 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--title` | `-t` | 任务描述前50字 | 任务标题 |
| `--complexity` | `-c` | `medium` | 任务复杂度：`simple` / `medium` / `complex` |
| `--priority` | `-p` | `5` | 任务优先级 (1-10) |
| `--agent` | `-a` | `ufo_agent` | Agent 类型：`ufo_agent` / `rag_agent` / `planner_agent` |
| `--max-steps` | `-s` | `20` | 最大执行步数 |

### `jingmai interactive` — 交互式模式

```bash
# 默认使用 ufo_agent
uv run python cli.py interactive

# 指定 Agent
uv run python cli.py interactive -a rag_agent
```

输入 `exit` 或 `quit` 退出。每行输入作为一个任务执行。

**参数：**

| 参数 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--agent` | `-a` | `ufo_agent` | 默认 Agent 类型 |

### `jingmai batch [file]` — 批量执行任务

```bash
# 从文本文件读取（每行一个任务）
uv run python cli.py batch tasks.txt

# 从 JSON 文件读取
uv run python cli.py batch -f json tasks.json

# 从 CSV 文件读取
uv run python cli.py batch -f csv tasks.csv

# 从标准输入读取
echo -e "任务1\n任务2\n任务3" | uv run python cli.py batch
```

**文件格式：**

- **txt**：每行一个任务描述
- **json**：数组格式，每项含 `title`、`description`、`complexity`、`priority`、`agent` 字段
- **csv**：标准 CSV，含表头

**参数：**

| 参数 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--format` | `-f` | `txt` | 文件格式：`json` / `txt` / `csv` |

### `jingmai status` — 查看系统状态

```bash
# 基础状态检查
uv run python cli.py status

# 详细模式（含任务统计）
uv run python cli.py status -v

# JSON 格式输出
uv run python cli.py status --json

# 初始化所有服务后检查
uv run python cli.py status -i
```

检查的服务项：数据库、Redis、Milvus（可选）、LLM 服务、向量存储（可选）、OSS 存储（可选）、记忆管理、RAG 服务、技能注册表。

**参数：**

| 参数 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--verbose` | `-v` | 否 | 显示详细信息和任务统计 |
| `--json` | `-j` | 否 | 以 JSON 格式输出 |
| `--init` | `-i` | 否 | 初始化所有服务后再检查 |

---

## 记忆管理（memory）

### `jingmai memory create <content>` — 创建记忆

```bash
uv run python cli.py memory create "京麦窗口标题是xxx" -t short -p high -g jingmai -g window
```

**参数：**

| 参数 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--type` | `-t` | `short` | 记忆类型：`short` / `long` / `working` |
| `--key` | `-k` | 无 | 记忆键 |
| `--priority` | `-p` | `medium` | 优先级：`low` / `medium` / `high` / `critical` |
| `--tags` | `-g` | 无 | 标签（可多次使用） |
| `--ttl` | 无 | 无 | 过期时间（秒） |

### `jingmai memory search <query>` — 搜索记忆

```bash
uv run python cli.py memory search "京麦窗口" -k 10 -g jingmai
```

**参数：**

| 参数 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--type` | `-t` | 无 | 按记忆类型过滤 |
| `--top-k` | `-k` | `5` | 返回结果数量 |
| `--tags` | `-g` | 无 | 按标签过滤 |

### `jingmai memory stats` — 记忆统计

```bash
uv run python cli.py memory stats
```

### `jingmai memory clear` — 清空记忆

```bash
uv run python cli.py memory clear -t working
```

---

## RAG 知识库（rag）

### `jingmai rag query <query>` — 查询知识库

```bash
uv run python cli.py rag query "如何发布京麦商品" -k 5 -r
```

**参数：**

| 参数 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--top-k` | `-k` | `5` | 返回结果数量 |
| `--rerank` | `-r` | 否 | 启用重排序 |

### `jingmai rag stats` — 知识库统计

```bash
uv run python cli.py rag stats
```

---

## 技能管理（skills）

### `jingmai skills list` — 列出可用技能

```bash
uv run python cli.py skills list
uv run python cli.py skills list -c automation -v
```

**参数：**

| 参数 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--category` | `-c` | 无 | 按类别筛选 |
| `--verbose` | `-v` | 否 | 显示详细信息（描述、动作列表） |

### `jingmai skills search <query>` — 搜索技能

```bash
uv run python cli.py skills search "商品发布" -k 5
```

**参数：**

| 参数 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--top-k` | `-k` | `5` | 返回结果数量 |

---

## 可执行 Skill（jingmai_product_publish）

系统内置 `jingmai_product_publish` Skill，命中关键词后自动由 `SkillAwareUFOAgent` 走 `run_skill` 执行。

**命中关键词：** `jingmai-product-publish`、`京麦商品发布`、`京麦上架`、`京麦发布`、`jingmai product publish`

**运行流程：**

```
任务描述 → 关键词匹配 → SkillAwareUFOAgent.run_skill()
                         ↓
                    SkillRuntimeBridge.execute_skill()
                         ↓
                    scripts/run_skill.py（子进程）
                         ↓
                    jingmai_processor.py（外部 Processor）
                         ↓
                    生成 phase_trace.json + artifacts
```

**输出资产：**

| 文件 | 说明 |
|------|------|
| `artifacts/<id>/phase_trace.json` | 阶段轨迹（phase / action / screenshot / result / status） |
| `artifacts/<id>/runtime_result.json` | 运行结果摘要 |
| `artifacts/<id>/stdout.log` | 标准输出日志 |
| `artifacts/<id>/stderr.log` | 错误输出日志 |

---

## 架构设计

```
┌──────────────────────────────────────────────────────────┐
│                   CLI (click)                             │
│  run | interactive | batch | status | memory | rag       │
│             | skills                                      │
├──────────────────────────────────────────────────────────┤
│                   Service Layer                           │
│  ┌────────────┐  ┌────────────┐  ┌──────────────────┐    │
│  │ AgentFactory│  │MemoryManager│  │   RAG Service   │    │
│  │  ufo_agent  │  │ short/long/ │  │ query / stats   │    │
│  │  rag_agent  │  │ working     │  │                  │    │
│  │  planner    │  │             │  │                  │    │
│  └──────┬─────┘  └────────────┘  └──────────────────┘    │
│         │                                                 │
│  ┌──────▼─────────────────────────────────────────────┐  │
│  │              SkillRuntimeBridge                     │  │
│  │  match → execute(run_skill.py) → trace → result    │  │
│  └────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────┤
│                   Infrastructure                          │
│  MySQL │ Redis │ Milvus │ LLM (Ollama) │ OSS            │
└──────────────────────────────────────────────────────────┘
```

---

## Session 隔离

当 jingmai-cli 在 Session 0（Windows 服务 / SSH）运行时，`pyautogui` 无法操作 Session 1（远程桌面）的京麦 GUI。

系统提供三层 Session 对齐机制：

```
Layer 1: CLI 入口检查
    cli() → _ensure_interactive_session()
    如果当前在 Session 0 → 尝试迁移到交互式 Session

Layer 2: Agent 执行前检查
    UFOAgent.execute() → _ensure_session_alignment()
    检查京麦进程所在 Session → 必要时启动京麦到当前 Session

Layer 3: 配置控制
    SESSION_MODE=auto      → 自动检测，迁移失败仅 warning（默认）
    SESSION_MODE=force_same → 强制要求同 Session，否则报错
    SESSION_MODE=manual    → 不做任何 Session 检查
```

**推荐用法：** 在远程桌面终端（Session 1）运行 jingmai-cli，确保与京麦在同一 Session。

---

## 关键配置

配置文件：`.env`（参考 `config.py`）

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `LLM_PROVIDER` | `ollama` | LLM 提供者 |
| `LLM_MODEL` | `qwen3-vl:32b` | 默认模型 |
| `LLM_BASE_URL` | `http://localhost:11434` | LLM 服务地址 |
| `DATABASE_TYPE` | `mysql` | 数据库类型（mysql / sqlite） |
| `MYSQL_HOST` | `localhost` | MySQL 地址 |
| `MYSQL_DATABASE` | `jingmai_agent` | 数据库名 |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis 连接地址 |
| `MILVUS_HOST` | `localhost` | Milvus 地址 |
| `MAX_TASK_STEPS` | `20` | 任务最大执行步数 |
| `TASK_TIMEOUT` | `600` | 任务超时时间（秒） |
| `AGENT_MAX_EXECUTION_TIME` | `300` | Agent 最大执行时间（秒） |
| `SCREENSHOT_ENABLED` | `True` | 是否启用截图 |
| `SKILL_EXTRA_DIRS` | 空 | 额外 Skill 搜索目录 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `SESSION_MODE` | `auto` | Session 检测模式：`auto` 自动检测 / `force_same` 强制同 Session / `manual` 不检查 |
| `TARGET_APP_PROCESS` | `Jingmai.exe` | 目标应用进程名（用于 Session 检测） |
