---
name: jingmai-product-publish
description: |
  京麦商品发布自动化技能。做什么：通过 Windows 桌面自动化完成京麦客户端商品发布、草稿保存、Excel批量导入、京东商品抓取、任务跟踪。何时用：用户提到「京麦发布」「批量上架」「jingmai」时触发。uv 管理依赖，一条命令安装。
---

## 触发词

- 京麦发布 / jingmai publish / jingmai / 京麦自动化 / 批量上架

## 对话式工作流

> Agent 根据用户意图匹配执行路径。每个箭头表示一个阶段，完成后暂停等待确认。

```
用户："帮我设置京麦环境"
  └─→ [1] 检查 uv → 安装依赖 → 安装 Chromium → check-config
       → 展示配置摘要 → ⏸ 用户确认
       → [2] init-db → ⏸ 用户确认数据库类型
       → ✅ 环境就绪

用户："导入这个 Excel 到京麦草稿"
  └─→ [1] 确认环境已就绪（否则先走上面流程）
       → [2] 读取 Excel → 展示商品摘要（数量/类目/耗时）→ ⏸ 用户确认
       → [3] run-import --mode draft → 实时进度 → ✅ 导入完成

用户："把草稿正式发布"
  └─→ [1] 展示待发布商品摘要 → ⏸ 用户输入 yes 确认
       → [2] run-desktop-check --step t8-publish-product --confirm-publish
       → [3] check-evidence 展示截图证据 → ✅ 发布完成

用户："京麦出问题了 / 报错了 / 没反应"
  └─→ [1] 收集症状 → 匹配「故障排查」表
       → [2] 按优先级尝试解决方案 → 每步验证 → ✅ 问题解决或升级
```

## 快速开始

### 环境安装（uv 管理）

| 步骤 | 命令 | 说明 |
|------|------|------|
| 1. 安装 uv | `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` | 仅首次需要；已有 uv 则跳过 |
| 2. 安装依赖 | `uv sync --dev` | 自动创建 `.venv`，安装所有依赖 |
| 3. 安装浏览器 | `uv run playwright install chromium` | Playwright 需要 Chromium 浏览器 |
| 4. 验证安装 | `uv run jingmai-publish check-config --root .` | 确认环境配置正确 |

```bash
# 完整安装流程（在项目目录执行）
cd E:\workspace\skills\jingmai-product-publish

# 步骤1：安装 uv（如果还没有）
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 步骤2：安装所有依赖
uv sync --dev

# 步骤3：安装 Playwright 浏览器
uv run playwright install chromium

# 步骤4：验证安装
uv run jingmai-publish check-config --root .
```

**环境要求：**
- Windows 10/11
- 已安装并登录京麦客户端
- 建议分辨率 `2560x1392`

## 配置

项目通过 `.env` 文件管理配置。首次使用前需在项目根目录创建 `.env` 文件：

```bash
# 必填：MySQL 连接（脚本会自动降级到 SQLite，可不填）
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=jingmai_agent

# 可选：飞书集成
# FEISHU_APP_ID=
# FEISHU_APP_SECRET=

# 可选：Ollama Vision（截图分析用）
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=qwen3-vl:8b
```

配置验证通过后，初始化数据库：

```bash
uv run jingmai-publish init-db --root .
```

## CLI 命令

> 所有命令均通过 `uv run jingmai-publish <子命令>` 执行。也可用 `python cli.py <子命令>` 在已激活的 venv 中运行。

### 环境检查

```bash
uv run jingmai-publish check-config --root .
```

### 初始化数据库

```bash
uv run jingmai-publish init-db --root .
```

### 导入商品（草稿模式）

```bash
uv run jingmai-publish run-import --excel ".\湖南上架表格.xlsx" --mode draft --root .
```

### 桌面执行检查

```bash
uv run jingmai-publish run-desktop-check --step both --debug --root .
```

### 正式发布（有人工守卫）

```bash
uv run jingmai-publish run-desktop-check --step t8-publish-product --confirm-publish --root .
```

### 检查证据

```bash
uv run jingmai-publish check-evidence --root .
```

### 清理运行时日志

```bash
uv run jingmai-publish cleanup-runtime-logs --root .
```

## 执行模型

```
Plan-and-Solve（文档驱动规划）
  └─ 解析京麦上架流程.docx正文 → 生成带workflow元数据的步骤
        ↓
ReAct（每步完整循环）
  └─ Precheck(截图预检) → Act(执行动作) → Screenshot(截图) → Observe(LLM视觉分析) → Postcheck(截图复核)
        ↓
Reflection（递进式重试，最多3次）
```

**关键设计：**
- **Precheck + Postcheck** — 执行前后截图对比，偏差自动恢复
- **页面态恢复策略** — 覆盖登录/商品列表/类目/商品信息/规格/发布确认 6 种页面
- **发布守卫** — `t8-publish-product` 步骤需 `--confirm-publish` 明确授权，防止误发布
- **自动降级** — MySQL 连接失败自动切换到 SQLite

## 检查点（Checkpoints）

> 每个关键操作前 Agent 必须暂停，等待用户确认后再继续。不可自主跳过。

| 阶段 | 检查点 | 确认方式 | 不通过时 |
|------|--------|---------|---------|
| 环境初始化 | `check-config` 通过后，展示配置摘要 | 用户确认"环境OK" | 修正 `.env` 后重新验证 |
| 数据库初始化 | `init-db` 执行前，确认数据库类型（MySQL/SQLite） | 用户确认"初始化" | 检查数据库连接后重试 |
| Excel 导入 | 读取 Excel 后展示：商品数量、类目分布、预计耗时 | 用户确认"开始导入" | 修正 Excel 数据后重新读取 |
| 正式发布 | 展示待发布商品摘要（数量/类目/价格区间） | 用户输入 `yes` 或传 `--confirm-publish` | 返回草稿模式，不执行发布 |
| 批量操作 | 展示操作计划（步骤数/预计耗时/风险点） | 用户确认"执行" | 调整参数后重新规划 |

## 调试选项

```bash
--verbose          # 详细输出
--log-file logs/cli-debug.log  # 日志文件
```

## Session1 Helper

京麦客户端运行在 Session 1（用户桌面会话），而脚本运行在 Session 0（服务会话）或其他非交互会话时，发出的操作无法传递到京麦窗口。

> **为什么有两个目录？** `jingmai-product-publish`（本目录）是发布主流程，`jingmai-product-publish-v2`（Session1 Helper 所在目录）负责桌面自动化桥接。两个项目配合使用，缺一不可。

**启动 Helper：**
```bash
# 在 Session1 Helper 项目目录执行（注意：是 v2 目录）
cd E:\workspace\skills\jingmai-product-publish-v2
uv run python session1_helper.py
# 或双击 start_helper.bat
```

**验证 Helper 是否运行：**
```bash
# 回到主项目目录
cd E:\workspace\skills\jingmai-product-publish
uv run jingmai-publish run-desktop-check --step t1-login-check --root .
# 如果能截到京麦窗口 → Helper 正常工作
```

## 故障排查

| 症状 | 可能原因 | 解决方案 |
|------|---------|---------|
| `uv` 命令不存在 | uv 未安装 | 执行步骤1安装 uv，或 `pip install uv` |
| `uv sync` 失败 | Python < 3.12 | 安装 Python 3.12+，推荐 `winget install Python.Python.3.12` |
| `playwright install` 失败 | 网络问题或权限不足 | 管理员 PowerShell 重试；配置代理后重试 |
| `check-config` 输出 `success: false` | 配置缺失或不合法 | 检查 `.env` 文件是否存在、MYSQL_PORT 范围、REDIS_URL/OLLAMA_BASE_URL 格式 |
| 数据库初始化失败 | MySQL 连接不上 | 检查 `MYSQL_*` 环境变量；脚本会自动降级到 SQLite，可留空 |
| 桌面操作无响应 | Session1 Helper 未启动 | 双击 `start_helper.bat` 或在 v2 目录运行 `uv run python session1_helper.py` |
| 京麦窗口未找到 | 京麦未登录或窗口标题不匹配 | 确认京麦客户端已登录并显示在主桌面 |
| 截图分析超时 | Ollama 未启动或显存不足 | 确认 `ollama serve` 运行中，检查 `OLLAMA_BASE_URL` 配置 |
| Excel 导入报错 | 表头不匹配或数据格式异常 | 对照模板检查列名（商品名称/价格/库存/类目/规格/图片）；确保无合并单元格 |
| Excel 导入0条 | 工作表为空或数据不在第一个 sheet | 确认数据在第一个工作表，且从第2行开始（第1行为表头） |
| UIA 元素找不到 | 京麦版本更新导致元素路径变化 | 运行 `run-desktop-check --step t1-login-check --debug` 生成最新截图，比对元素定位 |
| 发布后商品未显示 | 京东审核延迟 | 等待 5-10 分钟刷新；检查「待审核」tab；非报错，属正常流程 |
| 批量导入中途卡住 | 某个商品数据异常导致流程中断 | 查看 `logs/` 目录下的错误日志，定位失败商品行号，修正后单独导入 |
| 京麦客户端闪退 | 京麦自身稳定性问题 | 重新登录京麦；运行 `check-config` 确认环境；从断点续传（已导入商品不会重复） |
| 分辨率不匹配 | 非 2560×1392 导致坐标偏移 | 调整分辨率至推荐值；或在 `.env` 中设置 `SCREEN_WIDTH`/`SCREEN_HEIGHT` 覆盖默认坐标 |

## 项目文件

| 文件 | 用途 |
|------|------|
| `pyproject.toml` | 项目元数据、依赖声明、CLI 入口点 |
| `.env` | 运行时配置（需自行创建，参考上方「配置」章节） |
| `uv.lock` | 依赖版本锁定文件（`uv sync` 自动生成） |
| `jingmai_publish/cli.py` | CLI 命令入口（`jingmai-publish` → `cli:main`） |
| `jingmai_publish/config.py` | 配置加载与校验逻辑 |
| `jingmai_publish/bootstrap.py` | 数据库初始化逻辑 |
| `jingmai_publish/services/` | 核心业务服务（导入、发布、证据等） |
| `jingmai_publish/agent/` | Agent 执行引擎（Planner/Executor/Reflection） |
| `jingmai_publish/desktop/` | 桌面自动化适配层（UIA/Win32） |
| `logs/` | 运行日志（`--log-file` 可指定路径） |
| `resources/screenshots/` | 截图证据目录 |
