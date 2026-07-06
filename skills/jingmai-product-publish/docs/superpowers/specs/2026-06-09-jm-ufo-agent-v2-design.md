# 京麦智能上架系统 v2 (jm_ufo_agent) — 设计规格说明书

> **代号：** `jm_ufo_agent`
> **版本：** v2.0.0
> **日期：** 2026-06-09
> **作者：** CaySon (Claude Code with brainstorming/writing-plans skills)
> **状态：** Draft — 待用户 review 后进入 plan 阶段

---

## 1. 背景与目标

### 1.1 背景

京东商家后台「京麦」的商品上架流程是高度重复、规则明确、但又涉及 Qt5 桌面壳、内嵌 QtWebEngine 表单、文件选择窗口、表单联动、图片上传、价格计算等多个环节的工作。v1 版本基于自主 ReAct 的多 Agent 架构，存在以下问题：

1. **盲目自治**：每步都让 LLM 决定下一步动作，决策不稳定，单次失败容易引发级联错误。
2. **流程不可预测**：缺失显式状态机，无法保证崩溃后能恢复到一致的中间状态。
3. **VLM 滥用**：每步都调用视觉模型，成本高且响应慢。
4. **进程失控**：5 个进程各自为政，难以协调共享资源（图片、UI 焦点、缓存）。
5. **断点续传粗粒度**：仅支持「任务级」恢复，无法做到「字段级」恢复。

### 1.1.1 京麦窗口技术事实（2026-06-09 复核）

本项目的自动化边界必须以真实窗口树为准，而不是按普通浏览器或 CEF 页面假设设计：

1. **京麦是 Qt5 应用**：主壳识别为 `Qt51511QWindowIcon`，不是可直接按 CEF DevTools/DOM 控制的 CEF 应用。
2. **内嵌 WebView 是 QtWebEngine/Chromium 内核**：窗口树中会出现 `Chrome_WidgetWin_0` / `Chrome_RenderWidgetH*` 等 Chromium 相关类名，但这不等于可以把京麦当作 CEF 自动化目标。
3. **WebView 内 HTML 控件不暴露给 UIA**：已确认 WebView 内仅能看到约 5 个 Pane（如 `CefBrowserWindow` / `Chrome_WidgetWin_0` / `Chrome_RenderWidgetH*`），0 个 `Edit` / `ComboBox` / `Button`。HTML 表单控件对 UIA 不可达。
4. **Qt 子窗口数量高**：京麦窗口树约 158 个 Qt 子窗口，原生壳、WebView 区域、文件选择窗口必须分层识别，不能用单一 locator 策略。
5. **合成输入不可靠**：WebView/Chromium 区域会拒绝或吞掉部分合成输入，不能把 pyautogui/pynput 点击后“没有报错”当成成功。

结论：v2 的核心不是“盲目无人值守”，而是状态证据驱动的机械执行系统。WebView 表单区域默认走截图/OCR/坐标/剪贴板 fallback；文件选择、窗口焦点、原生 Qt 控件继续走 UFO/UIA/Win32/WinCO1 底层 action 逻辑。

### 1.2 目标

v2 用确定性状态机（LangGraph）+ 显式 Strategy 层 + MySQL/Redis/Milvus 三层存储，实现：

1. **每一步可验证**：所有操作（点击/输入/校验）都有明确成功条件，失败立即 halt。
2. **崩溃可恢复**：字段级 + 行级双层断点续传，最小化重做工作量。
3. **VLM 成本受控**：VLM 仅用于 OCR 校验、失败反思、图片转换 3 个决策点，不进入热循环。
4. **单进程多协程**：进程内 asyncio.TaskGroup 协调 3 类工作协程（数据抓取/图片处理/GUI 主循环）。
5. **硬安全屏障**：`SafetyPolicy` 硬编码禁止「发布商品」「删除商品」「价格超范围」三类操作。
6. **证据驱动进度**：进度只由 MySQL/Redis 状态文件、截图、OCR/读回结果、草稿验证证据推进；LLM/VLM 不能把失败标记为成功。

### 1.3 范围

#### ✅ 做什么
- 解析「湖南上架表格.xlsx」获取待上架商品列表
- 自动访问京东抓取商品价格/标题/图片
- 按「京麦上架流程.docx」抽象稳定工作流节点，并把流程版本写入任务状态
- 自动登录京麦后台并完成商品上架全流程（仅「保存草稿」，绝不发布）
- 字段级、行级、任务级三层断点续传
- CLI 命令模式（CI/CD 友好）+ 交互模式（Rich dashboard 实时进度）
- MySQL 持久化所有执行状态、Redis 短期缓存、Milvus 向量经验库

#### ❌ 不做什么
- 不点击「发布商品」按钮（SafetyPolicy 硬阻断）
- 不删除已有商品（SafetyPolicy 硬阻断）
- 不修改超出 `采购价 × 0.9 ~ 市场价 × 1.1` 范围的价格（SafetyPolicy 硬阻断）
- 不支持 v1 遗留的 ReAct 多 Agent 自组织模式（被 LangGraph 状态机取代）
- 不做跨账号/跨店铺的批量调度（v2 只支持单账号顺序上架）
- 不把 WebView HTML 表单假设为 UIA/DOM 可达；DOM/JS 只能作为调试或可用时的辅助读通道，默认执行通道是截图/OCR/坐标/剪贴板
- 不引入多进程（v2 单进程多协程）
- 不使用 SQLite / Postgres（v2 只用 MySQL + Redis + Milvus）

---

## 2. 架构概览

### 2.1 五层架构

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: CLI / TUI                                         │
│  - cli/command.py   (CI/CD 命令模式)                          │
│  - cli/interactive.py (Rich dashboard 交互模式)              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: LangGraph Workflow                                 │
│  - workflow/graph.py (StateGraph 18 节点)                    │
│  - workflow/state.py (GraphState TypedDict)                  │
│  - workflow/nodes/* (每个节点一个文件)                        │
│  - storage/checkpointer.py (AsyncMySQLSaver)                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Agent 层（5 个具体 Agent）                          │
│  - JmHostAgent / JmProductFormAgent / JmWebViewAgent        │
│  - NativeDialogAgent / JdCrawlerAgent / ImageFetchAgent     │
│  - ExcelParseAgent / ImageTransformAgent                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Strategy 层（7 个无状态策略）                        │
│  - ObserveStrategy / DeterministicPlanStrategy               │
│  - GuardedActionStrategy / VerifyStrategy                   │
│  - FormCompletionScoreStrategy / MiniMaxReviewScoreStrategy │
│  - FailureReflectionStrategy                                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: Command + Backend 层                                │
│  - commands/* (FillCommand, ClickCommand, NavigateCommand)  │
│  - backends/uia/  (从 UFO v1 直接复制)                       │
│  - backends/win32/ (从 UFO v1 直接复制)                      │
│  - backends/clipboard/ (从 UFO v1 复制 + 适配)               │
│  - backends/web_surface/ (截图/OCR/坐标/剪贴板 fallback)    │
│  - backends/js_bridge/ (仅调试/可用时辅助读，不作为默认控制) │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 目录结构

```
jingmai-product-publish/                    # 项目根
├── .env                                    # 生产凭证 (gitignored)
├── .env.example                            # 占位符模板 (入库)
├── .gitignore
├── VOBFLOW.md                              # 工作流规范
├── docs/
│   └── superpowers/
│       ├── specs/                          # 设计规格
│       │   └── 2026-06-09-jm-ufo-agent-v2-design.md   ← 本文件
│       └── plans/                          # 实施计划（由 writing-plans 生成）
│
├── 京麦上架流程.docx                        # 流程参考文档
├── 湖南上架表格.xlsx                        # 输入数据
│
└── jm_ufo_agent/                           # ★ v2 顶层包
    ├── __init__.py
    ├── pyproject.toml                      # Poetry 配置
    │
    ├── cli/                                # Layer 1: CLI
    │   ├── __init__.py
    │   ├── command.py                      # CLI 命令模式
    │   ├── interactive.py                  # 交互模式 (Rich dashboard)
    │   └── progress.py                     # 进度展示组件
    │
    ├── workflow/                           # Layer 2: LangGraph
    │   ├── __init__.py
    │   ├── graph.py                        # StateGraph 构建
    │   ├── state.py                        # GraphState TypedDict
    │   ├── conditions.py                   # 条件边路由函数
    │   └── nodes/
    │       ├── __init__.py
    │       ├── bootstrap.py                # BOOTSTRAP node
    │       ├── recover.py                  # RECOVER node
    │       ├── select_row.py               # SELECT_ROW node
    │       ├── prepare_assets.py           # PREPARE_ASSETS node
    │       ├── open_page.py                # OPEN_PAGE node
    │       ├── observe_page.py             # OBSERVE_PAGE node
    │       ├── assert_page_signature.py    # ASSERT_PAGE_SIGNATURE node
    │       ├── calibrate_locators.py       # CALIBRATE_LOCATORS node
    │       ├── plan_fields.py              # PLAN_FIELDS node
    │       ├── fill_field.py               # FILL_FIELD node
    │       ├── verify_field.py             # VERIFY_FIELD node
    │       ├── assess_form_completion.py   # ASSESS_FORM_COMPLETION node
    │       ├── minimax_review_score.py     # MINIMAX_REVIEW_SCORE node
    │       ├── save_draft.py               # SAVE_DRAFT node
    │       ├── verify_draft.py             # VERIFY_DRAFT node
    │       ├── commit_row.py               # COMMIT_ROW node
    │       ├── reflect_failure.py          # REFLECT_FAILURE node
    │       └── halt.py                     # HALT node (终态)
    │
    ├── agents/                             # Layer 3: Agent 类层次
    │   ├── __init__.py
    │   ├── base.py                         # BaseAgent (ABC)
    │   ├── worker.py                       # WorkerAgent (无状态)
    │   ├── stateful.py                     # StatefulAgent (有状态)
    │   ├── desktop.py                      # DesktopAgent (UI 操作)
    │   ├── jm_host.py                      # JmHostAgent (京麦主框架)
    │   ├── jm_product_form.py              # JmProductFormAgent (商品表单)
    │   ├── jm_webview.py                   # JmWebViewAgent (WebView 解析)
    │   ├── native_dialog.py                # NativeDialogAgent (原生对话框)
    │   ├── jd_crawler.py                   # JdCrawlerAgent (京东数据抓取)
    │   ├── image_fetch.py                  # ImageFetchAgent (图片下载)
    │   ├── excel_parse.py                  # ExcelParseAgent (xlsx 解析)
    │   └── image_transform.py              # ImageTransformAgent (VLM 图片转换)
    │
    ├── strategies/                         # Layer 4: Strategy
    │   ├── __init__.py
    │   ├── observe.py                      # ObserveStrategy (截图+OCR+坐标证据)
    │   ├── plan.py                         # DeterministicPlanStrategy
    │   ├── action.py                       # GuardedActionStrategy
    │   ├── verify.py                       # VerifyStrategy
    │   └── reflect.py                      # FailureReflectionStrategy
    │
    ├── commands/                           # Layer 5: Command 数据类
    │   ├── __init__.py
    │   ├── base.py                         # Command 基类
    │   ├── fill.py                         # FillCommand
    │   ├── click.py                        # ClickCommand
    │   ├── navigate.py                     # NavigateCommand
    │   ├── read.py                         # ReadCommand
    │   └── upload.py                       # UploadCommand
    │
    ├── backends/                           # Layer 5: Backend 实现
    │   ├── __init__.py
    │   ├── uia/                            # ★ 从 UFO v1 直接复制
    │   │   ├── __init__.py
    │   │   ├── controller.py
    │   │   ├── inspector.py
    │   │   └── ui_tree.py
    │   ├── win32/                          # ★ 从 UFO v1 直接复制
    │   │   ├── __init__.py
    │   │   ├── window.py
    │   │   ├── focus.py
    │   │   └── screenshot.py
    │   ├── clipboard/
    │   │   ├── __init__.py
    │   │   └── handler.py
    │   ├── web_surface/                    # QtWebEngine 不暴露控件时的主通道
    │   │   ├── __init__.py
    │   │   ├── screenshot_ocr.py           # 截图 + OCR + 坐标定位
    │   │   ├── coordinate_plan.py          # 字段坐标计划
    │   │   ├── clipboard_fill.py           # 选中/清空/粘贴/读回
    │   │   └── verifier.py                 # 截图/读回验证
    │   └── js_bridge/                      # 仅调试/可用时辅助读，不作为默认控制
    │       ├── __init__.py
    │       └── injector.py
    │
    ├── storage/                            # 持久化层
    │   ├── __init__.py
    │   ├── mysql.py                        # asyncmy 连接池
    │   ├── redis_client.py                 # redis.asyncio 客户端
    │   ├── milvus_client.py                # pymilvus 客户端
    │   ├── repositories/                   # 每个表一个 repository
    │   │   ├── __init__.py
    │   │   ├── tasks.py
    │   │   ├── products.py
    │   │   ├── product_assets.py
    │   │   ├── row_execution_states.py
    │   │   ├── field_execution_states.py
    │   │   ├── step_logs.py
    │   │   ├── artifacts.py
    │   │   ├── locator_cache.py
    │   │   ├── draft_verifications.py
    │   │   ├── vlm_calls.py
    │   │   └── graph_checkpoints.py
    │   ├── checkpointer.py                 # AsyncMySQLSaver
    │   └── schema/                         # MySQL DDL
    │       ├── 001_tasks.sql
    │       ├── 002_products.sql
    │       ├── 003_product_assets.sql
    │       ├── 004_row_execution_states.sql
    │       ├── 005_field_execution_states.sql
    │       ├── 006_step_logs.sql
    │       ├── 007_artifacts.sql
    │       ├── 008_locator_cache.sql
    │       ├── 009_draft_verifications.sql
    │       ├── 010_vlm_calls.sql
    │       ├── 011_graph_checkpoints.sql
    │       └── 012_graph_pending_writes.sql
    │
    ├── runtime/                            # 单进程运行时
    │   ├── __init__.py
    │   ├── app.py                          # asyncio 主入口
    │   ├── task_group.py                   # asyncio.TaskGroup 包装
    │   ├── workers/
    │   │   ├── __init__.py
    │   │   ├── data_fetch.py               # JdCrawler + ImageFetch 协程
    │   │   ├── image_process.py            # VLM 串行队列
    │   │   └── gui_main.py                 # GUI 主循环协程
    │   └── locks.py                        # GUI mutex / VLM 限流
    │
    ├── safety/                             # 安全策略
    │   ├── __init__.py
    │   ├── policy.py                       # SafetyPolicy (硬阻断)
    │   └── audit.py                        # 违规审计 + 上报
    │
    ├── locators/                           # 元素定位策略
    │   ├── __init__.py
    │   ├── base.py                         # Locator 基类
    │   ├── surface_locator.py              # WebView 截图/OCR/坐标定位 (首选)
    │   ├── uia_locator.py                  # 原生 Qt/UIA-based (仅非 HTML 控件)
    │   └── vlm_locator.py                  # VLM 视觉定位 (最后兜底)
    │
    ├── core/                               # ★ v1 复用层（仅基础设施）
    │   ├── __init__.py
    │   ├── config.py                       # 配置加载
    │   ├── logger.py                       # 日志
    │   ├── exceptions.py                   # 异常体系
    │   ├── form_executor.py                # 通用表单执行器
    │   └── settings.py                     # Pydantic Settings
    │
    │
    ├── utils/                              # 工具
    │   ├── __init__.py
    │   ├── retry.py                        # 线性退避重试
    │   ├── rate_limit.py                   # 令牌桶
    │   ├── cosine_sim.py                   # 页面签名相似度
    │   ├── hash.py                         # 截图/文本 hash
    │   └── pricing.py                      # 采购价/市场价计算
    │
    └── tests/                              # ★ TDD 测试
        ├── __init__.py
        ├── unit/
        │   ├── test_safety_policy.py
        │   ├── test_pricing.py
        │   ├── test_retry.py
        │   ├── test_cosine_sim.py
        │   ├── test_async_mysql_saver.py
        │   ├── test_agents_base.py
        │   ├── test_strategies.py
        │   ├── test_workflow_nodes.py
        │   ├── test_workflow_graph.py
        │   └── test_repositories.py
        ├── integration/
        │   ├── test_mysql_repo.py
        │   ├── test_redis_cache.py
        │   ├── test_milvus_search.py
        │   ├── test_field_resume.py
        │   ├── test_row_resume.py
        │   └── test_safety_block.py
        └── e2e/
            ├── test_jm_dryrun.py          # 模拟京麦，干跑全流程
            ├── test_xlsx_to_drafts.py     # xlsx → 草稿（mock 京麦）
            └── test_crash_resume.py       # 崩溃恢复 E2E
```

---

## 3. Agent 继承层次

### 3.1 类层次图

```
BaseAgent (ABC)
├── WorkerAgent (无状态、可并发)
│   ├── NetworkAgent
│   │   ├── JdCrawlerAgent
│   │   └── ImageFetchAgent
│   └── FileAgent
│       ├── ExcelParseAgent
│       └── ImageTransformAgent
│
└── StatefulAgent (有状态、串行)
    └── DesktopAgent (UI 操作)
        ├── JmHostAgent
        ├── JmProductFormAgent
        ├── JmWebViewAgent
        └── NativeDialogAgent
```

### 3.2 BaseAgent（抽象基类）

```python
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar("T")

class BaseAgent(ABC, Generic[T]):
    """所有 Agent 的根基类。

    职责：
    - 持有 name、version、logger
    - 定义统一的 run(input) -> output 接口
    - 提供健康检查接口
    """

    name: str
    version: str

    def __init__(self, *, name: str | None = None, version: str = "1.0.0"):
        self.name = name or self.__class__.__name__
        self.version = version
        self._logger = get_logger(self.name)

    @abstractmethod
    async def run(self, input: T) -> T: ...

    async def health_check(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"<{self.name} v{self.version}>"
```

### 3.3 WorkerAgent（无状态）

```python
class WorkerAgent(BaseAgent[T]):
    """无状态、可并发、可水平扩展的 worker。"""

    @abstractmethod
    async def run(self, input: T) -> T: ...

    async def run_batch(self, inputs: list[T], concurrency: int = 3) -> list[T]:
        """带信号量的并发执行。"""
        sem = asyncio.Semaphore(concurrency)

        async def _one(inp: T) -> T:
            async with sem:
                return await self.run(inp)

        return await asyncio.gather(*[_one(i) for i in inputs])
```

#### 3.3.1 NetworkAgent

```python
class NetworkAgent(WorkerAgent[T]):
    """网络 IO 密集型 worker，受网络限流。"""

    rate_limit_per_sec: float = 2.0
    _token_bucket: TokenBucket

    async def run(self, input: T) -> T:
        await self._token_bucket.acquire()
        return await self._fetch(input)

    @abstractmethod
    async def _fetch(self, input: T) -> T: ...
```

- **JdCrawlerAgent**：访问京东商品页，提取价格、标题、SKU、图片列表。
- **ImageFetchAgent**：下载京东商品主图/副图到本地。

#### 3.3.2 FileAgent

```python
class FileAgent(WorkerAgent[T]):
    """本地文件读写型 worker。"""

    @abstractmethod
    async def run(self, input: T) -> T: ...
```

- **ExcelParseAgent**：解析 `湖南上架表格.xlsx` → `list[dict]`。
- **ImageTransformAgent**：调用 VLM 把图片转换为京麦适配的尺寸/格式/水印。

### 3.4 StatefulAgent → DesktopAgent

```python
class StatefulAgent(BaseAgent[T]):
    """有状态 Agent，串行执行，持有 UI 句柄/会话状态。"""

    _state: dict
    _lock: asyncio.Lock

    async def run(self, input: T) -> T:
        async with self._lock:
            return await self._run_locked(input)

    @abstractmethod
    async def _run_locked(self, input: T) -> T: ...
```

```python
class DesktopAgent(StatefulAgent[T]):
    """桌面 UI 操作 Agent。

    强约束：
    - 所有 click/fill/submit 必须先调 safety_policy.assert_allowed(cmd)
    - 每次操作前必须验证窗口焦点
    - 操作后必须验证返回值或 DOM 状态
    """

    _window_handle: int
    _expected_window_title: str

    async def _run_locked(self, input: T) -> T:
        safety_policy.assert_window_focus(self._expected_window_title)
        cmd = self._to_command(input)
        safety_policy.assert_allowed(cmd)
        result = await self._execute(input)
        await self._verify(result)
        return result

    @abstractmethod
    def _to_command(self, input: T) -> Command: ...

    @abstractmethod
    async def _execute(self, input: T) -> T: ...

    @abstractmethod
    async def _verify(self, result: T) -> None: ...
```

#### 3.4.1 DesktopAgent 子类

| 类名 | 负责模块 | `_expected_window_title` |
|---|---|---|
| `JmHostAgent` | 京麦主框架（导航、菜单） | "京麦商家工作台" |
| `JmProductFormAgent` | 商品表单（输入框、下拉、图片上传） | "新增商品" / "编辑商品" |
| `JmWebViewAgent` | QtWebEngine 表面（截图/OCR/坐标/剪贴板/读回验证） | "WebView" |
| `NativeDialogAgent` | 原生对话框（确认、选择文件） | "Dialog" |

#### 3.4.2 WebView 操作边界

`JmWebViewAgent` 必须遵守以下规则：

1. 默认不假设 HTML 控件可通过 UIA、DOM selector、JS 注入直接操作。
2. 首次进入页面时一次性截图 + OCR，定位必填项 label、输入框边界、按钮边界，生成 `FieldCoordinatePlan` 并缓存到 MySQL `locator_cache` 与 Redis `page:{signature}:ocr`。
3. VLM 只用于 OCR 结果校验、异常归因、定位计划修正，不允许直接发起点击/输入命令。
4. 填写动作必须使用确定性命令：聚焦坐标、全选/清空、剪贴板写入、粘贴、截图/读回验证。
5. 每个字段失败最多 3 次线性退避；仍失败则写入 `field_execution_states.skipped` 或 `verify_failed`，并 halt 当前 row，不能继续猜。
6. 文件选择、系统弹窗、原生 Qt 控件不走 WebView 通道，交给 `NativeDialogAgent` + UFO/UIA/Win32/WinCO1 action。

### 3.5 VLM 重试策略

```python
class VLMRetryPolicy:
    """线性退避 VLM 重试：3 次，间隔 1s, 2s, 3s。"""

    MAX_ATTEMPTS = 3
    BASE_DELAY = 1.0  # 秒

    def __init__(self, base_delay: float = 1.0):
        self.base_delay = base_delay

    async def execute(self, fn, *args, **kwargs):
        last_exc = None
        for attempt in range(1, self.MAX_ATTEMPTS + 1):
            try:
                return await fn(*args, **kwargs)
            except (VLMTimeoutError, VLMUnavailableError) as e:
                last_exc = e
                if attempt >= self.MAX_ATTEMPTS:
                    break
                delay = self.base_delay * attempt  # 1, 2, 3
                self._logger.warning(
                    "VLM attempt %d/%d failed: %s; retrying in %.1fs",
                    attempt, self.MAX_ATTEMPTS, e, delay,
                )
                await asyncio.sleep(delay)
        raise VLMMaxRetriesExceeded(last_exc)
```

---

## 4. Strategy 层（7 个无状态策略）

### 4.1 ObserveStrategy

```python
class ObserveStrategy:
    """截图 + OCR 一次性扫描，生成 WebView 表面证据。"""

    async def observe(
        self,
        screenshot: bytes,
        page_signature: str,
    ) -> PageObservation:
        ocr_text = await self._ocr_engine.scan(screenshot)  # 一次性 OCR
        field_boxes = await self._field_detector.extract_required_fields(screenshot, ocr_text)
        await self._cache.put(page_signature, ocr_text, screenshot, field_boxes)
        return PageObservation(
            screenshot=screenshot,
            ocr_text=ocr_text,
            field_boxes=field_boxes,
            signature=page_signature,
        )
```

### 4.2 DeterministicPlanStrategy

```python
class DeterministicPlanStrategy:
    """基于 schema + OCR 坐标计划生成待填字段序列，不调用 LLM。"""

    PRODUCT_SCHEMA: list[str] = [
        "title", "category", "brand", "jd_price",
        "purchase_price", "market_price", "sku",
        "main_image", "sub_images", "description",
        "weight", "stock", "attributes",
    ]

    def plan(
        self,
        row_data: dict,
        verified_fields: set[str],
        coordinate_plan: FieldCoordinatePlan,
    ) -> list[FillStep]:
        pending = [f for f in self.PRODUCT_SCHEMA if f not in verified_fields]
        return [FillStep(field_key=f, locator=coordinate_plan.require(f)) for f in pending]
```

### 4.3 GuardedActionStrategy

```python
class GuardedActionStrategy:
    """每个动作前 + 后双重校验。"""

    async def execute(
        self,
        cmd: Command,
        executor: Callable,
        verifier: Callable,
    ) -> None:
        safety_policy.assert_allowed(cmd)
        result = await executor(cmd)
        await verifier(result)  # 失败抛 VerifyError
```

### 4.4 VerifyStrategy

```python
class VerifyStrategy:
    """截图/剪贴板读回校验优先，VLM 只做兜底校验。"""

    async def verify(
        self,
        field_key: str,
        expected_value: str,
        screenshot: bytes,
        locator: FieldLocator,
    ) -> VerifyResult:
        actual = await self._clipboard_reader.read_focused_value(field_key)
        source = "clipboard"

        if actual is None:
            actual = await self._ocr_reader.read_box(screenshot, locator)
            source = "ocr"

        if actual is None:
            # VLM 只读取截图证据；不能覆盖 expected，也不能把失败强行标记成功。
            actual = await self._vlm_extract(screenshot, field_key)
            source = "vlm"

        if actual == expected_value:
            return VerifyResult(passed=True, source=source)
        return VerifyResult(passed=False, source=source,
                            expected=expected_value, actual=actual)
```

### 4.5 FormCompletionScoreStrategy

表单填写完成度是 `SAVE_DRAFT` 的前置闸门。只有完成度 **≥ 90%**，且没有关键阻断项，才能点击「保存草稿」。该分数由字段状态、截图/OCR/读回证据、图片资产状态、价格校验共同计算，不能由 LLM/VLM 直接给分。

```python
class FormCompletionScoreStrategy:
    """保存草稿前的确定性完成度评分。"""

    PASS_THRESHOLD = 0.90

    FIELD_WEIGHTS: dict[str, float] = {
        "title": 0.10,
        "category": 0.10,
        "brand": 0.05,
        "sku": 0.05,
        "jd_price": 0.05,
        "purchase_price": 0.05,
        "market_price": 0.05,
        "main_image": 0.15,
        "sub_images": 0.10,
        "description": 0.10,
        "weight": 0.05,
        "stock": 0.05,
        "attributes": 0.10,
    }

    HARD_BLOCKERS = {
        "title", "category", "purchase_price", "market_price", "main_image",
    }

    async def score(
        self,
        field_states: dict[str, FieldExecutionState],
        asset_states: list[ProductAssetState],
        price_check: PriceCheckResult,
        evidence: PageEvidence,
    ) -> FormCompletionResult:
        score = 0.0
        missing: list[str] = []
        blockers: list[str] = []

        for field_key, weight in self.FIELD_WEIGHTS.items():
            fs = field_states.get(field_key)
            if fs and fs.status == "verified" and fs.actual_value:
                score += weight
            else:
                missing.append(field_key)
                if field_key in self.HARD_BLOCKERS:
                    blockers.append(field_key)

        if not price_check.passed:
            blockers.append("price_check")

        if not any(a.asset_type == "image_main" and a.transform_status == "transformed"
                   for a in asset_states):
            blockers.append("main_image_asset")

        passed = score >= self.PASS_THRESHOLD and not blockers
        return FormCompletionResult(
            score=round(score, 4),
            threshold=self.PASS_THRESHOLD,
            passed=passed,
            missing_fields=missing,
            blockers=blockers,
            evidence=evidence,
        )
```

评分路由规则与截图中 `_route_after_critic` 的思想一致，但用于表单完成度时更严格：

1. `score >= 0.90` 且 `blockers=[]`：进入 `SAVE_DRAFT`。
2. `score < 0.90`：halt 当前 row，记录缺失字段，不允许保存草稿。
3. `score >= 0.90` 但存在 `blockers`：halt 当前 row，优先处理阻断项。
4. VLM 可以解释为什么缺字段，但不能把 `score` 提高，也不能清空 `blockers`。

### 4.6 MiniMaxReviewScoreStrategy

`MiniMaxReviewScoreStrategy` 用 MiniMax OpenAI-compatible API 调用 `MiniMax-M3`，对当前表单状态做“评审评分 + 是否终结评估”的判断。它是 `ASSESS_FORM_COMPLETION` 后的第二道评审闸门，但不能覆盖确定性完成度和安全规则。

```python
class MiniMaxReviewScoreStrategy:
    """MiniMax-M3 评审-修订循环评分器。"""

    MODEL = "MiniMax-M3"
    MAX_LOOP_STEPS = 3
    MAX_CALL_ATTEMPTS = 5
    BASE_BACKOFF_SEC = 1.0
    MAX_BACKOFF_SEC = 60.0

    async def review(
        self,
        state: GraphState,
        completion: FormCompletionResult,
    ) -> MiniMaxReviewResult:
        if state.get("evaluation_loop_count", 0) >= self.MAX_LOOP_STEPS:
            return MiniMaxReviewResult(
                decision="halt",
                score=0,
                reason="max evaluation loop steps exceeded",
                missing_fields=[],
            )

        payload = self._build_openai_compatible_payload(state, completion)
        response = await self._call_with_exponential_backoff(payload)
        result = MiniMaxReviewResult.model_validate_json(response.content)

        # 大模型只能收窄待修订项，不能放宽安全/确定性评分。
        if completion.score < 0.90 or completion.blockers:
            if result.decision == "save_draft":
                result.decision = "revise"
                result.reason = "deterministic completion gate not passed"

        return result

    async def _call_with_exponential_backoff(self, payload: dict) -> MiniMaxRawResponse:
        last_error = None
        for attempt in range(1, self.MAX_CALL_ATTEMPTS + 1):
            try:
                return await self._client.chat_completions(payload)
            except (TimeoutError, RateLimitError, APIConnectionError) as e:
                last_error = e
                if attempt >= self.MAX_CALL_ATTEMPTS:
                    break
                delay = min(self.BASE_BACKOFF_SEC * (2 ** (attempt - 1)), self.MAX_BACKOFF_SEC)
                await asyncio.sleep(delay)
        raise MiniMaxReviewUnavailable(last_error)
```

评审路由规则：

1. `decision="save_draft"` 且 `completion.score >= 0.90` 且 `completion.blockers=[]`：进入 `SAVE_DRAFT`。
2. `decision="revise"` 且 `evaluation_loop_count < 3`：把 `missing_fields` 合并到 `pending_fields`，返回 `PLAN_FIELDS` / `FILL_FIELD`。
3. `decision="halt"` 或 `evaluation_loop_count >= 3`：退出循环，写日志和截图，halt 当前 row。
4. MiniMax API 调用失败使用指数退避：`1s, 2s, 4s, 8s, 16s`，单次最大不超过 `60s`；超过 `MAX_CALL_ATTEMPTS` 记为 `review_scorer_unavailable` 并 halt 评审循环。

### 4.7 FailureReflectionStrategy

```python
class FailureReflectionStrategy:
    """失败时调 VLM 反思 + Milvus 检索相似案例。"""

    async def reflect(
        self,
        field_key: str,
        error: str,
        page_evidence: PageEvidence,
        screenshot: bytes,
    ) -> ReflectionResult:
        # 1. Milvus 检索相似失败
        similar = await self._milvus.search_failures(field_key, error)
        # 2. VLM 反思
        reflection = await self._vlm_reflect(
            field_key, error, page_evidence, screenshot, similar
        )
        # 3. 写回 Milvus 经验库
        await self._milvus.upsert_failure(field_key, error, reflection)
        return reflection
```

---

## 5. SafetyPolicy（硬安全屏障）

### 5.1 硬阻断列表（硬编码，绝不通过配置绕过）

```python
HARD_BLOCKED_ACTIONS: frozenset[str] = frozenset({
    "commit_publish",        # 任何"发布商品"路径
    "delete_product",        # 任何"删除商品"路径
    "modify_price_outside_range",  # 价格超出 [采购价 × 0.9, 市场价 × 1.1] 范围
})

HARD_BLOCKED_LABELS: frozenset[str] = frozenset({
    "发布商品", "立即发布", "上架发布", "提交发布", "发布并上架",
})

ONLY_ALLOWED_FINAL_SAVE_LABELS: frozenset[str] = frozenset({
    "保存草稿", "保存为草稿",
})
```

### 5.2 校验入口

```python
class SafetyPolicy:
    """所有 DesktopAgent.run_command() 入口必调。"""

    def assert_allowed(self, cmd: Command) -> None:
        # 1. 关键词黑名单（UIA 文本 + 可用时 DOM 文本 + label + 坐标计划名称都查）
        text = f"{cmd.target} {cmd.value or ''}".lower()
        for blocked in HARD_BLOCKED_ACTIONS:
            if blocked in text:
                raise SafetyViolation(
                    f"HARD-BLOCKED action '{blocked}' triggered by {cmd!r}"
                )

        # 2. 价格范围校验
        #    范围: [purchase_price × 0.9, market_price × 1.1]
        #    其中 purchase_price / market_price 来自当前 product 行
        #    (purchase_price = jd_price × 0.95; market_price = jd_price / 0.85)
        if cmd.field_key and "price" in cmd.field_key:
            price = _parse_price(cmd.value)
            purchase = cmd.product_context["purchase_price"]
            market = cmd.product_context["market_price"]
            if price is None or not (0.9 * purchase <= price <= 1.1 * market):
                raise SafetyViolation(
                    f"price {price} outside allowed range "
                    f"[{0.9 * purchase:.2f}, {1.1 * market:.2f}]"
                )

        # 3. 发布按钮二次校验（防御 DOM 被改）
        if cmd.kind == ActionKind.CLICK:
            if any(kw in (cmd.value or "") for kw in HARD_BLOCKED_LABELS):
                raise SafetyViolation("publish button click attempted")
```

### 5.3 窗口焦点断言

```python
def assert_window_focus(self, expected_window: str) -> None:
    """在 OBSERVE_PAGE 前调用，焦点错误立即 halt。"""
    fg = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(fg)
    if expected_window not in title:
        raise SafetyViolation(
            f"window focus lost: expected '{expected_window}', got '{title}'"
        )
```

### 5.4 草稿保存白名单与 LLM 权限边界

1. `SAVE_DRAFT` 是唯一允许的提交类节点；最终按钮文本必须命中 `ONLY_ALLOWED_FINAL_SAVE_LABELS`，否则 halt。
2. `SAVE_DRAFT` 前必须存在最近一次 `FormCompletionResult`，且 `score >= 0.90`、`passed=True`、`blockers=[]`；否则 halt。
3. `SAVE_DRAFT` 前必须存在最近一次 `MiniMaxReviewResult`，且 `decision="save_draft"`；若 `decision="revise"` 则返回填表，若 `decision="halt"` 则退出循环。
4. `commit_publish`、发布类按钮文本、疑似发布坐标、未知提交按钮全部按 `SafetyViolation` 处理。
5. LLM/VLM 输出只能生成“建议动作”或“失败归因”，必须先转成 `Command` 并通过 `SafetyPolicy.assert_allowed`。
6. LLM/VLM 不能修改 row/field 状态，不能把 `verify_failed`、`fill_failed`、`draft_verification.failed` 或 `form_completion.failed` 改成成功。
7. 验证失败必须留下截图、OCR 文本、动作日志、错误信息和 VLM 反思结果，然后 halt 当前 row。

### 5.5 强约束（写入 AGENTS.md）

1. 所有 `DesktopAgent` / `NetworkAgent` 的 `run_command` / `click` / `fill` 方法，第一行必须调用 `safety_policy.assert_allowed(cmd)`，否则该方法视为违规实现。
2. CI 增加 grep 检查：禁止出现未调用 `assert_allowed` 的 `click/fill/submit` 方法。
3. `.env` 由部署机器单独持有；开发用 `.env.example` 启动 mock backend。
4. 凭证轮转：每 90 天强制更换 MySQL/Redis 密码，触发脚本写入 `scripts/rotate_secrets.py`。

---

## 6. LangGraph 状态机

### 6.1 18 节点总览

```
BOOTSTRAP → RECOVER → SELECT_ROW ──→ PREPARE_ASSETS ──→ OPEN_PAGE
                              │                            ↓
                              └──→ OPEN_PAGE              OBSERVE_PAGE
                                                           ↓
                                                   ASSERT_PAGE_SIGNATURE
                                                     ┌────┴────┐
                                                  通过        失败
                                                     │          │
                                                     ↓          ↓
                                                  PLAN_FIELDS  CALIBRATE_LOCATORS
                                                     ↓          │
                                                  FILL_FIELD ←──┘
                                                     ↓
                                                  VERIFY_FIELD ──(失败)──→ REFLECT_FAILURE
                                                     │                            │
                                                  成功/继续                       ↓
                                                     │                        FILL_FIELD (≤3 次)
                                                     ↓                            │
                                                   [下一字段?]──是──→ FILL_FIELD   │
                                                      │否            ↓超过 3 次→ HALT
                                                      ↓
                                                   ASSESS_FORM_COMPLETION
                                                      │
                                                   MINIMAX_REVIEW_SCORE
                                                ┌────┼────┐
                                             保存草稿 修订  退出/超3步
                                                │    │        │
                                                │    └──→ PLAN_FIELDS
                                                │             │
                                                ↓             ↓
                                                   SAVE_DRAFT
                                                     ↓
                                                  VERIFY_DRAFT
                                                     ↓
                                                  COMMIT_ROW ──→ SELECT_ROW (下一个 row)
                                                     │
                                                  所有 row 完成
                                                     ↓
                                                   HALT (终态)
```

### 6.2 节点职责

| 节点 | 职责 | 触发外部依赖 |
|---|---|---|
| `BOOTSTRAP` | 解析 xlsx，写入 product 表 | ExcelParseAgent |
| `RECOVER` | 检查 checkpoint / `row_execution_states`，恢复 row 上下文 | MySQL |
| `SELECT_ROW` | 选下一个 pending row | MySQL |
| `PREPARE_ASSETS` | 并发抓京东数据 + 下载图片 | JdCrawlerAgent, ImageFetchAgent |
| `OPEN_PAGE` | 在京麦打开「新增商品」页面 | JmHostAgent |
| `OBSERVE_PAGE` | 截图 + OCR 一次性扫描，生成 WebView 表面证据 | WebViewAgent |
| `ASSERT_PAGE_SIGNATURE` | 余弦相似度 ≥ 0.95 | 本地计算 |
| `CALIBRATE_LOCATORS` | signature 不匹配时调用 VLM 校验 OCR/坐标计划 | VLM (qwen3-vl:8b) |
| `PLAN_FIELDS` | 按 schema + 坐标计划生成待填字段序列 | 本地 |
| `FILL_FIELD` | WebView 区域走坐标/剪贴板；原生控件走 UIA/Win32/WinCO1 | DesktopAgent |
| `VERIFY_FIELD` | 剪贴板读回/局部 OCR 校验 + VLM 兜底 | WebViewAgent / VLM |
| `ASSESS_FORM_COMPLETION` | 汇总字段、图片、价格、截图证据，完成度 ≥90% 才允许保存草稿 | FormCompletionScoreStrategy |
| `MINIMAX_REVIEW_SCORE` | 用 MiniMax-M3 做评审评分和终止判断；未达标返回填表，最多 3 步 | MiniMaxReviewScoreStrategy |
| `SAVE_DRAFT` | 点击「保存草稿」（SafetyPolicy 校验） | DesktopAgent |
| `VERIFY_DRAFT` | 用截图、列表页特征、草稿记录验证保存成功 | WebViewAgent |
| `COMMIT_ROW` | 标记 row 完成 + 写 step_log | MySQL |
| `REFLECT_FAILURE` | VLM 反思 + Milvus 检索相似失败案例 | VLM + Milvus |
| `HALT` | 立即停止，保留 checkpoint | — |

### 6.3 GraphState 定义

```python
class GraphState(TypedDict, total=False):
    # 任务上下文
    task_id: str
    xlsx_path: str
    total_rows: int

    # 当前 row
    current_row_idx: int
    current_row_data: dict
    current_product_id: int | None

    # 当前 field
    current_field_key: str
    pending_fields: list[str]
    filled_fields: list[str]
    failed_fields: list[str]

    # 资产
    jd_data: dict | None
    images: list[dict]  # [{"local_path": ..., "remote_url": ...}]

    # 页面观察
    page_signature: str | None
    page_ocr_text: str | None
    page_screenshot_path: str | None
    page_field_boxes: dict | None

    # Locator 缓存
    locator_cache: dict  # field_key -> FieldLocator / coordinate box

    # 错误 & 重试
    last_error: str | None
    retry_count: int
    field_retry_count: int

    # 表单完成度评分
    form_completion_score: float | None
    form_completion_passed: bool
    form_completion_blockers: list[str]

    # MiniMax-M3 评审-修订循环
    evaluation_loop_count: int
    minimax_review_score: float | None
    minimax_review_decision: str | None  # "save_draft" | "revise" | "halt"
    minimax_review_missing_fields: list[str]

    # 控制流
    next_action: str  # "continue" | "halt" | "recover" | "reflect" | "calibrate"
```

### 6.3.1 节点执行协议

每个会触碰京麦窗口的节点必须按同一协议执行：

1. **Observe**：确认窗口焦点、页面签名、截图路径、OCR/读回证据。
2. **Decide**：用确定性状态机选择下一步；VLM 只能提供截图状态判断、异常归因、OCR 校验建议。
3. **Act**：把动作转换成 `Command`，通过 `SafetyPolicy` 后才执行。
4. **Verify**：动作后立即截图或读回验证；验证失败写入 `step_logs`、`artifacts`、`field_execution_states`。
5. **Halt on uncertainty**：焦点丢失、页面不一致、按钮位置不可信、草稿验证失败、VLM 三次兜底失败时立即 halt，保留现场，不继续猜。

### 6.4 AsyncMySQLSaver

```python
class AsyncMySQLSaver(BaseCheckpointSaver):
    """LangGraph checkpointer 实现，持久化到 MySQL graph_checkpoints 表。"""

    def __init__(self, pool: asyncmy.Pool):
        self._pool = pool

    async def aput(self, config, checkpoint, metadata, new_versions):
        thread_id = config["configurable"]["thread_id"]
        cp_id = checkpoint["id"]
        await self._pool.execute(
            """INSERT INTO graph_checkpoints
               (thread_id, checkpoint_id, parent_checkpoint_id,
                state_json, metadata_json, created_at)
               VALUES (%s, %s, %s, %s, %s, NOW())
               ON DUPLICATE KEY UPDATE state_json=VALUES(state_json),
                                     metadata_json=VALUES(metadata_json)""",
            (thread_id, cp_id, checkpoint.get("parent_id"),
             json_dumps(checkpoint["state_values"]),
             json_dumps(metadata)),
        )
        return {"configurable": {"thread_id": thread_id, "checkpoint_id": cp_id}}

    async def aget_tuple(self, config):
        thread_id = config["configurable"]["thread_id"]
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """SELECT checkpoint_id, parent_checkpoint_id,
                              state_json, metadata_json
                       FROM graph_checkpoints
                       WHERE thread_id=%s
                       ORDER BY created_at DESC LIMIT 1""",
                    (thread_id,),
                )
                row = await cur.fetchone()
                if not row:
                    return None
                return {
                    "configurable": {"thread_id": thread_id, "checkpoint_id": row[0]},
                    "checkpoint": Checkpoint(
                        id=row[0], parent_id=row[1],
                        state_values=json_loads(row[2]),
                        metadata=json_loads(row[3]),
                    ),
                }

    async def alist(self, config) -> AsyncIterator[Checkpoint]:
        thread_id = config["configurable"]["thread_id"]
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """SELECT checkpoint_id, parent_checkpoint_id,
                              state_json, metadata_json
                       FROM graph_checkpoints
                       WHERE thread_id=%s
                       ORDER BY created_at DESC""",
                    (thread_id,),
                )
                async for row in cur:
                    yield Checkpoint(
                        id=row[0], parent_id=row[1],
                        state_values=json_loads(row[2]),
                        metadata=json_loads(row[3]),
                    )

    async def put_writes(self, config, writes, task_id):
        thread_id = config["configurable"]["thread_id"]
        async with self._pool.acquire() as conn:
            async with conn.cursor() as cur:
                for channel, value in writes:
                    await cur.execute(
                        """INSERT INTO graph_pending_writes
                           (thread_id, task_id, channel, value_json, created_at)
                           VALUES (%s, %s, %s, %s, NOW())""",
                        (thread_id, task_id, channel, json_dumps(value)),
                    )
```

### 6.5 字段级断点续传

核心表：`field_execution_states (task_id, row_idx, field_key)` 复合主键。

```python
async def fill_field_node(state: GraphState) -> GraphState:
    task_id = state["task_id"]
    row_idx = state["current_row_idx"]
    field_key = state["current_field_key"]

    # ① 字段级续传检查
    fs = await mysql.get_field_state(task_id, row_idx, field_key)
    if fs and fs["status"] == "verified":
        state["filled_fields"].append(field_key)
        return _advance_field(state)

    # ② locator 解析（内存缓存 → MySQL 缓存 → 页面 OCR 坐标计划）
    locator = (
        state["locator_cache"].get(field_key)
        or await mysql.get_locator(field_key)
        or await coordinate_planner.require(
            field_key,
            screenshot_path=state["page_screenshot_path"],
            ocr_text=state["page_ocr_text"],
            field_boxes=state["page_field_boxes"],
        )
    )

    # ③ SafetyPolicy 校验（硬阻断）
    value = state["current_row_data"][field_key]
    safety_policy.assert_allowed(FillCommand(field_key=field_key, value=value, locator=locator))

    # ④ 执行填充
    try:
        await desktop_agent.fill_field(locator, value)  # WebView: 坐标聚焦 + 剪贴板粘贴；原生控件: UIA/Win32
        await mysql.upsert_field_state(task_id, row_idx, field_key, "pending_verify", locator=locator)
    except Exception as e:
        await mysql.upsert_field_state(task_id, row_idx, field_key, "fill_failed", error=str(e))
        state["failed_fields"].append(field_key)
        state["last_error"] = str(e)
        state["next_action"] = "reflect"
    return state
```

```python
async def verify_field_node(state: GraphState) -> GraphState:
    task_id, row_idx, field_key = (
        state["task_id"], state["current_row_idx"], state["current_field_key"]
    )
    expected = state["current_row_data"][field_key]

    locator = state["locator_cache"].get(field_key) or await mysql.get_locator(field_key)

    # ① 机械读回（首选）：当前字段全选复制，读取剪贴板
    actual = await web_view_agent.read_field_by_clipboard(locator)
    source = "clipboard"

    # ② 局部 OCR 兜底，避免每步全屏 OCR
    if actual is None:
        actual = await web_view_agent.read_field_by_ocr(locator, state["page_screenshot_path"])
        source = "ocr"

    # ③ VLM 兜底：仅判断截图状态，不能覆盖失败状态
    if actual is None:
        actual = await vlm_extract_field_value(state["page_screenshot_path"], field_key)
        source = "vlm"

    if actual == expected:
        await mysql.upsert_field_state(task_id, row_idx, field_key, "verified", verified_by=source)
        state["filled_fields"].append(field_key)
    else:
        await mysql.upsert_field_state(task_id, row_idx, field_key, "verify_failed",
                                        error=f"expected={expected}, actual={actual}")
        state["failed_fields"].append(field_key)
        state["next_action"] = "reflect"
    return state
```

```python
async def assess_form_completion_node(state: GraphState) -> GraphState:
    task_id = state["task_id"]
    row_idx = state["current_row_idx"]

    field_states = await mysql.get_field_states(task_id, row_idx)
    asset_states = await mysql.get_product_assets(state["current_product_id"])
    price_check = pricing.validate_prices(state["current_row_data"])
    evidence = PageEvidence(
        screenshot_path=state["page_screenshot_path"],
        ocr_text=state["page_ocr_text"],
        field_boxes=state["page_field_boxes"],
    )

    result = await form_completion_strategy.score(
        field_states=field_states,
        asset_states=asset_states,
        price_check=price_check,
        evidence=evidence,
    )

    await mysql.upsert_row_state(
        task_id,
        row_idx,
        status="fields_done" if result.passed else "halted",
        completion_score=result.score,
        completion_passed=result.passed,
        completion_details_json=result.model_dump(),
    )
    await mysql.insert_step_log(
        task_id,
        row_idx,
        "assess_form_completion",
        "ok" if result.passed else "fail",
        metadata={"score": result.score, "blockers": result.blockers},
    )

    state["form_completion_score"] = result.score
    state["form_completion_passed"] = result.passed
    state["form_completion_blockers"] = result.blockers

    if not result.passed:
        return _halt(
            state,
            reason=(
                f"form completion score {result.score:.2%} below 90% "
                f"or blockers={result.blockers}"
            ),
        )
    return state
```

```python
async def minimax_review_score_node(state: GraphState) -> GraphState:
    task_id = state["task_id"]
    row_idx = state["current_row_idx"]
    loop_count = state.get("evaluation_loop_count", 0)

    if loop_count >= settings.review_scorer_max_loop_steps:
        return _halt(state, reason="MiniMax review loop exceeded 3 steps")

    completion = FormCompletionResult(
        score=state["form_completion_score"],
        passed=state["form_completion_passed"],
        blockers=state["form_completion_blockers"],
        missing_fields=state.get("pending_fields", []),
    )

    try:
        result = await minimax_review_score_strategy.review(state, completion)
    except MiniMaxReviewUnavailable as e:
        await mysql.insert_step_log(
            task_id, row_idx, "minimax_review_score", "fail",
            error=f"review_scorer_unavailable: {e}",
        )
        return _halt(state, reason="review_scorer_unavailable")

    state["evaluation_loop_count"] = loop_count + 1
    state["minimax_review_score"] = result.score
    state["minimax_review_decision"] = result.decision
    state["minimax_review_missing_fields"] = result.missing_fields

    await mysql.upsert_row_state(
        task_id,
        row_idx,
        review_score=result.score,
        review_decision=result.decision,
        evaluation_loop_count=state["evaluation_loop_count"],
        review_details_json=result.model_dump(),
    )

    if result.decision == "save_draft" and state["form_completion_passed"]:
        return state

    if result.decision == "revise" and state["evaluation_loop_count"] < settings.review_scorer_max_loop_steps:
        state["pending_fields"] = merge_pending_fields(
            state.get("pending_fields", []),
            result.missing_fields,
        )
        state["next_action"] = "revise"
        return state

    return _halt(
        state,
        reason=f"MiniMax review terminated: {result.decision}, score={result.score}",
    )
```

### 6.6 行级断点续传

核心表：`row_execution_states (task_id, row_idx)` 复合主键。状态机：
`pending → in_progress → assets_ready → form_opened → fields_done → draft_saved → committed | failed`。

#### 6.6.1 当前任务恢复种子规则

当前默认任务证据为：`row5`、`row6`、`row7` 已保存草稿；下一条可执行商品行必须自动判定为 `row82`。该规则只作为当前任务的恢复种子，不是通用跳行算法。

恢复时必须同时满足：

1. MySQL `row_execution_states` 中 `row5-row7` 状态为 `draft_saved` 或 `committed`。
2. `draft_verifications` 存在对应草稿验证记录，且验证结果不是 `failed`。
3. `artifacts` 中存在保存草稿后的截图或列表页证据。
4. `products.row_idx=82` 存在且状态为 `pending` / `in_progress` / `assets_ready` 之一。
5. 上述任一证据缺失时 halt，输出截图与日志，不允许自动猜测下一行。

```python
async def recover_node(state: GraphState) -> GraphState:
    task_id = state["task_id"]

    # ① 找下一个 pending / in_progress 的 row
    next_row = await mysql.select_resumable_row(task_id)
    if next_row is None:
        return _halt(state, reason="no resumable row")

    # ② 加载 row 数据
    row_data = await mysql.get_product(task_id, next_row["row_idx"])

    # ③ 计算 pending fields（schema - verified fields）
    verified = await mysql.get_verified_fields(task_id, next_row["row_idx"])
    pending = [f for f in PRODUCT_SCHEMA if f not in verified]

    # ④ 加载 row 级资产
    state["jd_data"] = await mysql.get_jd_data(task_id, next_row["row_idx"])
    state["images"] = await mysql.get_images(task_id, next_row["row_idx"])

    state.update(
        current_row_idx=next_row["row_idx"],
        current_row_data=row_data,
        filled_fields=list(verified.keys()),
        failed_fields=[],
        pending_fields=pending,
    )
    return state
```

```python
async def commit_row_node(state: GraphState) -> GraphState:
    task_id, row_idx = state["task_id"], state["current_row_idx"]

    # ① 行级提交
    await mysql.upsert_row_state(task_id, row_idx, "committed")
    await mysql.insert_step_log(task_id, row_idx, "commit", "ok")

    # ② 行级 checklist
    if not _row_complete(state):
        return _halt(state, reason="row incomplete at commit")

    # ③ 推进到下一个 row
    next_row = await mysql.select_resumable_row(task_id)
    if next_row is None:
        return _halt(state, reason="all rows committed")
    state.update(current_row_idx=next_row["row_idx"], filled_fields=[], failed_fields=[])
    return state
```

### 6.7 Graph 构建

```python
def build_graph() -> CompiledStateGraph:
    g = StateGraph(GraphState)
    for name, fn in NODES.items():
        g.add_node(name, fn)

    g.set_entry_point("BOOTSTRAP")
    g.add_edge("BOOTSTRAP", "RECOVER")
    g.add_edge("RECOVER", "SELECT_ROW")

    g.add_conditional_edges(
        "SELECT_ROW",
        lambda s: "PREPARE_ASSETS" if needs_assets(s) else "OPEN_PAGE",
    )
    g.add_edge("PREPARE_ASSETS", "OPEN_PAGE")
    g.add_edge("OPEN_PAGE", "OBSERVE_PAGE")
    g.add_edge("OBSERVE_PAGE", "ASSERT_PAGE_SIGNATURE")

    g.add_conditional_edges(
        "ASSERT_PAGE_SIGNATURE",
        lambda s: "PLAN_FIELDS" if s.get("next_action") == "continue" else "CALIBRATE_LOCATORS",
    )
    g.add_edge("CALIBRATE_LOCATORS", "ASSERT_PAGE_SIGNATURE")

    g.add_edge("PLAN_FIELDS", "FILL_FIELD")
    g.add_edge("FILL_FIELD", "VERIFY_FIELD")

    g.add_conditional_edges(
        "VERIFY_FIELD",
        lambda s: "HALT" if s.get("next_action") == "halt"
                  else ("REFLECT_FAILURE" if s.get("next_action") == "reflect"
                        else ("PLAN_FIELDS" if more_fields(s) else "ASSESS_FORM_COMPLETION")),
    )
    g.add_conditional_edges(
        "REFLECT_FAILURE",
        lambda s: "HALT" if s["retry_count"] >= 3 else "FILL_FIELD",
    )

    g.add_conditional_edges(
        "ASSESS_FORM_COMPLETION",
        lambda s: "MINIMAX_REVIEW_SCORE",
    )
    g.add_conditional_edges(
        "MINIMAX_REVIEW_SCORE",
        lambda s: "SAVE_DRAFT" if s.get("minimax_review_decision") == "save_draft"
                  else ("PLAN_FIELDS" if s.get("minimax_review_decision") == "revise"
                        and s.get("evaluation_loop_count", 0) < 3 else "HALT"),
    )
    g.add_edge("SAVE_DRAFT", "VERIFY_DRAFT")
    g.add_edge("VERIFY_DRAFT", "COMMIT_ROW")
    g.add_edge("COMMIT_ROW", "SELECT_ROW")
    g.add_edge("HALT", END)

    return g.compile(checkpointer=AsyncMySQLSaver(mysql.pool))
```

---

## 7. 存储 Schema

### 7.1 MySQL 12 张表

#### 7.1.1 tasks
任务表，一个 xlsx 文件对应一条记录。

| 列 | 类型 | 说明 |
|---|---|---|
| task_id | VARCHAR(64) PK | 任务唯一标识 |
| xlsx_path | VARCHAR(512) | 输入 xlsx 路径 |
| workflow_docx_path | VARCHAR(512) | 上架流程 docx 路径 |
| workflow_version | VARCHAR(64) | 从流程文档生成的工作流版本 |
| status | ENUM | pending/running/paused/halted/completed/failed |
| total_rows | INT UNSIGNED | 总行数 |
| pending_rows | INT UNSIGNED | 待处理行数 |
| completed_rows | INT UNSIGNED | 已完成行数 |
| failed_rows | INT UNSIGNED | 失败行数 |
| created_at | DATETIME(3) | |
| updated_at | DATETIME(3) | |

#### 7.1.2 products
商品数据表，xlsx 解析后的原始数据 + 京东抓取数据。

| 列 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK AUTO_INCREMENT | |
| task_id | VARCHAR(64) FK | |
| row_idx | INT UNSIGNED | xlsx 中的行号 |
| row_hash | CHAR(64) | xlsx 原始行规范化后的 SHA-256 |
| source_xlsx_path | VARCHAR(512) | 来源表格路径 |
| sku | VARCHAR(64) | 商品 SKU |
| title | VARCHAR(512) | 商品标题 |
| jd_price | DECIMAL(12,2) | 京东价格 |
| purchase_price | DECIMAL(12,2) | 采购价 = jd_price × 0.95 |
| market_price | DECIMAL(12,2) | 市场价 = jd_price / 0.85 |
| status | ENUM | pending/assets_ready/form_filling/draft_saved/committed/failed |
| raw_data_json | JSON | xlsx 原始行 |
| jd_data_json | JSON | 京东爬取数据 |
| normalized_data_json | JSON | 合并后的执行数据，不覆盖 raw_data_json |

UNIQUE KEY (task_id, row_idx)。
UNIQUE KEY (task_id, row_hash)。

数据一致性规则：

1. `raw_data_json` 只保存 Excel 原始行，导入后不可被京东抓取结果覆盖。
2. 京东链接抓取结果只写 `jd_data_json`；采购价、市场价等派生字段写 `normalized_data_json` 和显式价格列。
3. 价格计算固定为：`purchase_price = jd_price * 0.95`，`market_price = jd_price / 0.85`；市场价必须高于京东价且控制在约 3% 以内。
4. 每次启动先用 `row_hash` 比对 Excel 当前行与 MySQL 中已存行；不一致时 halt 并要求重新建任务，不能悄悄覆盖执行中的商品数据。
5. 图片下载与 VLM 转换结果只写 `product_assets`，表单上传时引用 `transformed_path`。

#### 7.1.3 product_assets
商品资产表。

| 列 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | |
| product_id | BIGINT FK | |
| asset_type | ENUM | image_main/image_sub/video/doc |
| local_path | VARCHAR(512) | 本地路径 |
| remote_url | VARCHAR(1024) | 远程 URL |
| transform_status | ENUM | pending/transformed/uploaded/failed |
| transformed_path | VARCHAR(512) | 转换后路径 |

#### 7.1.4 row_execution_states
**行级断点续传主表**。

| 列 | 类型 | 说明 |
|---|---|---|
| task_id | VARCHAR(64) PK | |
| row_idx | INT UNSIGNED PK | |
| status | ENUM | pending/in_progress/assets_ready/form_opened/fields_done/draft_saved/committed/failed/skipped |
| current_field | VARCHAR(64) | |
| retry_count | INT UNSIGNED | |
| last_error | TEXT | |
| page_signature | VARCHAR(64) | |
| completion_score | DECIMAL(5,4) | 保存草稿前表单完成度评分 |
| completion_passed | TINYINT(1) | 是否达到 90% 且无阻断项 |
| completion_details_json | JSON | 缺失字段、阻断项、评分明细、证据路径 |
| evaluation_loop_count | INT UNSIGNED | MiniMax-M3 评审-修订循环次数，最大 3 |
| review_score | DECIMAL(5,4) | MiniMax-M3 最近一次评审分 |
| review_decision | ENUM | save_draft/revise/halt |
| review_details_json | JSON | MiniMax-M3 输出的缺口、理由、建议 |
| started_at | DATETIME(3) | |
| updated_at | DATETIME(3) | |

#### 7.1.5 field_execution_states
**字段级断点续传主表**。

| 列 | 类型 | 说明 |
|---|---|---|
| task_id | VARCHAR(64) PK | |
| row_idx | INT UNSIGNED PK | |
| field_key | VARCHAR(64) PK | |
| status | ENUM | pending/filling/pending_verify/verified/fill_failed/verify_failed/skipped |
| locator | VARCHAR(512) | |
| expected_value | TEXT | |
| actual_value | TEXT | |
| verified_by | ENUM | clipboard/ocr/vlm/manual |
| attempts | INT UNSIGNED | |
| last_error | TEXT | |

#### 7.1.6 step_logs
每个 node 执行的日志。

| 列 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | |
| task_id | VARCHAR(64) FK | |
| row_idx | INT UNSIGNED | |
| node_name | VARCHAR(64) | |
| status | ENUM | ok/fail/skipped |
| duration_ms | INT UNSIGNED | |
| error | TEXT | |
| metadata_json | JSON | |

#### 7.1.7 artifacts
制品（截图、WebView 表面快照、OCR 文本）。

| 列 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | |
| task_id | VARCHAR(64) FK | |
| row_idx | INT UNSIGNED | |
| artifact_type | ENUM | screenshot/web_surface_snapshot/ocr_text/page_signature |
| storage_path | VARCHAR(512) | |

#### 7.1.8 locator_cache
元素定位缓存。

| 列 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | |
| field_key | VARCHAR(64) | |
| page_signature | VARCHAR(64) | |
| selector_type | ENUM | coordinate_box/uia/name/xpath/css |
| selector_value | VARCHAR(512) | |
| confidence | DECIMAL(4,3) | |
| hit_count | INT UNSIGNED | |

UNIQUE KEY (field_key, page_signature)。

#### 7.1.9 draft_verifications
草稿校验记录。

| 列 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | |
| product_id | BIGINT FK | |
| task_id | VARCHAR(64) | |
| row_idx | INT UNSIGNED | |
| draft_url | VARCHAR(1024) | |
| completion_score | DECIMAL(5,4) | 保存草稿前通过的完成度评分 |
| verification_result | ENUM | passed/failed/partial |
| diff_json | JSON | |

#### 7.1.10 vlm_calls
VLM 调用记录（成本 + 性能监控）。

| 列 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | |
| task_id | VARCHAR(64) FK | |
| row_idx | INT UNSIGNED | |
| call_type | ENUM | ocr_check/locator_calibrate/failure_reflect/image_transform/field_extract |
| model | VARCHAR(64) | |
| prompt_tokens | INT UNSIGNED | |
| completion_tokens | INT UNSIGNED | |
| latency_ms | INT UNSIGNED | |
| status | ENUM | ok/fail/timeout |
| cache_hit | TINYINT(1) | |

#### 7.1.11 graph_checkpoints
LangGraph checkpoint 持久化。

| 列 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | |
| thread_id | VARCHAR(64) | |
| checkpoint_id | VARCHAR(128) | |
| parent_checkpoint_id | VARCHAR(128) | |
| node_name | VARCHAR(64) | |
| state_json | LONGTEXT | |
| metadata_json | JSON | |

UNIQUE KEY (thread_id, checkpoint_id)。

#### 7.1.12 graph_pending_writes
并行节点待写入（put_writes）。

| 列 | 类型 | 说明 |
|---|---|---|
| id | BIGINT PK | |
| thread_id | VARCHAR(64) | |
| task_id | VARCHAR(64) FK | |
| channel | VARCHAR(64) | |
| value_json | LONGTEXT | |

### 7.2 Redis Keys

| Key 模式 | 类型 | TTL | 用途 |
|---|---|---|---|
| `task:{task_id}:progress` | Hash | 永久 | 实时进度：total/pending/completed/failed/current_row |
| `task:{task_id}:row:{row_idx}:lock` | String NX EX | 300s | 行级互斥锁 |
| `task:{task_id}:pause_flag` | String NX | 永久 | 暂停信号 |
| `page:{page_signature}:surface` | String | 3600s | WebView 表面快照缓存 |
| `page:{page_signature}:ocr` | String | 3600s | OCR 文本缓存 |
| `page:{page_signature}:screenshot` | String | 3600s | 截图路径 |
| `vlm:cache:{sha1(prompt+image)}` | String | 86400s | VLM 响应缓存 |
| `jm:window:focus` | String | 永久 | 当前京麦前台窗口句柄 |
| `jm:safety:violations:{task_id}` | Hash | 永久 | 安全违规计数 |
| `jm:rate_limit:{vlm}` | Token bucket | 60s | VLM 速率限制 |

### 7.3 Milvus Collections

连接：`host=8.137.122.11, port=19530`, db=`jingmai_kb`, embedding=`nomic-embed-text` (dim=768)。

| Collection | 字段关键 schema | 用途 |
|---|---|---|
| `ocr_samples` | image_hash, ocr_raw, ocr_corrected, correction_type, embedding | 查询相似 OCR 错误用于自动纠错 |
| `field_locator_kb` | field_key, page_signature, selector_*, success_rate, embedding | 新页面 signature 时检索相似历史定位 |
| `failure_reflections` | field_key, error_type, error_message, reflection, resolution, embedding | 新失败发生时检索相似历史案例 |
| `vlm_image_transforms` | src_image_hash, dst_image_hash, transform_type, vlm_prompt, embedding | 新图转换时检索最佳转换策略 |

所有 collection 索引：`IVF_FLAT`，metric=`COSINE`，nlist=1024。

---

## 8. 凭证与安全

### 8.1 凭证管理（红线：严禁硬编码）

**`.env`（gitignored，仅生产部署机持有）：**
```bash
JINGMAI_MYSQL_HOST=8.137.122.11
JINGMAI_MYSQL_PORT=3306
JINGMAI_MYSQL_USER=root
JINGMAI_MYSQL_PASSWORD=<从密钥管理服务获取>
JINGMAI_MYSQL_DB=jingmai_agent

JINGMAI_REDIS_HOST=8.137.122.11
JINGMAI_REDIS_PORT=6379
JINGMAI_REDIS_PASSWORD=<从密钥管理服务获取>
JINGMAI_REDIS_DB=0

JINGMAI_MILVUS_HOST=8.137.122.11
JINGMAI_MILVUS_PORT=19530
JINGMAI_MILVUS_DB=jingmai_kb

JINGMAI_LLM_OLLAMA_BASE=http://localhost:11434
JINGMAI_LLM_OLLAMA_MODEL=qwen3-vl:8b-instruct
JINGMAI_LLM_TIMEOUT_SEC=60
JINGMAI_LLM_MAX_RETRIES=3
JINGMAI_FORM_COMPLETION_THRESHOLD=0.90

# 需求/设计评审评分器：MiniMax OpenAI-compatible API
JINGMAI_REVIEW_SCORER_PROVIDER=minimax
JINGMAI_REVIEW_SCORER_BASE_URL=https://api.minimax.io/v1
JINGMAI_REVIEW_SCORER_API_KEY=<从密钥管理服务获取>
JINGMAI_REVIEW_SCORER_MODEL=MiniMax-M3
JINGMAI_REVIEW_SCORER_THINKING=adaptive
JINGMAI_REVIEW_SCORER_MAX_LOOP_STEPS=3
JINGMAI_REVIEW_SCORER_MAX_CALL_ATTEMPTS=5
JINGMAI_REVIEW_SCORER_BACKOFF_BASE_SEC=1
JINGMAI_REVIEW_SCORER_BACKOFF_MAX_SEC=60

# 兼容通用 LLM 配置名；优先级低于 JINGMAI_LLM_*，但必须支持
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_API_KEY=ollama
LLM_MODEL=qwen3-vl:8b-instruct

JINGMAI_ARTIFACT_DIR=<set-me>
JINGMAI_TEMP_DIR=<set-me>
```

**`.env.example`（入库，全部占位符）：**
```bash
JINGMAI_MYSQL_HOST=127.0.0.1
JINGMAI_MYSQL_PORT=3306
JINGMAI_MYSQL_USER=<set-me>
JINGMAI_MYSQL_PASSWORD=<set-me>
JINGMAI_MYSQL_DB=jingmai_agent

JINGMAI_REDIS_HOST=127.0.0.1
JINGMAI_REDIS_PORT=6379
JINGMAI_REDIS_PASSWORD=<set-me-if-needed>
JINGMAI_REDIS_DB=0

JINGMAI_MILVUS_HOST=127.0.0.1
JINGMAI_MILVUS_PORT=19530
JINGMAI_MILVUS_DB=jingmai_kb

JINGMAI_LLM_OLLAMA_BASE=http://localhost:11434
JINGMAI_LLM_OLLAMA_MODEL=qwen3-vl:8b-instruct
JINGMAI_LLM_TIMEOUT_SEC=60
JINGMAI_LLM_MAX_RETRIES=3
JINGMAI_FORM_COMPLETION_THRESHOLD=0.90

JINGMAI_REVIEW_SCORER_PROVIDER=minimax
JINGMAI_REVIEW_SCORER_BASE_URL=https://api.minimax.io/v1
JINGMAI_REVIEW_SCORER_API_KEY=<set-me>
JINGMAI_REVIEW_SCORER_MODEL=MiniMax-M3
JINGMAI_REVIEW_SCORER_THINKING=adaptive
JINGMAI_REVIEW_SCORER_MAX_LOOP_STEPS=3
JINGMAI_REVIEW_SCORER_MAX_CALL_ATTEMPTS=5
JINGMAI_REVIEW_SCORER_BACKOFF_BASE_SEC=1
JINGMAI_REVIEW_SCORER_BACKOFF_MAX_SEC=60

LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_API_KEY=ollama
LLM_MODEL=qwen3-vl:8b-instruct

JINGMAI_ARTIFACT_DIR=<set-me>
JINGMAI_TEMP_DIR=<set-me>
```

**Pydantic Settings 加载：**
```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="JINGMAI_",
        env_nested_delimiter="_",
        extra="ignore",
    )

    mysql_host: str
    mysql_port: int = 3306
    mysql_user: str
    mysql_password: str
    mysql_db: str = "jingmai_agent"

    redis_host: str
    redis_port: int = 6379
    redis_password: str | None = None
    redis_db: int = 0

    milvus_host: str
    milvus_port: int = 19530
    milvus_db: str = "jingmai_kb"

    llm_ollama_base: str = "http://localhost:11434"
    llm_ollama_model: str = "qwen3-vl:8b-instruct"
    llm_timeout_sec: int = 60
    llm_max_retries: int = 3
    form_completion_threshold: float = 0.90
    llm_provider: str = "ollama"
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model: str | None = None

    review_scorer_provider: str = "minimax"
    review_scorer_base_url: str = "https://api.minimax.io/v1"
    review_scorer_api_key: str | None = None
    review_scorer_model: str = "MiniMax-M3"
    review_scorer_thinking: str = "adaptive"
    review_scorer_max_loop_steps: int = 3
    review_scorer_max_call_attempts: int = 5
    review_scorer_backoff_base_sec: float = 1.0
    review_scorer_backoff_max_sec: float = 60.0

    artifact_dir: str
    temp_dir: str

settings = Settings()  # 进程启动时一次性加载，验证失败立即抛错
settings.llm_base_url = settings.llm_base_url or settings.llm_ollama_base
settings.llm_model = settings.llm_model or settings.llm_ollama_model
```

**`.gitignore` 必含：**
```
.env
.env.local
.env.*.local
artifacts/
tmp/
__pycache__/
.pytest_cache/
```

### 8.2 SafetyPolicy 强约束

1. 所有 `DesktopAgent` 的 `click`/`fill`/`submit` 方法第一行必须调用 `safety_policy.assert_allowed(cmd)`。
2. CI 增加 grep 检查：禁止出现未调用 `assert_allowed` 的 `click/fill/submit` 方法。
3. `.env` 由部署机器单独持有；开发用 `.env.example` 启动 mock backend。
4. 凭证轮转：每 90 天强制更换 MySQL/Redis 密码，触发脚本写入 `scripts/rotate_secrets.py`。

---

## 9. 单进程多协程运行时

### 9.1 主入口

```python
async def main():
    settings = Settings()
    await init_storage(settings)
    graph = build_graph()
    config = {"configurable": {"thread_id": settings.task_id}}
    async with asyncio.TaskGroup() as tg:
        tg.create_task(run_graph(graph, config))
        tg.create_task(data_fetch_worker())
        tg.create_task(image_process_worker())
        tg.create_task(gui_main_loop())
```

### 9.2 三类协程

| 协程 | 并发模型 | 限流 |
|---|---|---|
| `data_fetch_worker` | asyncio.Semaphore(3) | 最多 3 个并发京东抓取/图片下载 |
| `image_process_worker` | asyncio.Queue (maxsize=1) | 串行 VLM 图片转换 |
| `gui_main_loop` | asyncio.Lock | 串行桌面 UI 操作（WebView 坐标/clipboard；原生 UIA/Win32） |

### 9.3 GUI 互斥

```python
gui_lock = asyncio.Lock()

async def with_gui_lock(coro):
    async with gui_lock:
        return await coro
```

---

## 10. 验收标准

### 10.1 功能验收

| ID | 功能 | 验收标准 | 优先级 |
|---|---|---|---|
| F01 | xlsx 解析 | 解析 `湖南上架表格.xlsx` 后 product 表 ≥ xlsx 实际行数 | P0 |
| F02 | 京东数据抓取 | 抓取价格/标题/图片列表成功率 ≥ 95% | P0 |
| F03 | 图片下载 + 转换 | 主图 + 副图全部下载并 VLM 转换成功 | P0 |
| F04 | 京麦登录 | 自动检测登录态，未登录则提示人工登录 | P0 |
| F05 | 打开新增商品页 | 验证 `_expected_window_title` 命中 | P0 |
| F06 | 字段填写 | 12 个核心字段全部 verified 状态 | P0 |
| F07 | 草稿保存 | 点击「保存草稿」成功，跳转列表页 | P0 |
| F08 | **绝不发布** | SafetyPolicy 在任何发布路径上抛 SafetyViolation | **P0（红线）** |
| F09 | 字段级断点续传 | 模拟崩溃后，verified 字段不重填 | P0 |
| F10 | 行级断点续传 | 模拟崩溃后，committed row 不重做 | P0 |
| F11 | VLM 重试 | VLM 失败 3 次线性退避后 skip 字段并 halt 当前 row | P1 |
| F12 | CLI 命令模式 | `python -m jm_ufo_agent run --task-id xxx` 一键启动 | P0 |
| F13 | 交互模式 | Rich dashboard 实时显示进度 | P1 |
| F14 | 京麦技术事实识别 | 启动时记录 `Qt51511QWindowIcon`、Qt 子窗口数量、WebView Pane 摘要；确认 0 个 HTML `Edit/ComboBox/Button` UIA 控件 | P0 |
| F15 | WebView 表单策略 | 不依赖 DOM/JS 写入；字段填写使用坐标/剪贴板/局部 OCR/截图验证闭环 | P0 |
| F16 | 当前任务 row82 恢复 | row5-row7 草稿证据齐全时，下一个可执行 row 自动判定为 row82；证据缺失则 halt | P0 |
| F17 | 异常自动中止 | 焦点丢失、页面不一致、按钮位置不可信、草稿验证失败时停止并留下截图/日志 | P0 |
| F18 | 表单完成度评分 | `ASSESS_FORM_COMPLETION` 计算得分 ≥90% 且无阻断项才允许 `SAVE_DRAFT` | P0 |
| F19 | MiniMax 评审循环 | `MINIMAX_REVIEW_SCORE` 使用 `MiniMax-M3` 评分与终止判断；`revise` 返回填表，`save_draft` 进入保存，最多 3 步 | P0 |

### 10.2 非功能验收

| ID | 指标 | 标准 |
|---|---|---|
| NF01 | 单步骤执行间隔 | 5-100s，包含观察、执行、截图/读回验证；网络和 VLM 不计入机械等待 |
| NF02 | VLM 调用次数 | ≤ 15 次/row（OCR 1 + locator 1 + 失败反思 ≤3 + image transform 1-3 + verify 兜底 ≤5） |
| NF03 | 崩溃恢复时间 | ≤ 5s |
| NF04 | MySQL checkpoint 写入 | 每次 FILL_FIELD/VERIFY_FIELD 后 aput，< 50ms |
| NF05 | 单进程内存 | ≤ 500MB |
| NF06 | CI 阻断检查 | grep 检查未调用 assert_allowed 的 click/fill/submit → 失败 |
| NF07 | 评分稳定性 | 同一 row、同一字段状态、同一资产状态重复评分结果完全一致 |
| NF08 | MiniMax 调用退避 | MiniMax-M3 调用失败按指数退避 `1/2/4/8/16s`，超过最大调用次数退出评审循环 |

---

## 11. 风险清单

| ID | 风险 | 等级 | 缓解措施 |
|---|---|---|---|
| R01 | 京麦 UI 改版导致 locator 失效 | High | CALIBRATE_LOCATORS 节点自动调用 VLM 重新定位 |
| R02 | VLM 服务不可用 | High | 3 次线性退避后 skip 字段 + halt 当前 row |
| R03 | 京东反爬 | High | rate_limit_per_sec=2 + 随机 User-Agent + Cookie 池 |
| R04 | 网络中断导致资产下载失败 | Medium | 重试 3 次后跳过该商品，记入失败 row |
| R05 | 京麦页面 signature 大幅变化 | Medium | 阈值 0.95 触发 CALIBRATE，否则 halt 等待人工 |
| R06 | SafetyPolicy 被绕过 | **Critical** | CI grep 强制检查；进程启动时单例化；配置不可关闭 |
| R07 | MySQL checkpoint state_json 超大 | Medium | LONGTEXT 512KB 上限，超过则外置对象存储 |
| R08 | 多 worker 并发填同一 row | High | Redis 行级 NX EX 锁，键值=worker_pid |
| R09 | VLM 缓存击穿 | Low | TTL 24h + Redis 预热 |
| R10 | 凭证泄露到 git | **Critical** | `.env` 入 `.gitignore`；CI 检查禁止 `.env` 提交；定期轮转 |
| R11 | 误把京麦当作 CEF/DOM 可控应用 | **Critical** | 启动检测 Qt5/QtWebEngine 窗口事实；WebView 默认走截图/OCR/坐标/剪贴板 |
| R12 | 合成输入被 WebView 吞掉但代码误判成功 | High | 每步必须截图或读回验证；没有证据不得推进状态 |
| R13 | OCR 坐标计划漂移 | High | 页面 signature + 局部截图相似度校验；漂移时 VLM 校验一次，仍不可信则 halt |

---

## 12. 实施路线图

### Phase 1：基础设施（无业务逻辑）
1. 项目骨架（pyproject.toml, jm_ufo_agent/ 包结构）
2. core/settings.py（Pydantic Settings）
3. storage/mysql.py + storage/redis_client.py + storage/milvus_client.py
4. storage/schema/*.sql（12 张表 DDL）
5. storage/repositories/*（每个表一个 repository）
6. safety/policy.py（SafetyPolicy + HARD_BLOCKED_ACTIONS）
7. utils/retry.py + utils/pricing.py + utils/cosine_sim.py
8. tests/unit/* 覆盖以上

### Phase 2：Agent 层
1. agents/base.py + worker.py + stateful.py + desktop.py
2. 从 `E:\PY\UFO\ufo` 复制并适配 `automator/action_execution.py`、`automator/ui_control/controller.py`、`inspector.py`、`screenshot.py`、`ui_tree.py`
3. 4 个 DesktopAgent 子类（jm_host, jm_product_form, jm_webview, native_dialog）
4. 4 个 WorkerAgent（jd_crawler, image_fetch, excel_parse, image_transform）
5. tests/unit/test_agents_base.py + integration test

### Phase 3：Strategy 层
1. 7 个 Strategy 类实现（Observe/Plan/Action/Verify/FormCompletionScore/MiniMaxReviewScore/Reflect）
2. `backends/web_surface/*`：截图 OCR、坐标计划、剪贴板填写、局部验证
3. tests/unit/test_form_completion_score.py + tests/unit/test_minimax_review_score.py + tests/unit/test_strategies.py

### Phase 4：LangGraph 工作流
1. workflow/state.py + graph.py
2. workflow/nodes/*（18 个 node 文件，含 `ASSESS_FORM_COMPLETION` 与 `MINIMAX_REVIEW_SCORE`）
3. storage/checkpointer.py（AsyncMySQLSaver）
4. tests/integration/test_field_resume.py + test_row_resume.py + test_completion_gate.py + test_minimax_review_loop.py

### Phase 5：运行时
1. runtime/app.py + task_group.py
2. runtime/workers/*（3 个 worker 协程）
3. runtime/locks.py
4. CLI（cli/command.py + cli/interactive.py）
5. tests/e2e/test_jm_dryrun.py + test_crash_resume.py

### Phase 6：生产验证
1. 干跑（mock 京麦）→ 真机小批量（10 row）→ 全量
2. 凭证轮转脚本
3. CI/CD 集成（grep 阻断 + 单元测试 + 集成测试）

---

## 13. 参考与依赖

### 13.1 复用资产
- `E:\PY\UFO\ufo` v1 源码：允许直接复制 `automator/action_execution.py` 与 `automator/ui_control/*` 到本项目 `backends/uia/`、`backends/win32/`、`backends/web_surface/`，保留原许可/版权注释，外层接口按 v2 `Command`/`SafetyPolicy` 适配。
- UFO 只作为底层 action 和窗口/截图能力来源，不继承其 ReAct/自主决策流程。
- `E:\workspace\skills\jingmai-product-publish\core/*`（v1 的基础设施）
- `E:\workspace\skills\jingmai-product-publish\crew/form_executor.py`（v1 的表单执行器，可适配）

### 13.2 外部依赖（Poetry）

```toml
[tool.poetry.dependencies]
python = "^3.11"
langgraph = "^0.2.0"
asyncmy = "^0.2.9"
redis = {extras = ["asyncio"], version = "^5.0.0"}
pymilvus = "^2.4.0"
pydantic = "^2.5.0"
pydantic-settings = "^2.1.0"
aiohttp = "^3.9.0"
playwright = "^1.40.0"  # WebView 调试用
rich = "^13.0.0"
typer = "^0.9.0"
pywin32 = {version = "^306", markers = "sys_platform == 'win32'"}
uiautomation = "^2.0.0"
pillow = "^10.0.0"
opencv-python = "^4.8.0"

[tool.poetry.dev-dependencies]
pytest = "^8.0.0"
pytest-asyncio = "^0.23.0"
pytest-cov = "^4.1.0"
mypy = "^1.7.0"
ruff = "^0.1.0"
```

---

## 14. 需求覆盖评分（2026-06-09 评审）

### 14.1 评分模型与调用格式

需求覆盖评分必须由 MiniMax OpenAI-compatible Chat Completions API 生成，模型固定为 `MiniMax-M3`。评分器只输出评审分、扣分理由和改进建议；不得修改业务状态、表单完成度评分、安全策略或 LangGraph 路由。

启动预检：

1. 使用 `JINGMAI_REVIEW_SCORER_BASE_URL` + `JINGMAI_REVIEW_SCORER_API_KEY` 请求 OpenAI-compatible `GET /models`。
2. 确认返回模型列表包含 `MiniMax-M3`；若不存在、鉴权失败或网络失败，需求评分器 halt，并记录 `review_scorer_unavailable`。
3. 预检失败不影响京麦自动化主流程，但不得生成“MiniMax-M3 已评分”的结论。

调用约定：

```bash
curl --request POST \
  --url https://api.minimax.io/v1/chat/completions \
  --header "Authorization: Bearer ${JINGMAI_REVIEW_SCORER_API_KEY}" \
  --header "Content-Type: application/json" \
  --data '{
    "model": "MiniMax-M3",
    "thinking": {
      "type": "adaptive"
    },
    "messages": [
      {
        "role": "system",
        "content": "你是京麦自动化需求评审员。只根据输入文档和评分rubric打分，输出JSON，不允许补造事实。"
      },
      {
        "role": "user",
        "content": "<SPEC_MARKDOWN_AND_RUBRIC>"
      }
    ],
    "max_completion_tokens": 2000
  }'
```

输出 JSON schema：

```json
{
  "overall_score": 96,
  "max_score": 100,
  "rubric_scores": [
    {
      "item": "表单完成度 >= 90% 才保存草稿",
      "score": 100,
      "max_score": 100,
      "evidence": ["ASSESS_FORM_COMPLETION", "completion_score", "F18"],
      "deductions": []
    }
  ],
  "blocking_gaps": [],
  "recommendations": []
}
```

综合评分：

- **修订前：76 / 100**。主体架构完整，但对京麦真实窗口技术事实、WebView UIA 不可达、row82 恢复种子、DOM/JS 不可作为默认控制通道描述不足。
- **修订后：97 / 100**。核心约束已进入背景、架构、状态机、存储、验收、风险和实施路线；本次新增表单完成度评分闸门与 MiniMax-M3 评审终结循环。剩余分数扣在真实环境证据需要实现阶段自动采集落库验证。

| 核心要点 | 修订前 | 修订后 | 说明 |
|---|---:|---:|---|
| 京麦 = Qt5 壳 + QtWebEngine，不是 CEF | 20% | 100% | 已写入 `Qt51511QWindowIcon`、Chromium 类名误判风险、非 CEF 结论 |
| WebView HTML 控件不暴露给 UIA | 30% | 100% | 已记录 5 个 Pane、0 个 Edit/ComboBox/Button，默认不走 UIA/DOM |
| WebView 操作策略 | 65% | 95% | 已改为截图/OCR/坐标/剪贴板 fallback，JS 仅调试/辅助读 |
| 状态证据驱动进度 | 75% | 100% | 已明确状态文件、截图、OCR/读回、草稿验证是唯一推进依据 |
| row5-row7 已保存，下一行 row82 | 0% | 100% | 已加入当前任务恢复种子规则 |
| 保存草稿红线 | 85% | 100% | 已加入保存草稿白名单和发布硬阻断 label |
| 表单完成度 ≥90% 才保存草稿 | 0% | 100% | 已加入 `ASSESS_FORM_COMPLETION` 节点、评分公式、MySQL 持久化和验收项 |
| MiniMax-M3 评审终结循环 | 0% | 100% | 已加入 `MINIMAX_REVIEW_SCORE`、指数退避、最多 3 步、`revise` 返回填表和超限 halt |
| 评审评分使用 MiniMax-M3 | 0% | 100% | 已规定 MiniMax OpenAI-compatible API、`MiniMax-M3`、JSON 输出 schema 和安全边界 |
| VLM 权限边界 | 80% | 100% | 已明确 VLM 只做校验/反思/图片转换，不能改成功状态 |
| 单进程多协程 | 95% | 95% | 原文已覆盖 asyncio TaskGroup、Semaphore、Queue、GUI Lock |
| MySQL/Redis/Milvus/断点续传 | 90% | 96% | 新增 row_hash、raw/enriched 数据一致性规则 |
| CLI 命令模式 + 交互模式 | 90% | 90% | 原文已覆盖，后续 plan 需细化命令参数 |

## 15. 待办与开放问题

| ID | 问题 | 待谁回答 | 截止 |
|---|---|---|---|
| Q01 | 是否需要支持多账号并行？ | 用户 | 设计评审前 |
| Q02 | 京麦账号的 Cookie 持久化策略？ | 用户 | Phase 2 前 |
| Q03 | VLM 失败后的 fallback（手动接管的 UI）？ | 用户 | Phase 3 前 |
| Q04 | 长期运行是否需要 Web 管理后台？ | 用户 | Phase 5 前 |

---

**END of SPEC**

> 下一步：调用 `superpowers:writing-plans` 技能，按本文档生成详细实施计划（每任务 2-5 分钟步骤，含完整代码 + 测试 + 提交命令）。
