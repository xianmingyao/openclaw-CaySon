# Graph Report - jingmai-product-publish  (2026-05-08)

## Corpus Check
- 58 files · ~261,225 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 884 nodes · 2476 edges · 29 communities detected
- Extraction: 53% EXTRACTED · 47% INFERRED · 0% AMBIGUOUS · INFERRED: 1171 edges (avg confidence: 0.65)
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

## God Nodes (most connected - your core abstractions)
1. `JingmaiLocator` - 117 edges
2. `BaseAgent` - 77 edges
3. `MemoryManager` - 59 edges
4. `DatabaseManager` - 58 edges
5. `ExecutorAgent` - 49 edges
6. `LLMManager` - 44 edges
7. `LongTermMemory` - 43 edges
8. `AgentFactory` - 42 edges
9. `MemoryType` - 41 edges
10. `ActionRegistry` - 37 edges

## Surprising Connections (you probably didn't know these)
- `_read_json_file()` --calls--> `test_read_json_file_supports_utf8_bom()`  [INFERRED]
  cli.py → tests\test_behavior.py
- `_load_batch_items()` --calls--> `test_load_batch_items_supports_xlsx()`  [INFERRED]
  cli.py → tests\test_behavior.py
- `_load_batch_items()` --calls--> `test_load_batch_items_supports_hunan_template_xlsx()`  [INFERRED]
  cli.py → tests\test_behavior.py
- `_build_product_model()` --calls--> `test_build_product_model_maps_new_fields()`  [INFERRED]
  cli.py → tests\test_behavior.py
- `_extract_plan_payload()` --calls--> `test_extract_plan_payload_supports_full_plan_and_steps_only()`  [INFERRED]
  cli.py → tests\test_behavior.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (88): AgentState, MemoryItem, MemoryStore, MemoryType, 京麦商品发布自动化 - Memory 存储基类与数据类型, Think 阶段：读取记忆 + LLM 分析，决定下一步动作         记忆参与决策：检索相关历史经验注入 LLM 上下文, Act 阶段：执行动作         子类必须覆写以定义具体执行逻辑, Observe 阶段：收集执行结果和环境反馈 (+80 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (105): BaseAgent, 京麦商品发布自动化 - Executor Agent (ReAct 执行循环)  三种经典范式协同工作（参考 DataWhale Hello-Agents, Plan-and-Solve: 每步完成后将计划状态写回文件          更新计划文件中对应步骤的 status/retries/screenshot, Plan-and-Solve: 每步完成后将计划状态写回文件          更新计划文件中对应步骤的 status/retries/screenshot, Plan-and-Solve: 每步完成后将计划状态写回文件          更新计划文件中对应步骤的 status/retries/screenshot, Executor 保持规则驱动，只回传当前动作。, 执行结束后回写计划包顶层状态，便于监控与断点续跑判断。, 执行结束后回写计划包顶层状态，便于监控与断点续跑判断。 (+97 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (45): LLMProvider, actions(), 京麦商品发布自动化 - Memory Package, LLMProvider, _configure_stdio(), get_logger(), init_logger(), JingmaiLogger (+37 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (81): debug_sku_all(), debug_sku_element(), _build_dropdown_keywords(), _click_dropdown_template(), click_element(), _collect_attribute_values(), _collect_price_area_anchors(), _collect_price_area_template_state() (+73 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (30): BaseAgent, Enum, ExecutorAgent, CheckResult, CircuitBreaker, CircuitBreakerState, JingmaiMonitor, MonitorState (+22 more)

### Community 5 - "Community 5"
Cohesion: 0.06
Nodes (48): batch(), _build_db(), _build_plan_package(), _build_product_model(), _build_progress_callback(), db_init(), _default_plan_path(), _detect_header_row_index() (+40 more)

### Community 6 - "Community 6"
Cohesion: 0.06
Nodes (60): _read_uia_value_for_field(), _verify_text_field(), _category_next_region(), _click_category_next(), _click_image_fallback(), _click_named_button(), _click_product_button(), _find_category_search_input() (+52 more)

### Community 7 - "Community 7"
Cohesion: 0.13
Nodes (12): create_client(), PipeClient, Named Pipe 客户端 - 连接 Session1 Helper, _get_client(), 剪贴板粘贴（Session1 Helper，推荐用于中文）, 发送快捷键（Session1 Helper）, 按单个键（Session1 Helper）, s1_hotkey() (+4 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (4): ABC, from_dict(), MemoryStore, ShortTermMemory

### Community 9 - "Community 9"
Cohesion: 0.19
Nodes (5): log(), Session 1 辅助程序 - 处理来自 cli 的命令, release_mouse_buttons(), runtime_log(), Session1Helper

### Community 10 - "Community 10"
Cohesion: 0.27
Nodes (9): find_descendants(), _get_cache_request(), _get_control_filter_condition(), _get_uia_control_id_map(), _get_uia_control_name_map(), _get_uia_defs(), Fast UIA control inspection adapted from UFO's cached UIA backend., UIAElementInfoFix (+1 more)

### Community 11 - "Community 11"
Cohesion: 0.36
Nodes (3): create_smart_executor(), SmartExecutor - 带截图验证的Executor 每个action执行前/后截图，用LLM视觉分析验证是否真正生效 失败重试3次，成功才执行下一步, SmartExecutor

### Community 12 - "Community 12"
Cohesion: 0.4
Nodes (8): _click_popup_button(), _click_template(), dismiss_cef_popup(), dismiss_popup(), _get_locator(), handle_dialog(), 京麦商品发布自动化 - 弹窗恢复 Actions 优先走轻量交互与 UIA，只有关键按钮才接视觉兜底。, test_dismiss_popup_prefers_uia_button()

### Community 13 - "Community 13"
Cohesion: 0.39
Nodes (8): Exception, ActionFailedError, DatabaseError, ElementNotFoundError, JingmaiError, LLMError, MemoryError, WindowNotFoundError

### Community 14 - "Community 14"
Cohesion: 0.5
Nodes (3): Path validation utilities adapted from UFO for safe local save paths., validate_path_not_sensitive(), validate_save_path()

### Community 15 - "Community 15"
Cohesion: 0.5
Nodes (2): CropSpec, Generate lightweight vision fallback templates from v1 screenshots.  Only stable

### Community 19 - "Community 19"
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
Nodes (1): Session 1 辅助程序 - 处理来自 cli 的命令

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): Session 1 辅助程序 - 处理来自 cli 的命令

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): 仿人点击：按下 → 随机按压时长 → 抬起 → 随机后停顿         参考 sightflow-desktop-agent 的 humanLikeCli

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): 在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): 双击 - 单次前置激活 + 两次快速点击（40-100ms 间隔）

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): 右键点击（自动缩放坐标）- 仿人移动+点击

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): 获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): 等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): 修复 _select_search_result 函数

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): 修复 _select_search_result 函数 - 使用正确的点击坐标

## Knowledge Gaps
- **61 isolated node(s):** `京麦商品发布自动化 - SQLAlchemy ORM 模型`, `Named Pipe 客户端 - 连接 Session1 Helper`, `快捷键，如 hotkey('ctrl', 'a')`, `按单个键，如 press('ENTER'), press('TAB')`, `京麦商品发布自动化 - JD 商品信息采集 从京东商品页采集标题、价格、类目等信息` (+56 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 15`** (4 nodes): `generate_vision_templates.py`, `CropSpec`, `main()`, `Generate lightweight vision fallback templates from v1 screenshots.  Only stable`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (2 nodes): `京麦商品发布自动化 - 坐标配置别名 对齐设计文档 config/coords.py 命名规范，实际坐标定义在 jingmai_coords.py`, `coords.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `标题过滤，避免误命中 IDE、终端和无关小窗。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `Session 1 辅助程序 - 处理来自 cli 的命令`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `Session 1 辅助程序 - 处理来自 cli 的命令`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `仿人点击：按下 → 随机按压时长 → 抬起 → 随机后停顿         参考 sightflow-desktop-agent 的 humanLikeCli`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `在窗口坐标处点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `双击 - 单次前置激活 + 两次快速点击（40-100ms 间隔）`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `右键点击（自动缩放坐标）- 仿人移动+点击`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `获取京麦 UIA 窗口对象（带 5s TTL 缓存，避免重复遍历）         参考 sightflow window-utils.ts 的窗口信息缓存`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `等待页面稳定（通过连续截图像素 hash 变化检测）         参考 sightflow image-compare.ts 的 pixelmatch d`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `修复 _select_search_result 函数`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `修复 _select_search_result 函数 - 使用正确的点击坐标`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `JingmaiLocator` connect `Community 1` to `Community 0`, `Community 2`, `Community 3`, `Community 4`, `Community 6`, `Community 11`, `Community 12`?**
  _High betweenness centrality (0.191) - this node is a cross-community bridge._
- **Why does `京麦商品发布自动化 - Memory Package` connect `Community 2` to `Community 0`, `Community 1`, `Community 4`, `Community 8`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Why does `BaseAgent` connect `Community 1` to `Community 8`, `Community 0`, `Community 2`, `Community 4`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Are the 87 inferred relationships involving `JingmaiLocator` (e.g. with `SmartExecutor` and `SmartExecutor - 带截图验证的Executor 每个action执行前/后截图，用LLM视觉分析验证是否真正生效 失败重试3次，成功才执行下一步`) actually correct?**
  _`JingmaiLocator` has 87 INFERRED edges - model-reasoned connections that need verification._
- **Are the 58 inferred relationships involving `BaseAgent` (e.g. with `MemoryManager` and `MemoryType`) actually correct?**
  _`BaseAgent` has 58 INFERRED edges - model-reasoned connections that need verification._
- **Are the 44 inferred relationships involving `MemoryManager` (e.g. with `兼容普通 UTF-8 和 UTF-8 BOM。` and `兼容完整计划包与旧版 steps-only 计划文件。`) actually correct?**
  _`MemoryManager` has 44 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `DatabaseManager` (e.g. with `兼容普通 UTF-8 和 UTF-8 BOM。` and `兼容完整计划包与旧版 steps-only 计划文件。`) actually correct?**
  _`DatabaseManager` has 42 INFERRED edges - model-reasoned connections that need verification._