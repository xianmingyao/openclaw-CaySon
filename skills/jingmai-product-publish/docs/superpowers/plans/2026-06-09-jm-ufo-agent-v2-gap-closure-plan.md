# jm_ufo_agent v2 缺陷修复与完善计划

日期：2026-06-09  
基线评分：62 / 100  
目标评分：第一轮提升到 78+，真实京麦小批量验证后提升到 90+

## 目标

把当前 dry-run 骨架推进为“真实可控、证据驱动、可恢复”的京麦保存草稿自动化系统。计划只覆盖保存草稿，不覆盖发布商品。

## 安全边界

- 不实现、不开关、不过滤绕过任何发布商品路径。
- 真实桌面动作必须全部经过 `SafetyPolicy.assert_allowed`。
- 接入真实京麦窗口前必须先通过 mock backend、截图证据和安全静态扫描。
- 任何需要账号、真实京麦窗口、真实京东访问、真实 MiniMax 调用的阶段，都必须单独人工确认运行环境。

## 阶段 1：LangGraph StateGraph 正式化

目的：把当前 `DryRunWorkflow` 迁移成文档要求的 18 节点 StateGraph，同时保留 dry-run 测试能力。

任务：
- 新增 `workflow/nodes/bootstrap.py`、`recover.py`、`select_row.py`、`prepare_assets.py`、`open_page.py`、`observe_page.py`、`assert_page_signature.py`、`calibrate_locators.py`、`plan_fields.py`、`fill_field.py`、`verify_field.py`、`assess_form_completion.py`、`minimax_review_score.py`、`save_draft.py`、`verify_draft.py`、`commit_row.py`、`reflect_failure.py`、`halt.py`。
- 保留 `workflow/nodes/dryrun.py` 作为兼容层，逐步迁移调用方。
- `workflow/graph.py` 新增 `build_state_graph()`，在未安装 LangGraph 时给出明确错误。
- `AsyncMySQLSaver` 接入 graph compile checkpointer。
- 增加节点路由测试：completion gate、review revise、halt、commit row。

验收：
- 18 个节点文件存在，节点名和设计文档一致。
- `build_state_graph()` 可在测试 fake checkpointer 下构建。
- 原 dry-run 测试继续通过。

## 阶段 2：Repository 与业务状态补全

目的：让 12 张表都有明确读写边界，并让 workflow 写入关键业务证据。

任务：
- 新增 `ProductAssetRepository`、`StepLogRepository`、`LocatorCacheRepository`、`DraftVerificationRepository`、`VlmCallRepository`、`GraphCheckpointRepository`、`GraphPendingWriteRepository`。
- 在每个 workflow 节点前后写 `step_logs`。
- 在截图/OCR/页面签名处写 `artifacts`。
- 保存草稿验证结果写 `draft_verifications`。
- VLM 调用统一写 `vlm_calls`，包含 cache_hit、latency、status。

验收：
- 每张表至少有一个 repository 单元测试。
- 关键节点失败时能查到 step log 和 artifact path。
- `python -m pytest` 通过。

## 阶段 3：UFO/UIA/Win32 真实 backend 适配

目的：从 `E:\PY\UFO\ufo` 复制和适配底层窗口、截图、UIA、Win32 能力，但不继承 v1 ReAct 决策流。

任务：
- 复制并隔离 UFO 底层文件到 `backends/uia/`、`backends/win32/`、`backends/clipboard/`。
- 新增 adapter：`UfoDesktopBackend.execute(Command)`。
- 实现窗口枚举、前台焦点断言、窗口标题读取、窗口截图、UIA 树摘要。
- 所有真实 click/fill/submit 仍只从 `DesktopAgent` 入口进入。
- 增加 mock UFO backend 测试和真实 backend smoke 测试开关。

验收：
- 能记录 `Qt51511QWindowIcon`、Qt 子窗口数量、WebView Pane 摘要。
- 真实 backend 测试默认跳过，只有显式环境变量才运行。
- 安全脚本确认没有未保护的高危入口。

## 阶段 4：WebView fallback 闭环

目的：把 WebView 从“模型骨架”推进到截图/OCR/坐标/剪贴板/读回闭环。

任务：
- `ScreenshotOcrService` 接真实截图输入和 OCR engine adapter。
- `CoordinatePlanner` 根据 OCR block 生成字段坐标计划。
- `ClipboardFillService` 实现点击、全选、清空、写剪贴板、粘贴。
- `SurfaceVerifier` 实现剪贴板读回优先、局部 OCR 兜底、截图相似度校验。
- Redis 缓存 `page:{signature}:ocr`、`surface`、`screenshot`。

验收：
- mock 截图可完成字段定位和读回验证。
- 合成输入失败时不能推进 verified。
- 页面 signature 低于阈值时 halt 并写 artifact。

## 阶段 5：真实保存草稿链路

目的：从 dry-run `SAVE_DRAFT` 变成真实点击「保存草稿」并验证结果。

任务：
- 在 UI 层定位「保存草稿」按钮，仅允许白名单 label。
- 点击后等待跳转、toast、列表页或草稿 ID。
- `verify_draft.py` 写入 `draft_verifications`。
- 失败时写截图、OCR 文本、页面 signature、step log。

验收：
- 不存在任何发布按钮点击路径。
- mock 京麦保存草稿 E2E 通过。
- 真实京麦 smoke 仅在人工确认后运行。

## 阶段 6：京东抓取与图片处理

目的：补齐 F02/F03/F11，让商品数据和图片资产进入可执行状态。

任务：
- `JdCrawlerAgent` 抓取标题、价格、图片列表，写 `jd_data_json`。
- 价格派生写 `purchase_price`、`market_price`、`normalized_data_json`。
- `ImageFetchAgent` 下载主图/副图，写 `product_assets`。
- `ImageTransformAgent` 接 VLM 图片转换，失败 3 次后 halt 当前 row。
- 增加网络限流、重试、缓存和失败证据。

验收：
- fake 京东页面解析成功。
- 图片下载/转换 fake VLM 流程成功。
- VLM 失败 3 次后不会继续保存草稿。

## 阶段 7：MiniMax 生产评审闭环

目的：让 `MINIMAX_REVIEW_SCORE` 真正具备 preflight、退避、评分、revise/halt/save_draft 路由。

任务：
- 增加 aiohttp/httpx transport。
- 启动时 `/models` preflight，确认 `MiniMax-M3`。
- 实现 `1/2/4/8/16s` 指数退避。
- 评审结果写 `row_execution_states.review_details_json`。
- API 不可用时记录 `review_scorer_unavailable`，不伪造评分。

验收：
- fake transport 覆盖成功、不可用、超时、非法 JSON。
- 真实 MiniMax 调用必须由环境变量显式开启。

## 阶段 8：Rich dashboard 与运行时编排

目的：补齐 F13，把任务状态、当前 row、字段进度、失败证据实时展示出来。

任务：
- 新增 `cli/interactive.py` 和 `cli/progress.py`。
- 展示 total/pending/completed/failed/current_row。
- 展示当前节点、当前字段、completion_score、review_decision。
- 支持暂停标记读取 `task:{task_id}:pause_flag`。

验收：
- 无真实京麦环境也能用 fake state 播放进度。
- dashboard 不修改业务状态，只读 MySQL/Redis。

## 阶段 9：异常 halt 证据标准化

目的：所有失败都留下可复盘证据。

任务：
- 统一 `halt(reason, evidence)` 结构。
- halt 时写 screenshot、OCR、page_signature、window_summary、step_log。
- `FailureReflectionStrategy` 读取 Milvus 相似失败并写回新反思。
- 增加 `artifacts/` 路径命名规范。

验收：
- 每种失败类型都有 artifact 路径。
- 没有证据的失败不得进入 committed。

## 阶段 10：生产验证路线

目的：避免直接全量跑真实京麦。

顺序：
1. 纯单元测试。
2. mock 京麦 E2E。
3. 真实京麦只观察，不点击。
4. 真实京麦单 row 保存草稿。
5. 真实京麦 10 row 小批量。
6. 全量前人工 review 证据。

退出条件：
- 任一阶段出现发布路径风险，立即停止。
- 任一阶段出现无证据推进状态，立即停止。

## 依赖顺序

1. LangGraph 节点拆分。
2. Repository 补全。
3. UFO backend。
4. WebView fallback。
5. 保存草稿。
6. 京东抓取与图片处理。
7. MiniMax 生产闭环。
8. Rich dashboard。
9. halt 证据标准化。
10. 生产验证。

## 本计划不解决的问题

- 不支持多账号并行。
- 不做发布商品。
- 不做跨店铺调度。
- 不把 DOM/JS 作为默认控制通道。
