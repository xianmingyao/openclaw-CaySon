---
name: jingmai-product-publish
description: |
  京麦商品发布自动化技能，面向 Windows 环境下的京麦客户端商品发布、草稿保存、批量导入、商品抓取、任务跟踪与记忆管理。
---

# jingmai-product-publish

京麦商品发布自动化技能，面向 Windows 环境下的京麦客户端商品发布、草稿保存、批量导入、商品抓取、任务跟踪与记忆管理。

## 触发词

- 京麦发布
- jingmai publish
- jingmai
- 京麦自动化
- 批量上架

## 环境安装（uv 管理）

本项目使用 uv 管理依赖，4 步完成安装。

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

## v2 相对于 v1 的改进

1. **文档驱动规划**：先解析 `京麦上架流程.docx` 正文段落，再从真实段落生成步骤
2. **Precheck + Postcheck**：执行前截图预检，执行后截图复核
3. **偏差恢复矩阵**：按偏差类型执行恢复动作（recover_locator / force_relocate / navigate_to / select_category / wait）
4. **页面态细分恢复策略**：覆盖登录页 / 商品列表页 / 类目页 / 商品信息页 / 规格描述页 / 发布确认页
5. **Session1 Helper**：在用户桌面 Session 运行 Win32 操作，解决 Session 0 无法操作京麦的问题
6. **MySQL 持久化**：支持 `MYSQL_HOST / MYSQL_PORT / MYSQL_USER / MYSQL_PASSWORD / MYSQL_DATABASE` 自动拼接连接
7. **批量场景分治**：通过 `publish_mode` 区分 single / batch

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

## 调试选项

```bash
--verbose          # 详细输出
--log-file logs/cli-debug.log  # 日志文件
```

## Session1 Helper

京麦客户端运行在 Session 1，而脚本运行在 Session 0。Session 0 发出的操作无法传递到 Session 1 的京麦窗口。

**启动 Helper：**
```bash
cd E:\workspace\skills\jingmai-product-publish-v2
uv run python session1_helper.py
# 或双击 start_helper.bat
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
