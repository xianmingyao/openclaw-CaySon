# Graph Report - jingmai-product-publish  (2026-05-07)

## Corpus Check
- 51 files · ~486,043 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 699 nodes · 1916 edges · 20 communities detected
- Extraction: 53% EXTRACTED · 47% INFERRED · 0% AMBIGUOUS · INFERRED: 891 edges (avg confidence: 0.67)
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
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]

## God Nodes (most connected - your core abstractions)
1. `JingmaiLocator` - 72 edges
2. `MemoryManager` - 52 edges
3. `DatabaseManager` - 51 edges
4. `BaseAgent` - 48 edges
5. `ExecutorAgent` - 46 edges
6. `LLMManager` - 37 edges
7. `LongTermMemory` - 36 edges
8. `AgentFactory` - 35 edges
9. `京麦商品发布自动化 - Memory Package` - 34 edges
10. `MemoryType` - 34 edges

## Surprising Connections (you probably didn't know these)
- `_read_json_file()` --calls--> `test_read_json_file_supports_utf8_bom()`  [INFERRED]
  cli.py → tests\test_behavior.py
- `_load_batch_items()` --calls--> `test_load_batch_items_supports_xlsx()`  [INFERRED]
  cli.py → tests\test_behavior.py
- `_build_product_model()` --calls--> `test_build_product_model_maps_new_fields()`  [INFERRED]
  cli.py → tests\test_behavior.py
- `_extract_plan_payload()` --calls--> `test_extract_plan_payload_supports_full_plan_and_steps_only()`  [INFERRED]
  cli.py → tests\test_behavior.py
- `_build_plan_package()` --calls--> `test_build_plan_package_includes_phase_summary()`  [INFERRED]
  cli.py → tests\test_behavior.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (58): ABC, AgentState, from_dict(), MemoryItem, MemoryStore, MemoryType, 京麦商品发布自动化 - Memory 存储基类与数据类型, Think 阶段：读取记忆 + LLM 分析，决定下一步动作         记忆参与决策：检索相关历史经验注入 LLM 上下文 (+50 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (96): _build_dropdown_keywords(), _click_dropdown_template(), click_element(), _collect_attribute_values(), _compare_field_value(), fill_product_info(), _fill_supported_attributes(), fill_text() (+88 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (31): BaseAgent, ExecutorAgent, 京麦商品发布自动化 - Executor Agent (ReAct 执行循环)  三种经典范式协同工作（参考 DataWhale Hello-Agents, Executor 保持规则驱动，只回传当前动作。, ReAct 执行主循环 — 每步 Act → Screenshot → Observe → Reflect          参考 DataWhare He, 执行 Agent — ReAct 循环（每步截图 + 视觉验证 + 递进重试）, ReAct Observation 阶段 — 截图 + LLM 视觉分析          参考 ReAct 范式的 Observation: 收集执行结果, 执行前验证 locator.hwnd 有效，无效则自动重定位。 (+23 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (42): ElementPosition, _get_process_name(), _is_excluded_title(), _is_matching_title(), _is_usable_rect(), JingmaiLocator, _print_window_capture(), 京麦商品发布自动化 - 双引擎元素定位器 UIA 元素查找 + 坐标 fallback (+34 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (31): LLMProvider, LLMProvider, _provider_supports_embeddings(), 京麦商品发布自动化 - LLM 管理器 统一管理和调度不同的 LLM 提供者  三级回退链: Ollama → vLLM → 抛异常（由上层降级处理） - ro, embedding 默认只尝试健康 provider；若都不健康，再按原顺序兜底一次。, 基于模型名做轻量能力判断，避免对明显不支持 embedding 的生成模型发请求。, 同步调用 LLM（多模态：文本 + 图片）, 文本向量化。          embeddings 只服务于记忆检索，不应因 provider 不支持而污染主流程日志。         失败时返回空向量结果 (+23 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (38): BaseAgent, batch(), _build_plan_package(), _build_product_model(), _build_progress_callback(), _default_plan_path(), execute(), _extract_plan_payload() (+30 more)

### Community 6 - "Community 6"
Cohesion: 0.1
Nodes (25): _build_db(), db_init(), init_db_cmd(), products(), scrape(), status(), DatabaseManager, 京麦商品发布自动化 - 数据库管理器 MySQL 优先，SQLite 兜底。 (+17 more)

### Community 7 - "Community 7"
Cohesion: 0.1
Nodes (8): actions(), _configure_stdio(), get_logger(), init_logger(), JingmaiLogger, 京麦商品发布自动化 - 日志模块 从 scripts/jingmai_logger.py 迁移，保持接口兼容, 带完整 fallback 的 LLM 调用          策略：         1. route() 找健康的 provider → 优先调用, 路由到健康的 Provider          按优先级: Ollama → vLLM         返回第一个健康的 provider。

### Community 8 - "Community 8"
Cohesion: 0.16
Nodes (10): auto_discover(), execute(), get(), list_categories(), Action registry and execution hooks., summary(), create_smart_executor(), SmartExecutor - 带截图验证的Executor 每个action执行前/后截图，用LLM视觉分析验证是否真正生效 失败重试3次，成功才执行下一步 (+2 more)

### Community 9 - "Community 9"
Cohesion: 0.17
Nodes (8): Enum, 京麦商品发布自动化 - Memory Package, CheckResult, CircuitBreakerState, JingmaiMonitor, MonitorState, 京麦商品发布自动化 - 重试 + 熔断器 从 scripts/jingmai_monitor.py 迁移，新增 CircuitBreaker, RetryStrategy

### Community 10 - "Community 10"
Cohesion: 0.25
Nodes (10): find_descendants(), _get_cache_request(), _get_control_filter_condition(), _get_uia_control_id_map(), _get_uia_control_name_map(), _get_uia_defs(), Fast UIA control inspection adapted from UFO's cached UIA backend., rectangle() (+2 more)

### Community 11 - "Community 11"
Cohesion: 0.23
Nodes (7): get_settings(), _load_dotenv(), 京麦商品发布自动化 - 统一配置 优先级: kwargs > 环境变量 > .env 文件 > 类默认值, 手动加载 .env 文件到 os.environ（不依赖 python-dotenv）      格式:       - KEY=VALUE, 从 .env 文件 + 环境变量 + kwargs 加载配置          优先级: kwargs > 环境变量 > .env 文件 > 类默认值, Settings, test_settings()

### Community 12 - "Community 12"
Cohesion: 0.39
Nodes (8): Exception, ActionFailedError, DatabaseError, ElementNotFoundError, JingmaiError, LLMError, MemoryError, WindowNotFoundError

### Community 13 - "Community 13"
Cohesion: 0.5
Nodes (3): Path validation utilities adapted from UFO for safe local save paths., validate_path_not_sensitive(), validate_save_path()

### Community 14 - "Community 14"
Cohesion: 0.5
Nodes (2): CropSpec, Generate lightweight vision fallback templates from v1 screenshots.  Only stable

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): 修复 _select_search_result 函数

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): 修复 _select_search_result 函数 - 使用正确的点击坐标

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): 京麦商品发布自动化 - 坐标配置别名 对齐设计文档 config/coords.py 命名规范，实际坐标定义在 jingmai_coords.py

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): 标题过滤，避免误命中 IDE、终端和无关小窗。

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): 过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte

## Knowledge Gaps
- **39 isolated node(s):** `修复 _select_search_result 函数`, `修复 _select_search_result 函数 - 使用正确的点击坐标`, `京麦商品发布自动化 - SQLAlchemy ORM 模型`, `京麦商品发布自动化 - JD 商品信息采集 从京东商品页采集标题、价格、类目等信息`, `采集商品信息         url: 京东商品页 URL` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 14`** (4 nodes): `generate_vision_templates.py`, `CropSpec`, `main()`, `Generate lightweight vision fallback templates from v1 screenshots.  Only stable`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (2 nodes): `fix_navigation.py`, `修复 _select_search_result 函数`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (2 nodes): `fix_navigation2.py`, `修复 _select_search_result 函数 - 使用正确的点击坐标`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (2 nodes): `京麦商品发布自动化 - 坐标配置别名 对齐设计文档 config/coords.py 命名规范，实际坐标定义在 jingmai_coords.py`, `coords.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `标题过滤，避免误命中 IDE、终端和无关小窗。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `过滤最小化/离屏/尺寸异常窗口，避免命中 Session 幽灵窗口。          参考 UFOAgent 的 _update_window_conte`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `JingmaiLocator` connect `Community 3` to `Community 8`, `Community 1`, `Community 2`, `Community 9`?**
  _High betweenness centrality (0.179) - this node is a cross-community bridge._
- **Why does `京麦商品发布自动化 - Memory Package` connect `Community 9` to `Community 0`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.171) - this node is a cross-community bridge._
- **Why does `MemoryManager` connect `Community 0` to `Community 9`, `Community 2`, `Community 5`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Are the 43 inferred relationships involving `JingmaiLocator` (e.g. with `SmartExecutor` and `SmartExecutor - 带截图验证的Executor 每个action执行前/后截图，用LLM视觉分析验证是否真正生效 失败重试3次，成功才执行下一步`) actually correct?**
  _`JingmaiLocator` has 43 INFERRED edges - model-reasoned connections that need verification._
- **Are the 37 inferred relationships involving `MemoryManager` (e.g. with `兼容普通 UTF-8 和 UTF-8 BOM。` and `兼容完整计划包与旧版 steps-only 计划文件。`) actually correct?**
  _`MemoryManager` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 35 inferred relationships involving `DatabaseManager` (e.g. with `兼容普通 UTF-8 和 UTF-8 BOM。` and `兼容完整计划包与旧版 steps-only 计划文件。`) actually correct?**
  _`DatabaseManager` has 35 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `BaseAgent` (e.g. with `MemoryManager` and `MemoryType`) actually correct?**
  _`BaseAgent` has 29 INFERRED edges - model-reasoned connections that need verification._