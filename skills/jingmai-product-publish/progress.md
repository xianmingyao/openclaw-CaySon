# jm_ufo_agent v2 本轮进度

## 2026-06-10 真实闭环剩余任务继续推进

- F02：新增 `runtime/jd_batch.py`，提供 `JdBatchCrawlService` 和 `JdCrawlBatchReport`，按批次计算京东标题/价格/图片抓取成功率，并在低于 95% 时返回失败证据；真实网络仍需显式注入 `JdCrawlerAgent` transport。
- F03：新增 `runtime/assets.py`，提供 `AssetPipelineService`，串联 `ImageFetchAgent`、`ImageTransformAgent`、`ProductAssetRepository`、`VlmCallRepository`，可记录下载素材、转换素材和 VLM 审计记录；测试使用 fake handler。
- UFO/UIA/Win32：`ufo_adapter.py` 新增 `Win32DesktopBackend`，支持 click/fill/submit/upload 的真实 API 适配边界；默认 `allow_write=False`，未显式开启时阻断真实写操作。
- F15：`clipboard_fill.py` 新增 `SystemClipboardFillService`，支持真实坐标点击、系统剪贴板写入、Ctrl+A/Ctrl+V 粘贴；默认 `allow_write=False`，必须显式开启才会触碰桌面。
- 真实 E2E：新增 `runtime/e2e.py`，提供 `ProductionE2EOrchestrator`，按固定生产阶段顺序执行注入 handler；readiness 不通过时不启动任何真实阶段，阶段失败后停止后续执行。
- 新增 `tests/test_v2_remaining_real_boundaries.py`，覆盖批量京东成功率、图片/VLM 审计、Win32 写操作门控、系统剪贴板门控、E2E readiness 和阶段顺序。
- 验证结果：`python -m compileall -q jm_ufo_agent tests` 通过；`python -m pytest` 为 84 passed；`uv run --extra test python -m pytest` 为 82 passed, 2 skipped；`python scripts\check_safety_policy.py jm_ufo_agent\agents` 通过；`graphify update .` 更新到 872 nodes / 2239 edges。
- 仍未执行真实外部动作：没有真实访问京东、没有真实点击京麦、没有真实剪贴板写入、没有真实图片/VLM/MiniMax 调用、没有真实保存草稿。当前完成的是可注入生产实现和强安全门控。

## 2026-06-09 gstack 剩余缺口继续推进

- F01：新增 `ExcelProductImportService`，支持解析真实 xlsx 后批量写入 `ProductRepository` 协议，并返回 `parsed_count/written_count/generated_id_rows/first_rows` 验收摘要；CLI 新增 `import-excel --xlsx ...` dry-run 汇总入口。
- F14/F04/F05：新增 `Win32WindowInspectorBackend` 和 `Win32ApiAdapter`，可只读枚举真实 Windows 窗口，提取 `Qt51511QWindowIcon`、Qt 子窗口数量、Chrome/Cef/WebView pane 摘要；CLI 新增 `inspect-jingmai-window`。
- F07/F17：新增 `runtime/evidence.py`，标准化 `HaltEvidenceSnapshot` 和 `DraftVerificationSnapshot`；`GraphState.halt()` 现在统一记录 screenshot/log/OCR/page_signature/window_summary/details；`VERIFY_DRAFT` 输出草稿验证证据结构。
- F13：`interactive.py` 新增 `render_live_dashboard()` 多帧渲染；CLI 新增 `live-dashboard --states-jsonl ...`，可回放状态流，后续可接真实 workflow event stream。
- F19：新增 `runtime/review.py`，提供 `UrllibReviewTransport`、`RetryingReviewTransport`、`build_minimax_review_strategy()`，按配置构造 MiniMax-M3 评审策略并支持指数退避；测试仍使用 fake transport。
- 真实 E2E：`production.py` 新增 `assess_production_readiness()`，按 `parse_excel/crawl_jd/download_images/transform_images/check_jingmai_login/open_add_product_page/fill_webview_form/save_draft/verify_draft_readback` 检查能力缺口；CLI 新增 `production-readiness`。
- 新增 `tests/test_v2_production_gap_closure.py`，覆盖 Excel 导入、Win32 窗口事实、halt/draft 证据、live dashboard、MiniMax retry、production readiness。
- 验证结果：`python -m pytest` 为 79 passed；`uv run --extra test python -m pytest` 为 77 passed, 2 skipped；`python scripts\check_safety_policy.py jm_ufo_agent\agents` 通过；`python -m compileall -q jm_ufo_agent tests` 通过；`graphify update .` 更新到 805 nodes / 1980 edges。
- 仍未执行真实外部动作：没有真实访问京东、没有真实下载商品图片、没有真实调用 VLM/MiniMax、没有真实点击京麦、没有真实保存草稿。当前新增的是生产接入边界和启动前准备度检查。

## 2026-06-09 gstack 真实缺口边界修复

- 已补 F02 京东数据抓取边界：`JdPageParser` 可从注入 HTML/JSON-LD 解析商品 ID、标题、价格、图片 URL；`JdCrawlerAgent` 默认不联网，只有显式注入 transport 时才允许真实抓取。
- 已补图片下载边界：`ImageFetchAgent` 默认 dry-run 返回 requested_urls；显式注入 downloader 后才会访问网络和写入本地图片。
- 已补 F04/F05/F14 京麦主窗口边界：新增 `ufo_adapter.py`，定义 `JingmaiWindowFacts`、`StaticWindowInspectorBackend`、`UfoImportBackend`；`JmHostAgent` 支持登录态判断、新增商品页标题验证、Qt51511QWindowIcon/WebView Pane 摘要证据。
- 已补 WebView 真实闭环的可替换编排：新增 `WebViewFormLoop`，串起截图 OCR、坐标计划、剪贴板填充、二次 OCR、读回验证和局部相似度证据；默认仍是 dry-run/fake provider，不触碰真实桌面。
- 已补 Redis/Milvus 业务缓存边界：新增 `RedisBusinessCache` 覆盖 OCR cache、VLM cache、locator cache；新增 `MilvusReflectionStore` 写入 failure reflection，向量生成仍由上层显式传入。
- 已补 F13 Rich dashboard 快照入口：新增 `cli/progress.py`、`cli/interactive.py`，CLI 增加 `dashboard`；无 rich 时可回退文本输出。
- CLI 增加 `inspect-ufo` 和生产安全门控：`run --backend ufo-observe` 必须显式 `--confirm-real-jingmai` 且当前只允许 observe-only；真实点击/填写/保存仍未开放。
- 新增 `tests/test_v2_real_gap_boundaries.py`，覆盖 JD 解析、图片 dry-run、京麦窗口事实、登录提示、WebView OCR 读回、Redis/Milvus 缓存、dashboard、生产门控、UFO 路径检查。
- 验证结果：`python -m compileall -q jm_ufo_agent tests` 通过；`python -m pytest` 为 73 passed；`uv run --extra test python -m pytest` 为 72 passed, 1 skipped；`python scripts\check_safety_policy.py jm_ufo_agent\agents` 通过；`graphify update .` 更新到 714 nodes / 1739 edges。
- 剩余真实生产缺口：尚未执行真实京麦窗口操作、真实京东网络抓取、真实 OCR/VLM、真实保存草稿、真实 Excel 到草稿读回 E2E。当前是可测试 adapter/contract，不是生产自动上架闭环。

## 2026-06-09 既有进展摘要

- 已建立 `task_plan.md`、`findings.md`、`progress.md` 作为轻量任务追踪文件，不使用 `.ccg/tasks`。
- 已把核心字段从 6 个扩到 12 个：`title/category/brand/sku/jd_price/purchase_price/market_price/main_image/sub_images/description/weight/stock`。
- 已新增 `RowExecutionRepository`、`ArtifactRepository`，并把 MySQL DDL 扩展到 12 张表。
- 已把 `DryRunWorkflow` 接入 SELECT_ROW、RECOVER、字段进度写入、row82 seed 规则和 committed 行状态写入。
- 已新增 `python -m jm_ufo_agent run` 入口，默认仍使用 dry-run，不触碰真实京麦。
- 已新增 `scripts/check_safety_policy.py`，用 AST 检查 `click/fill/submit` 是否先调用 `assert_allowed`。
- MiniMax 评审策略已支持注入 `MiniMaxReviewClient`，测试使用 fake transport，不访问真实 MiniMax。

## 2026-06-09 gstack 缺口开发推进

- 已按 `gstack` 技能读取并分析 `docs/superpowers/specs/2026-06-09-jm-ufo-agent-v2-design.md`，本轮只开发本地可测、不触碰真实京麦/京东/MiniMax 账号的闭环。
- 已新增设计文档要求的 18 个 workflow 节点文件：BOOTSTRAP、RECOVER、SELECT_ROW、PREPARE_ASSETS、OPEN_PAGE、OBSERVE_PAGE、ASSERT_PAGE_SIGNATURE、CALIBRATE_LOCATORS、PLAN_FIELDS、FILL_FIELD、VERIFY_FIELD、ASSESS_FORM_COMPLETION、MINIMAX_REVIEW_SCORE、SAVE_DRAFT、VERIFY_DRAFT、COMMIT_ROW、REFLECT_FAILURE、HALT。
- 已新增 `build_state_graph()`：有 `langgraph` 依赖时注册真实 `StateGraph` 节点；无依赖时返回 `LocalStateGraphSpec`，用于本地测试验证 18 节点和边顺序。
- 已把 `PREPARE_ASSETS` 接入 `DryRunWorkflow`，默认仍是 dry-run；注入失败的图片转换 handler 时，VLM 连续失败 3 次会 halt 当前 row，并写入 `halt_evidence`。
- 已把 `GraphState.halt()` 扩展为带证据的中止记录，保留旧调用兼容，新增 `halt_evidence` 列表，记录 node、reason、details。
- 已补齐 5 个缺失业务 repository：`ProductAssetRepository`、`StepLogRepository`、`LocatorCacheRepository`、`DraftVerificationRepository`、`VlmCallRepository`。
- 已扩展 repository 数据模型：`ProductAssetRecord`、`StepLogRecord`、`LocatorCacheRecord`、`DraftVerificationRecord`、`VlmCallRecord`。
- 已给 `jm_product_assets` 增加唯一键 `uk_jm_product_assets_identity`，与 `ProductAssetRepository.upsert()` 语义一致。
- 已新增测试 `tests/test_v2_state_graph_and_halt.py`，覆盖 18 节点规格、节点文件完整性、halt 证据和 VLM 三次失败 halt。

## 验证记录

- `python -m compileall -q jm_ufo_agent tests`：通过。
- `python -m pytest`：`64 passed`。
- `uv run --extra test python -m pytest`：`63 passed, 1 skipped`。
- `python scripts\check_safety_policy.py jm_ufo_agent\agents`：通过。
- `graphify update .`：通过，图谱更新到 600 nodes / 1386 edges。

## 仍未完成

- 真实 UFO/UIA/Win32 backend 仍未从 `E:\PY\UFO\ufo` 复制/适配。
- 真实京麦登录检测、新增商品页打开、窗口技术事实识别仍未实现。
- WebView 真实截图、OCR、剪贴板写入、读回闭环仍未接入。
- 京东抓取、图片下载、真实 VLM 转换仍未接入生产链路。
- Rich dashboard 仍未实现。
- MiniMax 默认生产 preflight/scoring/退避仍未接入真实运行配置。
