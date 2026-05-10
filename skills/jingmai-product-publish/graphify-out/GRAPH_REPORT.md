# Graph Report - jingmai-product-publish  (2026-05-11)

## Corpus Check
- 64 files · ~470,583 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1042 nodes · 2938 edges · 46 communities detected
- Extraction: 49% EXTRACTED · 51% INFERRED · 0% AMBIGUOUS · INFERRED: 1486 edges (avg confidence: 0.64)
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
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 25|Community 25]]
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

## God Nodes (most connected - your core abstractions)
1. `JingmaiLocator` - 179 edges
2. `BaseAgent` - 127 edges
3. `MemoryManager` - 66 edges
4. `DatabaseManager` - 65 edges
5. `ExecutorAgent` - 59 edges
6. `JDScraper` - 51 edges
7. `LLMManager` - 51 edges
8. `LongTermMemory` - 50 edges
9. `AgentFactory` - 49 edges
10. `MemoryType` - 48 edges

## Surprising Connections (you probably didn't know these)
- `_read_json_file()` --calls--> `test_read_json_file_supports_utf8_bom()`  [INFERRED]
  cli.py → tests\test_behavior.py
- `_load_batch_items()` --calls--> `test_load_batch_items_supports_xlsx()`  [INFERRED]
  cli.py → tests\test_behavior.py
- `_load_batch_items()` --calls--> `test_load_batch_items_supports_hunan_template_xlsx()`  [INFERRED]
  cli.py → tests\test_behavior.py
- `test_cli_enrich_product_from_source_merges_scraped_detail()` --calls--> `_enrich_product_from_source()`  [INFERRED]
  tests\test_scraper_enrichment.py → cli.py
- `_build_product_model()` --calls--> `test_build_product_model_maps_new_fields()`  [INFERRED]
  cli.py → tests\test_behavior.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (82): ABC, AgentState, from_dict(), MemoryItem, MemoryStore, MemoryType, 京麦商品发布自动化 - Memory 存储基类与数据类型, Think 阶段：读取记忆 + LLM 分析，决定下一步动作         记忆参与决策：检索相关历史经验注入 LLM 上下文 (+74 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (148): BaseAgent, 京麦商品发布自动化 - Executor Agent (ReAct 执行循环)  三种经典范式协同工作（参考 DataWhale Hello-Agents, Plan-and-Solve: 每步完成后将计划状态写回文件          更新计划文件中对应步骤的 status/retries/screenshot, 调用 LLM 做视觉验证          Returns:             dict: {"status": "ok"|"error"|"unk, 调用 LLM 做视觉验证          Returns:             dict: {"status": "ok"|"error"|"unk, Plan-and-Solve: 每步完成后将计划状态写回文件          更新计划文件中对应步骤的 status/retries/screenshot, Plan-and-Solve: 每步完成后将计划状态写回文件          更新计划文件中对应步骤的 status/retries/screenshot, Executor 保持规则驱动，只回传当前动作。 (+140 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (68): BaseAgent, _build_precheck_action_hint(), ExecutorAgent, _iter_json_repair_candidates(), _price_area_ready(), _verify_text_field(), _LLMReturning, test_batch_plan_out_creates_one_plan_file_per_task() (+60 more)

### Community 3 - "Community 3"
Cohesion: 0.03
Nodes (47): LLMProvider, actions(), LLMProvider, _configure_stdio(), get_logger(), init_logger(), JingmaiLogger, 京麦商品发布自动化 - 日志模块 从 scripts/jingmai_logger.py 迁移，保持接口兼容 (+39 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (86): debug_sku_all(), debug_sku_element(), _build_description_html(), _build_dropdown_keywords(), _click_dropdown_template(), _collect_attribute_values(), _collect_price_area_anchors(), _collect_price_area_template_state() (+78 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (53): batch(), _build_db(), _build_plan_package(), _build_product_model(), _build_progress_callback(), db_init(), _default_plan_path(), _detect_header_row_index() (+45 more)

### Community 6 - "Community 6"
Cohesion: 0.04
Nodes (36): ElementPosition, _get_process_name(), _is_excluded_title(), _is_matching_title(), _is_usable_rect(), _print_window_capture(), 京麦商品发布自动化 - 双引擎元素定位器 UIA 元素查找 + 坐标 fallback, 刷新窗口矩形缓存，避免使用过期尺寸做坐标缩放。 (+28 more)

### Community 7 - "Community 7"
Cohesion: 0.1
Nodes (47): click_element(), _find_labeled_dropdown_center(), wait_and_click(), _build_category_disabled_reason(), _category_next_region(), _click_category_next(), _click_image_fallback(), click_modify() (+39 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (11): Enum, 京麦商品发布自动化 - Memory Package, CheckResult, CircuitBreaker, CircuitBreakerState, JingmaiMonitor, MonitorState, 京麦商品发布自动化 - 重试 + 熔断器 从 scripts/jingmai_monitor.py 迁移，新增 CircuitBreaker (+3 more)

### Community 9 - "Community 9"
Cohesion: 0.13
Nodes (12): create_client(), PipeClient, Named Pipe 客户端 - 连接 Session1 Helper, _get_client(), 剪贴板粘贴（Session1 Helper，推荐用于中文）, 发送快捷键（Session1 Helper）, 按单个键（Session1 Helper）, s1_hotkey() (+4 more)

### Community 10 - "Community 10"
Cohesion: 0.13
Nodes (8): _read_uia_value_for_field(), 获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存, log(), Session 1 辅助程序 - 处理来自 cli 的命令, release_mouse_buttons(), runtime_log(), Session1Helper, test_read_uia_value_prefers_local_candidates()

### Community 11 - "Community 11"
Cohesion: 0.16
Nodes (10): auto_discover(), execute(), get(), list_categories(), Action registry and execution hooks., summary(), create_smart_executor(), SmartExecutor - 带截图验证的Executor 每个action执行前/后截图，用LLM视觉分析验证是否真正生效 失败重试3次，成功才执行下一步 (+2 more)

### Community 12 - "Community 12"
Cohesion: 0.27
Nodes (9): find_descendants(), _get_cache_request(), _get_control_filter_condition(), _get_uia_control_id_map(), _get_uia_control_name_map(), _get_uia_defs(), Fast UIA control inspection adapted from UFO's cached UIA backend., UIAElementInfoFix (+1 more)

### Community 13 - "Community 13"
Cohesion: 0.39
Nodes (8): Exception, ActionFailedError, DatabaseError, ElementNotFoundError, JingmaiError, LLMError, MemoryError, WindowNotFoundError

### Community 14 - "Community 14"
Cohesion: 0.5
Nodes (2): CropSpec, Generate lightweight vision fallback templates from v1 screenshots.  Only stable

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): 京麦商品发布自动化 - 坐标配置别名 对齐设计文档 config/coords.py 命名规范，实际坐标定义在 jingmai_coords.py

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): 标题过滤，避免误命中 IDE、终端和无关小窗。

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): 过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (1): 采集商品信息         url: 京东商品页 URL

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): 坐标自适应缩放：从参考分辨率映射到实际窗口尺寸。          坐标文件中的坐标基于 2560x1392，         实际窗口可能是任意尺寸（如

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): 刷新窗口矩形缓存，避免使用过期尺寸做坐标缩放。

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
Nodes (1): 仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanL

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): 仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanLi

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): 仿人点击：短暂停顿后执行原子 click，避免残留按下态。

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
Nodes (1): Session 1 辅助程序 - 处理来自 cli 的命令

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Session 1 辅助程序 - 处理来自 cli 的命令

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): 仿人点击：按下 → 随机按压时长 → 抬起 → 随机后停顿         参考 sightflow-desktop-agent 的 humanLikeCli

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): 在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): 双击 - 单次前置激活 + 两次快速点击（40-100ms 间隔）

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): 右键点击（自动缩放坐标）- 仿人移动+点击

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): 获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): 等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): 修复 _select_search_result 函数

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): 修复 _select_search_result 函数 - 使用正确的点击坐标

## Knowledge Gaps
- **79 isolated node(s):** `京麦商品发布自动化 - SQLAlchemy ORM 模型`, `Named Pipe 客户端 - 连接 Session1 Helper`, `快捷键，如 hotkey('ctrl', 'a')`, `按单个键，如 press('ENTER'), press('TAB')`, `京麦商品发布自动化 - JD 商品信息采集 从京东商品页采集标题、价格、类目等信息` (+74 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 14`** (4 nodes): `generate_vision_templates.py`, `CropSpec`, `main()`, `Generate lightweight vision fallback templates from v1 screenshots.  Only stable`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (2 nodes): `京麦商品发布自动化 - 坐标配置别名 对齐设计文档 config/coords.py 命名规范，实际坐标定义在 jingmai_coords.py`, `coords.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `标题过滤，避免误命中 IDE、终端和无关小窗。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `采集商品信息         url: 京东商品页 URL`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `坐标自适应缩放：从参考分辨率映射到实际窗口尺寸。          坐标文件中的坐标基于 2560x1392，         实际窗口可能是任意尺寸（如`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `刷新窗口矩形缓存，避免使用过期尺寸做坐标缩放。`
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
- **Thin community `Community 37`** (1 nodes): `仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanL`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `仿人鼠标移动：三次贝塞尔曲线 + Ease Out 缓动 + 随机抖动         参考 sightflow-desktop-agent 的 humanLi`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `仿人点击：短暂停顿后执行原子 click，避免残留按下态。`
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
- **Thin community `Community 45`** (1 nodes): `Session 1 辅助程序 - 处理来自 cli 的命令`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `Session 1 辅助程序 - 处理来自 cli 的命令`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `仿人点击：按下 → 随机按压时长 → 抬起 → 随机后停顿         参考 sightflow-desktop-agent 的 humanLikeCli`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `双击 - 单次前置激活 + 两次快速点击（40-100ms 间隔）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `右键点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `修复 _select_search_result 函数`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `修复 _select_search_result 函数 - 使用正确的点击坐标`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `JingmaiLocator` connect `Community 1` to `Community 2`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 10`, `Community 11`?**
  _High betweenness centrality (0.210) - this node is a cross-community bridge._
- **Why does `京麦商品发布自动化 - Memory Package` connect `Community 8` to `Community 0`, `Community 1`, `Community 2`, `Community 3`, `Community 5`, `Community 6`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Why does `BaseAgent` connect `Community 1` to `Community 0`, `Community 2`, `Community 5`, `Community 8`, `Community 10`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Are the 149 inferred relationships involving `JingmaiLocator` (e.g. with `SmartExecutor` and `SmartExecutor - 带截图验证的Executor 每个action执行前/后截图，用LLM视觉分析验证是否真正生效 失败重试3次，成功才执行下一步`) actually correct?**
  _`JingmaiLocator` has 149 INFERRED edges - model-reasoned connections that need verification._
- **Are the 108 inferred relationships involving `BaseAgent` (e.g. with `MemoryManager` and `MemoryType`) actually correct?**
  _`BaseAgent` has 108 INFERRED edges - model-reasoned connections that need verification._
- **Are the 51 inferred relationships involving `MemoryManager` (e.g. with `兼容普通 UTF-8 和 UTF-8 BOM。` and `兼容完整计划包与旧版 steps-only 计划文件。`) actually correct?**
  _`MemoryManager` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 49 inferred relationships involving `DatabaseManager` (e.g. with `兼容普通 UTF-8 和 UTF-8 BOM。` and `兼容完整计划包与旧版 steps-only 计划文件。`) actually correct?**
  _`DatabaseManager` has 49 INFERRED edges - model-reasoned connections that need verification._