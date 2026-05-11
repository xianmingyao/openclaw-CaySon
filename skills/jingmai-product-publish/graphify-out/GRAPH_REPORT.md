# Graph Report - jingmai-product-publish  (2026-05-11)

## Corpus Check
- 63 files · ~179,467 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1090 nodes · 3085 edges · 68 communities detected
- Extraction: 47% EXTRACTED · 53% INFERRED · 0% AMBIGUOUS · INFERRED: 1621 edges (avg confidence: 0.63)
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
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 21|Community 21]]
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

## God Nodes (most connected - your core abstractions)
1. `JingmaiLocator` - 205 edges
2. `BaseAgent` - 145 edges
3. `MemoryManager` - 75 edges
4. `DatabaseManager` - 74 edges
5. `JDScraper` - 65 edges
6. `ExecutorAgent` - 64 edges
7. `LLMManager` - 60 edges
8. `LongTermMemory` - 59 edges
9. `AgentFactory` - 58 edges
10. `MemoryType` - 57 edges

## Surprising Connections (you probably didn't know these)
- `_enrich_product_from_source()` --calls--> `test_cli_enrich_product_from_source_merges_scraped_detail()`  [INFERRED]
  cli.py → tests\test_scraper_enrichment.py
- `DatabaseManager` --uses--> `京麦商品发布自动化 - 数据库初始化脚本 建表 + 验证连接`  [INFERRED]
  db.py → init_db.py
- `SmartExecutor - 带截图验证的Executor 每个action执行前/后截图，用LLM视觉分析验证是否真正生效 失败重试3次，成功才执行下一步` --uses--> `JingmaiLocator`  [INFERRED]
  smart_executor.py → infrastructure\locator.py
- `fill_text()` --calls--> `test_fill_text_fails_when_focus_click_fails()`  [INFERRED]
  actions\form.py → tests\test_behavior.py
- `_price_area_ready()` --calls--> `test_price_area_ready_accepts_text_anchor_fallback()`  [INFERRED]
  actions\form.py → tests\test_behavior.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.02
Nodes (174): BaseAgent, 按 product_id upsert 商品。, 京麦商品发布自动化 - Executor Agent (ReAct 执行循环)  三种经典范式协同工作（参考 DataWhale Hello-Agents, 本地恢复窗口上下文：find_window → activate_window。, Plan-and-Solve: 每步完成后将计划状态写回文件          更新计划文件中对应步骤的 status/retries/screenshot, 调用 LLM 做视觉验证          Returns:             dict: {"status": "ok"|"error"|"unk, 调用 LLM 做视觉验证          Returns:             dict: {"status": "ok"|"error"|"unk, Plan-and-Solve: 每步完成后将计划状态写回文件          更新计划文件中对应步骤的 status/retries/screenshot (+166 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (84): ABC, AgentState, from_dict(), MemoryItem, MemoryStore, MemoryType, 京麦商品发布自动化 - Memory 存储基类与数据类型, Think 阶段：读取记忆 + LLM 分析，决定下一步动作         记忆参与决策：检索相关历史经验注入 LLM 上下文 (+76 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (71): BaseAgent, _build_plan_package(), think(), _build_precheck_action_hint(), ExecutorAgent, _iter_json_repair_candidates(), 查找京麦窗口（优先 UIA，fallback win32gui）, WindowInfo (+63 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (104): debug_sku_all(), debug_sku_element(), _build_description_html(), _build_dropdown_keywords(), _click_dropdown_template(), click_element(), _collect_attribute_values(), _collect_price_area_anchors() (+96 more)

### Community 4 - "Community 4"
Cohesion: 0.03
Nodes (49): LLMProvider, Enum, 京麦商品发布自动化 - Memory Package, LLMProvider, _configure_stdio(), get_logger(), init_logger(), JingmaiLogger (+41 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (45): actions(), _annotate_publish_mode(), batch(), _build_product_model(), _build_progress_callback(), db_init(), _default_plan_path(), _default_workflow_doc_path() (+37 more)

### Community 6 - "Community 6"
Cohesion: 0.11
Nodes (43): _find_labeled_dropdown_center(), _build_category_disabled_reason(), _category_depth(), _category_next_region(), _click_category_next(), _click_image_fallback(), click_modify(), _click_named_button() (+35 more)

### Community 7 - "Community 7"
Cohesion: 0.07
Nodes (9): memory_create(), memory_search(), UIA 方式查找窗口（带超时）。          Desktop(backend="uia").windows() 在京麦窗口不存在时会遍历所有窗口，, 获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存, CircuitBreaker, 熔断器 — 借鉴 jingmai-putaway base.py, test_infrastructure(), test_memory_manager() (+1 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (18): _resolve_agent_type(), _annotate_plan_phases(), _attach_react_contracts(), _build_required_visual_fields(), _canonicalize_publish_plan(), _enforce_plan_order(), PlannerAgent, list_actions() (+10 more)

### Community 9 - "Community 9"
Cohesion: 0.07
Nodes (23): list_tasks(), ElementPosition, _get_process_name(), _is_excluded_title(), _is_matching_title(), _is_usable_rect(), _print_window_capture(), 京麦商品发布自动化 - 双引擎元素定位器 UIA 元素查找 + 坐标 fallback (+15 more)

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (5): test_scraper(), _FakeResponse, test_cli_enrich_product_from_source_merges_scraped_detail(), test_scraper_falls_back_to_opencli_after_playwright(), test_scraper_html_path_collects_detail_assets()

### Community 11 - "Community 11"
Cohesion: 0.16
Nodes (10): auto_discover(), execute(), get(), list_categories(), Action registry and execution hooks., summary(), create_smart_executor(), SmartExecutor - 带截图验证的Executor 每个action执行前/后截图，用LLM视觉分析验证是否真正生效 失败重试3次，成功才执行下一步 (+2 more)

### Community 12 - "Community 12"
Cohesion: 0.23
Nodes (3): create_client(), PipeClient, Named Pipe 客户端 - 连接 Session1 Helper

### Community 13 - "Community 13"
Cohesion: 0.27
Nodes (9): find_descendants(), _get_cache_request(), _get_control_filter_condition(), _get_uia_control_id_map(), _get_uia_control_name_map(), _get_uia_defs(), Fast UIA control inspection adapted from UFO's cached UIA backend., UIAElementInfoFix (+1 more)

### Community 14 - "Community 14"
Cohesion: 0.39
Nodes (8): Exception, ActionFailedError, DatabaseError, ElementNotFoundError, JingmaiError, LLMError, MemoryError, WindowNotFoundError

### Community 15 - "Community 15"
Cohesion: 0.4
Nodes (2): get_element(), 京麦商品发布自动化 - 元素坐标配置 v3.0 基于实际截图分析 (2560x1392)  【重要】坐标来源说明： - 所有坐标均基于2560x1392分辨率截

### Community 16 - "Community 16"
Cohesion: 0.5
Nodes (3): Path validation utilities adapted from UFO for safe local save paths., validate_path_not_sensitive(), validate_save_path()

### Community 17 - "Community 17"
Cohesion: 0.5
Nodes (2): CropSpec, Generate lightweight vision fallback templates from v1 screenshots.  Only stable

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): 京麦商品发布自动化 - 坐标配置别名 对齐设计文档 config/coords.py 命名规范，实际坐标定义在 jingmai_coords.py

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): 标题过滤，避免误命中 IDE、终端和无关小窗。

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): 过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): Scrape JD product basics plus detail assets from a product URL.

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Session 1 辅助程序 - 处理来自 cli 的命令

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): 点击坐标（Session1 Helper）

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): 剪贴板粘贴（Session1 Helper，推荐用于中文）

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): 发送快捷键（Session1 Helper）

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): 按单个键（Session1 Helper）

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): 手动加载 .env 文件到 os.environ（不依赖 python-dotenv）      格式:       - KEY=VALUE

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): 从 .env 文件 + 环境变量 + kwargs 加载配置          优先级: kwargs > 环境变量 > .env 文件 > 类默认值

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): UIA 方式查找窗口（带超时）。          Desktop(backend="uia").windows() 在京麦窗口不存在时会遍历所有窗口，

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): 标题过滤，避免误命中 IDE、终端和无关小窗。

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): 过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): 检测系统里是否存在京麦相关句柄，包括最小化/离屏窗口。

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (1): 移动前强制释放鼠标键，防止残留按下态导致 move 变拖拽。

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (1): 仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanLi

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): 仿人点击：短暂停顿后执行原子 click，避免残留按下态。

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): 在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): 双击 - 单次前置激活 + 原子 doubleClick，避免按下态遗留。

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): 获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): 等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): 采集商品信息         url: 京东商品页 URL

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): 坐标自适应缩放：从参考分辨率映射到实际窗口尺寸。          坐标文件中的坐标基于 2560x1392，         实际窗口可能是任意尺寸（如

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): 刷新窗口矩形缓存，避免使用过期尺寸做坐标缩放。

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): LLM 识别图坐标 → 实际屏幕坐标。          LLM 返回的坐标基于识别图（1120x560），         需要先映射到参考分辨率（25

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): 查找京麦窗口（优先 UIA，fallback win32gui）

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): 优先使用当前前台大窗口，解决 jd_ 幽灵句柄误命中的问题。

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): UIA 方式查找窗口（带超时）。          Desktop(backend="uia").windows() 在京麦窗口不存在时会遍历所有窗口，

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): 标题过滤，避免误命中 IDE、终端和无关小窗。

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): 过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): 检测系统里是否存在京麦相关句柄，包括最小化/离屏窗口。

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): 仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanL

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): 仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanLi

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): 仿人点击：短暂停顿后执行原子 click，避免残留按下态。

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): 在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): 双击 - 单次前置激活 + 原子 doubleClick，避免按下态遗留。

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): 右键点击（自动缩放坐标）- 仿人移动+点击

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): 获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): 等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): Session 1 辅助程序 - 处理来自 cli 的命令

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (1): Session 1 辅助程序 - 处理来自 cli 的命令

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): 仿人点击：按下 → 随机按压时长 → 抬起 → 随机后停顿         参考 sightflow-desktop-agent 的 humanLikeCli

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): 在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (1): 双击 - 单次前置激活 + 两次快速点击（40-100ms 间隔）

### Community 72 - "Community 72"
Cohesion: 1.0
Nodes (1): 右键点击（自动缩放坐标）- 仿人移动+点击

### Community 73 - "Community 73"
Cohesion: 1.0
Nodes (1): 获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存

### Community 74 - "Community 74"
Cohesion: 1.0
Nodes (1): 等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d

### Community 75 - "Community 75"
Cohesion: 1.0
Nodes (1): 修复 _select_search_result 函数

### Community 76 - "Community 76"
Cohesion: 1.0
Nodes (1): 修复 _select_search_result 函数 - 使用正确的点击坐标

## Knowledge Gaps
- **93 isolated node(s):** `京麦商品发布自动化 - SQLAlchemy ORM 模型`, `Named Pipe 客户端 - 连接 Session1 Helper`, `快捷键，如 hotkey('ctrl', 'a')`, `按单个键，如 press('ENTER'), press('TAB')`, `京麦商品发布自动化 - JD 商品信息采集 从京东商品页采集标题、价格、类目等信息` (+88 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 15`** (5 nodes): `jingmai_coords.py`, `calc_price()`, `get_element()`, `print_elements()`, `京麦商品发布自动化 - 元素坐标配置 v3.0 基于实际截图分析 (2560x1392)  【重要】坐标来源说明： - 所有坐标均基于2560x1392分辨率截`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (4 nodes): `generate_vision_templates.py`, `CropSpec`, `main()`, `Generate lightweight vision fallback templates from v1 screenshots.  Only stable`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (2 nodes): `京麦商品发布自动化 - 坐标配置别名 对齐设计文档 config/coords.py 命名规范，实际坐标定义在 jingmai_coords.py`, `coords.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `标题过滤，避免误命中 IDE、终端和无关小窗。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `Scrape JD product basics plus detail assets from a product URL.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Session 1 辅助程序 - 处理来自 cli 的命令`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `点击坐标（Session1 Helper）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `剪贴板粘贴（Session1 Helper，推荐用于中文）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `发送快捷键（Session1 Helper）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `按单个键（Session1 Helper）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `手动加载 .env 文件到 os.environ（不依赖 python-dotenv）      格式:       - KEY=VALUE`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `从 .env 文件 + 环境变量 + kwargs 加载配置          优先级: kwargs > 环境变量 > .env 文件 > 类默认值`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `UIA 方式查找窗口（带超时）。          Desktop(backend="uia").windows() 在京麦窗口不存在时会遍历所有窗口，`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `标题过滤，避免误命中 IDE、终端和无关小窗。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `检测系统里是否存在京麦相关句柄，包括最小化/离屏窗口。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `移动前强制释放鼠标键，防止残留按下态导致 move 变拖拽。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanLi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `仿人点击：短暂停顿后执行原子 click，避免残留按下态。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `双击 - 单次前置激活 + 原子 doubleClick，避免按下态遗留。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `采集商品信息         url: 京东商品页 URL`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `坐标自适应缩放：从参考分辨率映射到实际窗口尺寸。          坐标文件中的坐标基于 2560x1392，         实际窗口可能是任意尺寸（如`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `刷新窗口矩形缓存，避免使用过期尺寸做坐标缩放。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `LLM 识别图坐标 → 实际屏幕坐标。          LLM 返回的坐标基于识别图（1120x560），         需要先映射到参考分辨率（25`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `查找京麦窗口（优先 UIA，fallback win32gui）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `优先使用当前前台大窗口，解决 jd_ 幽灵句柄误命中的问题。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `UIA 方式查找窗口（带超时）。          Desktop(backend="uia").windows() 在京麦窗口不存在时会遍历所有窗口，`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `标题过滤，避免误命中 IDE、终端和无关小窗。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `检测系统里是否存在京麦相关句柄，包括最小化/离屏窗口。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanL`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanLi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `仿人点击：短暂停顿后执行原子 click，避免残留按下态。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `双击 - 单次前置激活 + 原子 doubleClick，避免按下态遗留。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `右键点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `Session 1 辅助程序 - 处理来自 cli 的命令`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `Session 1 辅助程序 - 处理来自 cli 的命令`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `仿人点击：按下 → 随机按压时长 → 抬起 → 随机后停顿         参考 sightflow-desktop-agent 的 humanLikeCli`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `双击 - 单次前置激活 + 两次快速点击（40-100ms 间隔）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `右键点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `修复 _select_search_result 函数`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `修复 _select_search_result 函数 - 使用正确的点击坐标`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `JingmaiLocator` connect `Community 0` to `Community 2`, `Community 3`, `Community 4`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 11`?**
  _High betweenness centrality (0.219) - this node is a cross-community bridge._
- **Why does `BaseAgent` connect `Community 0` to `Community 1`, `Community 2`, `Community 4`, `Community 7`, `Community 8`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Why does `京麦商品发布自动化 - Memory Package` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`, `Community 7`, `Community 8`, `Community 9`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Are the 173 inferred relationships involving `JingmaiLocator` (e.g. with `SmartExecutor` and `SmartExecutor - 带截图验证的Executor 每个action执行前/后截图，用LLM视觉分析验证是否真正生效 失败重试3次，成功才执行下一步`) actually correct?**
  _`JingmaiLocator` has 173 INFERRED edges - model-reasoned connections that need verification._
- **Are the 126 inferred relationships involving `BaseAgent` (e.g. with `MemoryManager` and `MemoryType`) actually correct?**
  _`BaseAgent` has 126 INFERRED edges - model-reasoned connections that need verification._
- **Are the 60 inferred relationships involving `MemoryManager` (e.g. with `兼容普通 UTF-8 和 UTF-8 BOM。` and `兼容完整计划包与旧版 steps-only 计划文件。`) actually correct?**
  _`MemoryManager` has 60 INFERRED edges - model-reasoned connections that need verification._
- **Are the 58 inferred relationships involving `DatabaseManager` (e.g. with `兼容普通 UTF-8 和 UTF-8 BOM。` and `兼容完整计划包与旧版 steps-only 计划文件。`) actually correct?**
  _`DatabaseManager` has 58 INFERRED edges - model-reasoned connections that need verification._