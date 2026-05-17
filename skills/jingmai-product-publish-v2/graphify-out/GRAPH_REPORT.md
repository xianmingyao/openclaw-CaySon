# Graph Report - jingmai-product-publish-v2  (2026-05-17)

## Corpus Check
- 88 files · ~743,734 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2093 nodes · 5751 edges · 49 communities detected
- Extraction: 38% EXTRACTED · 62% INFERRED · 0% AMBIGUOUS · INFERRED: 3568 edges (avg confidence: 0.62)
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
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
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

## God Nodes (most connected - your core abstractions)
1. `WindowInfo` - 371 edges
2. `WorkflowStepResult` - 173 edges
3. `RuntimeLogRepository` - 159 edges
4. `WindowManager` - 158 edges
5. `RuntimeEventLoop` - 136 edges
6. `JingmaiWorkflowService` - 118 edges
7. `ActionStep` - 103 edges
8. `AgentExecutor` - 97 edges
9. `RealWindowsUIAAdapter` - 87 edges
10. `EventType` - 85 edges

## Surprising Connections (you probably didn't know these)
- `build_parser()` --calls--> `test_cli_parser_supports_new_t6_t8_steps()`  [INFERRED]
  jingmai_publish\cli.py → tests\test_t6_t8_verify.py
- `handle_run_desktop_check()` --calls--> `test_handle_run_desktop_check()`  [INFERRED]
  jingmai_publish\cli.py → tests\test_cli.py
- `WindowInfo` --uses--> `真实 Windows UIA 适配器第一版。`  [INFERRED]
  jingmai_publish\desktop\adapter.py → jingmai_publish\desktop\uia_adapter.py
- `WindowInfo` --uses--> `基于 pywinauto 的真实 Windows UIA 适配器。      当前目标：     - 列举桌面顶层窗口     - 激活京麦窗口`  [INFERRED]
  jingmai_publish\desktop\adapter.py → jingmai_publish\desktop\uia_adapter.py
- `WindowInfo` --uses--> `按顺序返回可用桌面后端。          原因：         - 某些窗口在 `uia` 下标题不完整         - 某些窗口在 `win3`  [INFERRED]
  jingmai_publish\desktop\adapter.py → jingmai_publish\desktop\uia_adapter.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.02
Nodes (218): FeishuChannelProvider, JsonlMemoryProvider, LocalPathChannelProvider, _normalize(), Default runtime providers used by the host runtime., Normalize a Feishu/Lark event payload into the host contract., Persist runtime events into runtime logs., Store short-term episodic memory in a local JSONL file. (+210 more)

### Community 1 - "Community 1"
Cohesion: 0.01
Nodes (312): WindowInfo, 向当前焦点控件发送键盘输入。          该方法用于 SKU 虚拟化单元格实验。它只负责键盘注入和结果观测，         不负责目标单元格定位。, 枚举窗口内指定 automation_id 的所有候选控件。, 对已经定位到的下拉控件执行选择。          这里优先遵守“下拉选择”语义：         1. 先尝试原生 `select`         2. 再, 采集锚点附近以普通文本渲染的候选项。          某些京麦下拉不会暴露标准 ListItem，而是直接把可选值渲染在页面文档层。         这, 向当前焦点控件发送键盘输入。          该方法用于 SKU 虚拟化单元格实验。它只负责键盘注入和结果观测，         不负责目标单元格定位。, 通过剪贴板粘贴文本，避免小数点在键盘注入时丢失。, 构建 SKU 区域探针结果。          目的：         - 观察动态 automation_id 是否会短暂出现         - 区 (+304 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (198): AgentExecutor, Executes ActionSteps via workflow_service reflection or private methods.      Pu, T6 透明图上传：支持 transparent_image_path / image_path 回退。, T6 详情编辑器写入：支持多种内容来源解析。, Execute a single ActionStep, optionally via a RetryLane.          When lane is p, Build method kwargs from params dict using required_params + param_map., WorkflowStepResult, AgentPipeline (+190 more)

### Community 3 - "Community 3"
Cohesion: 0.02
Nodes (102): _extract_text_block(), FeishuPathChannelService, FeishuPathMessage, LocalPathChannelService, parse_feishu_payload(), Channel/local-path task ingress service., Normalize local-path messages and execute the import pipeline., Normalized Feishu local-path message. (+94 more)

### Community 4 - "Community 4"
Cohesion: 0.03
Nodes (79): AnchorGroundingAdapter, GroundingCandidate, GroundingResult, 三路 Grounding 仲裁 — DOM/UIA + Vision + Anchor 候选融合。  BL-095: 当单一元素定位方法失败时，通过三路候选融合, Anchor 定位器 — 基于文本、地标关系推断元素位置。      当 UIA 和 Vision 都不可用时，通过已知文本位置 + 相对偏移推断目标位置。, 基于文本地标推断元素位置。          参数:             target: 目标元素标识（如 "save_draft", "next_step, 三路 Grounding 仲裁 — DOM/UIA + Vision + Anchor 候选融合。      使用方式:         provider =, 执行三路 grounding 仲裁。          参数:             target: 定位目标（automation_id 或元素描述） (+71 more)

### Community 5 - "Community 5"
Cohesion: 0.03
Nodes (95): LoopSessionState, Current runtime loop session state (aligned with sightflow session state)., Service 层导出。  说明： - 这里优先导出当前仓库中已经落地的服务 - 某些计划中的服务文件可能尚未恢复到工作区 - 为避免一个未实现模块阻塞整个 C, HostRuntime, Host runtime wrapper for provider-oriented execution., Wrap TaskRunner with provider-oriented metadata and event output., Enqueue a task for background processing. Returns event_id.          The task wi, Start the background event loop. (+87 more)

### Community 6 - "Community 6"
Cohesion: 0.04
Nodes (77): Enum, EventStatus, EventType, SightFlow-style runtime event loop with queue, schedule, and session state.  Ali, SightFlow-compatible runtime event loop.      Manages the observe→decide→act→ver, Submit an event for immediate processing. Returns event_id., Schedule an event for future processing. Returns event_id., Subscribe to event lifecycle notifications. (+69 more)

### Community 7 - "Community 7"
Cohesion: 0.03
Nodes (77): 构建调试输出（窗口快照、候选控件、点击诊断）。          保留用于 debug=True 模式，与原实现完全一致。, test_click_local_upload_entry_supports_oxygen_vision_panel(), test_click_picker_file_card_by_name_clicks_thumbnail_above_label(), test_expand_target_texts_merges_aliases_without_duplicates(), test_hover_text_by_index_moves_to_indexed_text(), test_import_pywinauto_error_message(), test_is_image_upload_slot_candidate_excludes_header_icon(), test_is_image_upload_slot_candidate_matches_real_empty_slot_controls() (+69 more)

### Community 8 - "Community 8"
Cohesion: 0.05
Nodes (51): _limit_detail_content(), _normalize_detail_content(), AgentExecutor: getattr-based dispatch replacing hardcoded if/elif chain.  BL-091, _read_detail_content_file(), _reject_probe_detail_content(), build_detail_editor_content(), _build_detail_html_from_images(), _extract_attributes() (+43 more)

### Community 9 - "Community 9"
Cohesion: 0.06
Nodes (33): AuditRepository, Phase D 审计 Repository —— UiArtifact / ActionEvent / ReflectionCase。  对应 BL-102 三, 审计数据写入仓库。      注入 SQLAlchemy Session，所有方法遵循 RuntimeLogRepository 模式：     创建模型实例, Base, Base, 兼容旧版 publish_tasks 表结构。      SQLAlchemy `create_all()` 只会创建不存在的表，不会为已有表补列。     当, DeclarativeBase, 确保图片格式满足业务要求，必要时做格式转换。 (+25 more)

### Community 10 - "Community 10"
Cohesion: 0.08
Nodes (64): handle_run_desktop_check(), DraftE2EOptions, 执行验证步骤管线。          签名和返回结构与原 TaskRunner 完全兼容。, _build_pipeline(), FakeSession, test_agent_pipeline.py — AgentPipeline 测试。 BL-091: 验证全管线集成、T1 失败停止、重试成功、结果结构兼容。, 异常应被包装为 WorkflowStepResult(success=False)。, 结果结构应与原 TaskRunner.run() 兼容。 (+56 more)

### Community 11 - "Community 11"
Cohesion: 0.05
Nodes (51): init_database(), _migrate_legacy_publish_tasks(), _add_common_options(), build_parser(), configure_logging(), handle_check_config(), handle_check_evidence(), handle_cleanup_runtime_logs() (+43 more)

### Community 12 - "Community 12"
Cohesion: 0.05
Nodes (12): DesktopAutomationAdapter, 按 automation_id 激活表格单元格或输入控件。, 向当前激活的系统文件对话框写入本地文件路径。, 向当前激活的系统文件对话框写入本地文件路径。, 桌面自动化适配器协议。      这里先抽象出窗口发现、激活、点击与截图能力，     后续可替换为 pywinauto / UIA / Win32 真实实现。, 点击已存在图片的 SKU 图片槽位，用于替换已有图片。, 点击已存在图片的 SKU 图片槽位，用于替换已有图片。, 按 automation_id 选择下拉值。 (+4 more)

### Community 13 - "Community 13"
Cohesion: 0.16
Nodes (14): calculate_file_sha256(), ImageProcessResult, infer_extension_from_url(), inspect_image(), ProductImageService, 确保图片格式满足业务要求，必要时做格式转换。, 处理单张图片，完成下载/查重/转换/落库。, DummyImageRecord (+6 more)

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): 构造 SQLAlchemy 使用的 MySQL 连接串。

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): 从 RuntimeEventLoop REFLECTION_RECORDED 事件构造。

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): 该记录是否代表一次失败（非 CONTINUE 决策）。

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): 将 Ollama 格式消息转为 OpenAI 兼容格式。          Ollama 的 image_url 格式和 OpenAI 略有不同。

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): 从京东抓取 payload 构建可写入京麦详情编辑器的图文内容。

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): 从本地 `.env` 文件加载环境变量。      只在对应环境变量尚未存在时写入，避免覆盖外部注入配置。

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): 构造 SQLAlchemy 使用的 MySQL 连接串。

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): 加载项目配置。      参数:         root_dir: 项目根目录。为空时默认使用当前文件的上级目录。

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): Lightweight provider registry for the host runtime.

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): Return a structured view of the registered providers.

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): 从京东抓取 payload 构建可写入京麦详情编辑器的图文内容。

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (1): 悬浮 SKU 图片上传槽位，触发本地上传悬浮入口。

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): 按 automation_id 向输入框写值。

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): 按 automation_id 向输入框写值。

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): 向当前激活的系统文件对话框写入本地文件路径。

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): 构造 SQLAlchemy 使用的 MySQL 连接串。

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): 加载项目配置。      参数:         root_dir: 项目根目录。为空时默认使用当前文件的上级目录。

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): 按 automation_id 激活表格单元格或输入控件。

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): Lightweight provider registry for the host runtime.

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): 按 automation_id 向输入框写值。

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): 按 automation_id 激活表格单元格或输入控件。

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): 按 automation_id 选择下拉值。

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): 按 automation_id 激活表格单元格或输入控件。

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): 向当前激活的系统文件对话框写入本地文件路径。

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (1): 向当前激活的系统文件对话框写入本地文件路径。

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (1): 按 automation_id 向输入框写值。

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): 基于已有 Excel 种子数据构建首版京东商品快照。

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): 按 automation_id 选择下拉值。

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): 按 automation_id 激活表格单元格或输入控件。

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

## Knowledge Gaps
- **469 isolated node(s):** `配置加载模块。  当前项目以 `.env` 作为统一配置事实源。这里先提供最小可用配置， 支撑数据库、日志与任务运行时的基础初始化。`, `从本地 `.env` 文件加载环境变量。      只在对应环境变量尚未存在时写入，避免覆盖外部注入配置。`, `构造 SQLAlchemy 使用的 MySQL 连接串。`, `加载项目配置。      参数:         root_dir: 项目根目录。为空时默认使用当前文件的上级目录。`, `校验外部 HTTP URL，阻止 SSRF 常见入口。      当前策略以域名白名单为主，并显式拒绝本地、内网、链路本地和     带凭据 URL。京东商品页` (+464 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 16`** (1 nodes): `构造 SQLAlchemy 使用的 MySQL 连接串。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `从 RuntimeEventLoop REFLECTION_RECORDED 事件构造。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `该记录是否代表一次失败（非 CONTINUE 决策）。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `将 Ollama 格式消息转为 OpenAI 兼容格式。          Ollama 的 image_url 格式和 OpenAI 略有不同。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `从京东抓取 payload 构建可写入京麦详情编辑器的图文内容。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `从本地 `.env` 文件加载环境变量。      只在对应环境变量尚未存在时写入，避免覆盖外部注入配置。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `构造 SQLAlchemy 使用的 MySQL 连接串。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `加载项目配置。      参数:         root_dir: 项目根目录。为空时默认使用当前文件的上级目录。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `Lightweight provider registry for the host runtime.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `Return a structured view of the registered providers.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `从京东抓取 payload 构建可写入京麦详情编辑器的图文内容。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `悬浮 SKU 图片上传槽位，触发本地上传悬浮入口。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `按 automation_id 向输入框写值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `按 automation_id 向输入框写值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `向当前激活的系统文件对话框写入本地文件路径。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `构造 SQLAlchemy 使用的 MySQL 连接串。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `加载项目配置。      参数:         root_dir: 项目根目录。为空时默认使用当前文件的上级目录。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `按 automation_id 激活表格单元格或输入控件。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `Lightweight provider registry for the host runtime.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `按 automation_id 向输入框写值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `按 automation_id 激活表格单元格或输入控件。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `按 automation_id 选择下拉值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `按 automation_id 激活表格单元格或输入控件。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `向当前激活的系统文件对话框写入本地文件路径。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `向当前激活的系统文件对话框写入本地文件路径。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `按 automation_id 向输入框写值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `基于已有 Excel 种子数据构建首版京东商品快照。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `按 automation_id 选择下拉值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `按 automation_id 激活表格单元格或输入控件。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `WindowInfo` connect `Community 1` to `Community 0`, `Community 12`, `Community 7`?**
  _High betweenness centrality (0.282) - this node is a cross-community bridge._
- **Why does `Service 层导出。  说明： - 这里优先导出当前仓库中已经落地的服务 - 某些计划中的服务文件可能尚未恢复到工作区 - 为避免一个未实现模块阻塞整个 C` connect `Community 5` to `Community 0`, `Community 2`, `Community 3`, `Community 4`, `Community 6`, `Community 8`, `Community 13`?**
  _High betweenness centrality (0.229) - this node is a cross-community bridge._
- **Why does `WorkflowStepResult` connect `Community 2` to `Community 0`, `Community 8`, `Community 10`, `Community 3`?**
  _High betweenness centrality (0.142) - this node is a cross-community bridge._
- **Are the 370 inferred relationships involving `WindowInfo` (e.g. with `UIATuningConfig` and `RealWindowsUIAAdapter`) actually correct?**
  _`WindowInfo` has 370 INFERRED edges - model-reasoned connections that need verification._
- **Are the 157 inferred relationships involving `WorkflowStepResult` (e.g. with `AgentPipeline` and `AgentPipeline: Planner → Executor → Reflection orchestration.  BL-091: Replaces`) actually correct?**
  _`WorkflowStepResult` has 157 INFERRED edges - model-reasoned connections that need verification._
- **Are the 155 inferred relationships involving `RuntimeLogRepository` (e.g. with `RuntimeLog` and `RuntimeLogPersistenceProvider`) actually correct?**
  _`RuntimeLogRepository` has 155 INFERRED edges - model-reasoned connections that need verification._
- **Are the 154 inferred relationships involving `WindowManager` (e.g. with `DesktopAutomationAdapter` and `WindowInfo`) actually correct?**
  _`WindowManager` has 154 INFERRED edges - model-reasoned connections that need verification._