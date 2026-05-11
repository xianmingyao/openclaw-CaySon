# Graph Report - jingmai-product-publish  (2026-05-11)

## Corpus Check
- 66 files · ~2,414,560 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1519 nodes · 4686 edges · 82 communities detected
- Extraction: 40% EXTRACTED · 60% INFERRED · 0% AMBIGUOUS · INFERRED: 2823 edges (avg confidence: 0.6)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]

## God Nodes (most connected - your core abstractions)
1. `JingmaiLocator` - 401 edges
2. `BaseAgent` - 306 edges
3. `DatabaseManager` - 122 edges
4. `JDScraper` - 122 edges
5. `MemoryManager` - 112 edges
6. `LLMManager` - 109 edges
7. `PublishTask` - 97 edges
8. `TaskStep` - 97 edges
9. `AgentFactory` - 96 edges
10. `LongTermMemory` - 96 edges

## Surprising Connections (you probably didn't know these)
- `_enrich_product_from_source()` --calls--> `test_cli_enrich_product_from_source_merges_scraped_detail()`  [INFERRED]
  cli.py → tests\test_scraper_enrichment.py
- `_build_product_model()` --calls--> `test_build_product_model_maps_new_fields()`  [INFERRED]
  cli.py → tests\test_behavior.py
- `DatabaseManager` --uses--> `京麦商品发布自动化 - 数据库初始化脚本 建表 + 验证连接`  [INFERRED]
  db.py → init_db.py
- `DatabaseManager` --calls--> `test_db_mysql_retry_falls_back_to_sqlite()`  [INFERRED]
  db.py → tests\test_behavior.py
- `Settings` --calls--> `test_settings_builds_mysql_url_from_components()`  [INFERRED]
  settings.py → tests\test_behavior.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.01
Nodes (367): BaseAgent, 京麦商品发布自动化 - 数据库管理器 MySQL 优先，SQLite 兜底。, Upsert a product by product_id., Upsert a product by product_id., 将 ORM 对象转成字典，避免 detached instance 问题。, Convert an ORM object into a plain dict., Database manager with MySQL preflight and SQLite fallback., Backfill missing columns for existing databases. (+359 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (180): debug_sku_all(), debug_sku_element(), _activate_publish_section_tab(), _append_fill_results(), _build_description_html(), _build_dropdown_keywords(), _click_dropdown_template(), click_element() (+172 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (115): AgentState, from_dict(), MemoryItem, MemoryStore, MemoryType, 京麦商品发布自动化 - Memory 存储基类与数据类型, Think 阶段：读取记忆 + LLM 分析，决定下一步动作         记忆参与决策：检索相关历史经验注入 LLM 上下文, Act 阶段：执行动作         子类必须覆写以定义具体执行逻辑 (+107 more)

### Community 3 - "Community 3"
Cohesion: 0.03
Nodes (90): BaseAgent, _build_precheck_action_hint(), _detect_page_state(), _doc_strict_page_state_can_bypass_marker_check(), ExecutorAgent, _expand_doc_strict_allowed_page_states(), _extract_recovery_category(), _should_block_precheck() (+82 more)

### Community 4 - "Community 4"
Cohesion: 0.03
Nodes (58): ABC, LLMProvider, actions(), Enum, 京麦商品发布自动化 - Memory Package, LLMProvider, _configure_stdio(), get_logger() (+50 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (77): acceptance_run(), _annotate_publish_mode(), batch(), _build_acceptance_run_paths(), _build_db(), _build_execution_evidence(), _build_plan_package(), _build_product_model() (+69 more)

### Community 6 - "Community 6"
Cohesion: 0.05
Nodes (17): create_client(), PipeClient, Named Pipe 客户端 - 连接 Session1 Helper, _attach_scrape_diagnostics(), _is_product_payload_complete(), _parse_opencli_json(), _product_completeness_score(), 京麦商品发布自动化 - JD 商品信息采集 从京东商品页采集标题、价格、类目等信息 (+9 more)

### Community 7 - "Community 7"
Cohesion: 0.05
Nodes (36): _resolve_agent_type(), 获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存, CircuitBreaker, 熔断器 — 借鉴 jingmai-putaway base.py, _annotate_plan_phases(), _attach_react_contracts(), _build_doc_step_specs_from_paragraphs(), _build_doc_strict_guard() (+28 more)

### Community 8 - "Community 8"
Cohesion: 0.05
Nodes (31): ElementPosition, _get_process_name(), _is_excluded_title(), _is_matching_title(), _is_usable_rect(), _print_window_capture(), 京麦商品发布自动化 - 双引擎元素定位器 UIA 元素查找 + 坐标 fallback, 刷新窗口矩形缓存，避免使用过期尺寸做坐标缩放。 (+23 more)

### Community 9 - "Community 9"
Cohesion: 0.12
Nodes (10): auto_discover(), execute(), get(), list_categories(), Action registry and execution hooks., summary(), create_smart_executor(), SmartExecutor - 带截图验证的Executor 每个action执行前/后截图，用LLM视觉分析验证是否真正生效 失败重试3次，成功才执行下一步 (+2 more)

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (18): test_navigate_to_fails_on_click_error(), check_status(), _get_locator(), get_page_info(), 京麦商品发布自动化 - 验证操作 Actions 覆盖 15 个脚本：结果验证、图像定位、状态检查, 获取当前页面中所有 Edit 控件的值，用于状态检查, verify_result(), wait_for_text() (+10 more)

### Community 11 - "Community 11"
Cohesion: 0.27
Nodes (9): find_descendants(), _get_cache_request(), _get_control_filter_condition(), _get_uia_control_id_map(), _get_uia_control_name_map(), _get_uia_defs(), Fast UIA control inspection adapted from UFO's cached UIA backend., UIAElementInfoFix (+1 more)

### Community 12 - "Community 12"
Cohesion: 0.39
Nodes (8): Exception, ActionFailedError, DatabaseError, ElementNotFoundError, JingmaiError, LLMError, MemoryError, WindowNotFoundError

### Community 13 - "Community 13"
Cohesion: 0.29
Nodes (4): _load_dotenv(), 京麦商品发布自动化 - 统一配置 优先级: kwargs > 环境变量 > .env 文件 > 类默认值, 从 .env 文件 + 环境变量 + kwargs 加载配置          优先级: kwargs > 环境变量 > .env 文件 > 类默认值, 手动加载 .env 文件到 os.environ（不依赖 python-dotenv）      格式:       - KEY=VALUE

### Community 14 - "Community 14"
Cohesion: 0.4
Nodes (2): get_element(), 京麦商品发布自动化 - 元素坐标配置 v3.0 基于实际截图分析 (2560x1392)  【重要】坐标来源说明： - 所有坐标均基于2560x1392分辨率截

### Community 15 - "Community 15"
Cohesion: 0.5
Nodes (2): CropSpec, Generate lightweight vision fallback templates from v1 screenshots.  Only stable

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): 京麦商品发布自动化 - 坐标配置别名 对齐设计文档 config/coords.py 命名规范，实际坐标定义在 jingmai_coords.py

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): 标题过滤，避免误命中 IDE、终端和无关小窗。

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (1): 过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): 从 .env 文件 + 环境变量 + kwargs 加载配置          优先级: kwargs > 环境变量 > .env 文件 > 类默认值

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): 从 .env 文件 + 环境变量 + kwargs 加载配置          优先级: kwargs > 环境变量 > .env 文件 > 类默认值

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): LLM 识别图坐标 → 实际屏幕坐标。          LLM 返回的坐标基于识别图（1120x560），         需要先映射到参考分辨率（25

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): 查找京麦窗口（优先 UIA，fallback win32gui）

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): 优先使用当前前台大窗口，解决 jd_ 幽灵句柄误命中的问题。

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): UIA 方式查找窗口（带超时）。          Desktop(backend="uia").windows() 在京麦窗口不存在时会遍历所有窗口，

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): 标题过滤，避免误命中 IDE、终端和无关小窗。

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): 过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): 检测系统里是否存在京麦相关句柄，包括最小化/离屏窗口。

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): 移动前强制释放鼠标键，防止残留按下态导致 move 变拖拽。

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): 仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanLi

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): 右键点击（自动缩放坐标）- 仿人移动+点击

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): 在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): 双击 - 单次前置激活 + 原子 doubleClick，避免按下态遗留。

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (1): 右键点击（自动缩放坐标）- 仿人移动+点击

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (1): 获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): 等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): Scrape JD product basics plus detail assets from a product URL.

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Session 1 辅助程序 - 处理来自 cli 的命令

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): 点击坐标（Session1 Helper）

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): 剪贴板粘贴（Session1 Helper，推荐用于中文）

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): 发送快捷键（Session1 Helper）

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): 按单个键（Session1 Helper）

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): 手动加载 .env 文件到 os.environ（不依赖 python-dotenv）      格式:       - KEY=VALUE

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): 从 .env 文件 + 环境变量 + kwargs 加载配置          优先级: kwargs > 环境变量 > .env 文件 > 类默认值

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): UIA 方式查找窗口（带超时）。          Desktop(backend="uia").windows() 在京麦窗口不存在时会遍历所有窗口，

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): 标题过滤，避免误命中 IDE、终端和无关小窗。

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): 过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): 检测系统里是否存在京麦相关句柄，包括最小化/离屏窗口。

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): 移动前强制释放鼠标键，防止残留按下态导致 move 变拖拽。

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): 仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanLi

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): 仿人点击：短暂停顿后执行原子 click，避免残留按下态。

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): 在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): 双击 - 单次前置激活 + 原子 doubleClick，避免按下态遗留。

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): 获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): 等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): 采集商品信息         url: 京东商品页 URL

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): 坐标自适应缩放：从参考分辨率映射到实际窗口尺寸。          坐标文件中的坐标基于 2560x1392，         实际窗口可能是任意尺寸（如

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): 刷新窗口矩形缓存，避免使用过期尺寸做坐标缩放。

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): LLM 识别图坐标 → 实际屏幕坐标。          LLM 返回的坐标基于识别图（1120x560），         需要先映射到参考分辨率（25

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (1): 查找京麦窗口（优先 UIA，fallback win32gui）

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): 优先使用当前前台大窗口，解决 jd_ 幽灵句柄误命中的问题。

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): UIA 方式查找窗口（带超时）。          Desktop(backend="uia").windows() 在京麦窗口不存在时会遍历所有窗口，

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (1): 标题过滤，避免误命中 IDE、终端和无关小窗。

### Community 72 - "Community 72"
Cohesion: 1.0
Nodes (1): 过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte

### Community 73 - "Community 73"
Cohesion: 1.0
Nodes (1): 检测系统里是否存在京麦相关句柄，包括最小化/离屏窗口。

### Community 74 - "Community 74"
Cohesion: 1.0
Nodes (1): 仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanL

### Community 75 - "Community 75"
Cohesion: 1.0
Nodes (1): 仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanLi

### Community 76 - "Community 76"
Cohesion: 1.0
Nodes (1): 仿人点击：短暂停顿后执行原子 click，避免残留按下态。

### Community 77 - "Community 77"
Cohesion: 1.0
Nodes (1): 在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击

### Community 78 - "Community 78"
Cohesion: 1.0
Nodes (1): 双击 - 单次前置激活 + 原子 doubleClick，避免按下态遗留。

### Community 79 - "Community 79"
Cohesion: 1.0
Nodes (1): 右键点击（自动缩放坐标）- 仿人移动+点击

### Community 80 - "Community 80"
Cohesion: 1.0
Nodes (1): 获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存

### Community 81 - "Community 81"
Cohesion: 1.0
Nodes (1): 等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d

### Community 82 - "Community 82"
Cohesion: 1.0
Nodes (1): Session 1 辅助程序 - 处理来自 cli 的命令

### Community 83 - "Community 83"
Cohesion: 1.0
Nodes (1): Session 1 辅助程序 - 处理来自 cli 的命令

### Community 84 - "Community 84"
Cohesion: 1.0
Nodes (1): 仿人点击：按下 → 随机按压时长 → 抬起 → 随机后停顿         参考 sightflow-desktop-agent 的 humanLikeCli

### Community 85 - "Community 85"
Cohesion: 1.0
Nodes (1): 在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击

### Community 86 - "Community 86"
Cohesion: 1.0
Nodes (1): 双击 - 单次前置激活 + 两次快速点击（40-100ms 间隔）

### Community 87 - "Community 87"
Cohesion: 1.0
Nodes (1): 右键点击（自动缩放坐标）- 仿人移动+点击

### Community 88 - "Community 88"
Cohesion: 1.0
Nodes (1): 获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存

### Community 89 - "Community 89"
Cohesion: 1.0
Nodes (1): 修复 _select_search_result 函数

### Community 90 - "Community 90"
Cohesion: 1.0
Nodes (1): 修复 _select_search_result 函数 - 使用正确的点击坐标

## Knowledge Gaps
- **116 isolated node(s):** `京麦商品发布自动化 - SQLAlchemy ORM 模型`, `Named Pipe 客户端 - 连接 Session1 Helper`, `快捷键，如 hotkey('ctrl', 'a')`, `按单个键，如 press('ENTER'), press('TAB')`, `京麦商品发布自动化 - JD 商品信息采集 从京东商品页采集标题、价格、类目等信息` (+111 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 14`** (5 nodes): `jingmai_coords.py`, `calc_price()`, `get_element()`, `print_elements()`, `京麦商品发布自动化 - 元素坐标配置 v3.0 基于实际截图分析 (2560x1392)  【重要】坐标来源说明： - 所有坐标均基于2560x1392分辨率截`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (4 nodes): `generate_vision_templates.py`, `CropSpec`, `main()`, `Generate lightweight vision fallback templates from v1 screenshots.  Only stable`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (2 nodes): `京麦商品发布自动化 - 坐标配置别名 对齐设计文档 config/coords.py 命名规范，实际坐标定义在 jingmai_coords.py`, `coords.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `标题过滤，避免误命中 IDE、终端和无关小窗。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `从 .env 文件 + 环境变量 + kwargs 加载配置          优先级: kwargs > 环境变量 > .env 文件 > 类默认值`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `从 .env 文件 + 环境变量 + kwargs 加载配置          优先级: kwargs > 环境变量 > .env 文件 > 类默认值`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `LLM 识别图坐标 → 实际屏幕坐标。          LLM 返回的坐标基于识别图（1120x560），         需要先映射到参考分辨率（25`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `查找京麦窗口（优先 UIA，fallback win32gui）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `优先使用当前前台大窗口，解决 jd_ 幽灵句柄误命中的问题。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `UIA 方式查找窗口（带超时）。          Desktop(backend="uia").windows() 在京麦窗口不存在时会遍历所有窗口，`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `标题过滤，避免误命中 IDE、终端和无关小窗。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `检测系统里是否存在京麦相关句柄，包括最小化/离屏窗口。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `移动前强制释放鼠标键，防止残留按下态导致 move 变拖拽。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanLi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `右键点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `双击 - 单次前置激活 + 原子 doubleClick，避免按下态遗留。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `右键点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `Scrape JD product basics plus detail assets from a product URL.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `Session 1 辅助程序 - 处理来自 cli 的命令`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `点击坐标（Session1 Helper）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `剪贴板粘贴（Session1 Helper，推荐用于中文）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `发送快捷键（Session1 Helper）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `按单个键（Session1 Helper）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `手动加载 .env 文件到 os.environ（不依赖 python-dotenv）      格式:       - KEY=VALUE`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `从 .env 文件 + 环境变量 + kwargs 加载配置          优先级: kwargs > 环境变量 > .env 文件 > 类默认值`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `UIA 方式查找窗口（带超时）。          Desktop(backend="uia").windows() 在京麦窗口不存在时会遍历所有窗口，`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `标题过滤，避免误命中 IDE、终端和无关小窗。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `检测系统里是否存在京麦相关句柄，包括最小化/离屏窗口。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `移动前强制释放鼠标键，防止残留按下态导致 move 变拖拽。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanLi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `仿人点击：短暂停顿后执行原子 click，避免残留按下态。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `双击 - 单次前置激活 + 原子 doubleClick，避免按下态遗留。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `采集商品信息         url: 京东商品页 URL`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `坐标自适应缩放：从参考分辨率映射到实际窗口尺寸。          坐标文件中的坐标基于 2560x1392，         实际窗口可能是任意尺寸（如`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `刷新窗口矩形缓存，避免使用过期尺寸做坐标缩放。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `LLM 识别图坐标 → 实际屏幕坐标。          LLM 返回的坐标基于识别图（1120x560），         需要先映射到参考分辨率（25`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `查找京麦窗口（优先 UIA，fallback win32gui）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `优先使用当前前台大窗口，解决 jd_ 幽灵句柄误命中的问题。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `UIA 方式查找窗口（带超时）。          Desktop(backend="uia").windows() 在京麦窗口不存在时会遍历所有窗口，`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `标题过滤，避免误命中 IDE、终端和无关小窗。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `检测系统里是否存在京麦相关句柄，包括最小化/离屏窗口。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanL`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanLi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `仿人点击：短暂停顿后执行原子 click，避免残留按下态。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (1 nodes): `在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 78`** (1 nodes): `双击 - 单次前置激活 + 原子 doubleClick，避免按下态遗留。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 79`** (1 nodes): `右键点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 80`** (1 nodes): `获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 81`** (1 nodes): `等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 82`** (1 nodes): `Session 1 辅助程序 - 处理来自 cli 的命令`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 83`** (1 nodes): `Session 1 辅助程序 - 处理来自 cli 的命令`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 84`** (1 nodes): `仿人点击：按下 → 随机按压时长 → 抬起 → 随机后停顿         参考 sightflow-desktop-agent 的 humanLikeCli`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 85`** (1 nodes): `在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 86`** (1 nodes): `双击 - 单次前置激活 + 两次快速点击（40-100ms 间隔）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 87`** (1 nodes): `右键点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 88`** (1 nodes): `获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 89`** (1 nodes): `修复 _select_search_result 函数`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 90`** (1 nodes): `修复 _select_search_result 函数 - 使用正确的点击坐标`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `JingmaiLocator` connect `Community 0` to `Community 1`, `Community 3`, `Community 4`, `Community 7`, `Community 8`, `Community 9`, `Community 10`?**
  _High betweenness centrality (0.225) - this node is a cross-community bridge._
- **Why does `BaseAgent` connect `Community 0` to `Community 2`, `Community 3`, `Community 4`, `Community 7`?**
  _High betweenness centrality (0.147) - this node is a cross-community bridge._
- **Why does `京麦商品发布自动化 - Memory Package` connect `Community 4` to `Community 0`, `Community 2`, `Community 3`, `Community 7`, `Community 8`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Are the 369 inferred relationships involving `JingmaiLocator` (e.g. with `SmartExecutor` and `SmartExecutor - 带截图验证的Executor 每个action执行前/后截图，用LLM视觉分析验证是否真正生效 失败重试3次，成功才执行下一步`) actually correct?**
  _`JingmaiLocator` has 369 INFERRED edges - model-reasoned connections that need verification._
- **Are the 287 inferred relationships involving `BaseAgent` (e.g. with `MemoryManager` and `MemoryType`) actually correct?**
  _`BaseAgent` has 287 INFERRED edges - model-reasoned connections that need verification._
- **Are the 99 inferred relationships involving `DatabaseManager` (e.g. with `兼容普通 UTF-8 和 UTF-8 BOM。` and `兼容完整计划包与旧版 steps-only 计划文件。`) actually correct?**
  _`DatabaseManager` has 99 INFERRED edges - model-reasoned connections that need verification._
- **Are the 79 inferred relationships involving `JDScraper` (e.g. with `兼容普通 UTF-8 和 UTF-8 BOM。` and `兼容完整计划包与旧版 steps-only 计划文件。`) actually correct?**
  _`JDScraper` has 79 INFERRED edges - model-reasoned connections that need verification._