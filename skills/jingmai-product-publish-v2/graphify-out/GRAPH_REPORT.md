# Graph Report - jingmai-product-publish-v2  (2026-05-16)

## Corpus Check
- 57 files · ~2,860,900 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1237 nodes · 2673 edges · 40 communities detected
- Extraction: 47% EXTRACTED · 53% INFERRED · 0% AMBIGUOUS · INFERRED: 1424 edges (avg confidence: 0.63)
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
- [[_COMMUNITY_Community 15|Community 15]]
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

## God Nodes (most connected - your core abstractions)
1. `WindowInfo` - 347 edges
2. `RuntimeLogRepository` - 122 edges
3. `WindowManager` - 121 edges
4. `JingmaiWorkflowService` - 108 edges
5. `RealWindowsUIAAdapter` - 83 edges
6. `WorkflowStepResult` - 63 edges
7. `ImportPipelineService` - 49 edges
8. `DummyT6T8Adapter` - 42 edges
9. `TaskRunner` - 34 edges
10. `DesktopAutomationAdapter` - 33 edges

## Surprising Connections (you probably didn't know these)
- `handle_run_desktop_check()` --calls--> `test_handle_run_desktop_check()`  [INFERRED]
  jingmai_publish\cli.py → tests\test_cli.py
- `WindowInfo` --uses--> `真实 Windows UIA 适配器第一版。`  [INFERRED]
  jingmai_publish\desktop\adapter.py → jingmai_publish\desktop\uia_adapter.py
- `基于 pywinauto 的真实 Windows UIA 适配器。      当前目标：     - 列举桌面顶层窗口     - 激活京麦窗口` --uses--> `WindowInfo`  [INFERRED]
  jingmai_publish\desktop\uia_adapter.py → jingmai_publish\desktop\adapter.py
- `按顺序返回可用桌面后端。          原因：         - 某些窗口在 `uia` 下标题不完整         - 某些窗口在 `win3` --uses--> `WindowInfo`  [INFERRED]
  jingmai_publish\desktop\uia_adapter.py → jingmai_publish\desktop\adapter.py
- `延迟导入 pywinauto，避免测试环境硬依赖。` --uses--> `WindowInfo`  [INFERRED]
  jingmai_publish\desktop\uia_adapter.py → jingmai_publish\desktop\adapter.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.01
Nodes (290): WindowInfo, 向当前焦点控件发送键盘输入。          该方法用于 SKU 虚拟化单元格实验。它只负责键盘注入和结果观测，         不负责目标单元格定位。, 枚举窗口内指定 automation_id 的所有候选控件。, 采集锚点附近以普通文本渲染的候选项。          某些京麦下拉不会暴露标准 ListItem，而是直接把可选值渲染在页面文档层。         这, 向当前焦点控件发送键盘输入。          该方法用于 SKU 虚拟化单元格实验。它只负责键盘注入和结果观测，         不负责目标单元格定位。, 通过剪贴板粘贴文本，避免小数点在键盘注入时丢失。, 构建 SKU 区域探针结果。          目的：         - 观察动态 automation_id 是否会短暂出现         - 区, 向当前激活的系统文件对话框写入本地文件路径。          优先接管当前激活窗口，只处理典型的资源管理器/文件选择窗口：         - `Cabine (+282 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (69): 执行重量列格式探针，确认京麦真实接受的重量输入格式。, 执行重量列格式探针，确认京麦真实接受的重量输入格式。, 执行重量列格式探针，确认京麦真实接受的重量输入格式。, 执行重量列格式探针，确认京麦真实接受的重量输入格式。, 执行重量列格式探针，确认京麦真实接受的重量输入格式。, _brand_value_selected(), _classify_draft_save_document(), _count_t6_empty_slots() (+61 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (72): test_click_local_upload_entry_supports_oxygen_vision_panel(), test_expand_target_texts_merges_aliases_without_duplicates(), test_hover_text_by_index_moves_to_indexed_text(), test_import_pywinauto_error_message(), test_is_image_upload_slot_candidate_excludes_header_icon(), test_is_image_upload_slot_candidate_matches_real_empty_slot_controls(), test_is_picker_image_candidate_accepts_thumbnail_without_text(), test_list_windows_skips_backend_enumeration_errors() (+64 more)

### Community 3 - "Community 3"
Cohesion: 0.04
Nodes (63): calculate_market_price(), calculate_purchase_price(), ExcelIngestService, _normalize_decimal(), ParsedExcelRow, 按业务规则计算采购价。          规则：采购价 = 京东价 * 0.95, 按业务规则计算市场价。          规则：市场价 = 京东价 / 0.85, 将 Excel 单元格值归一化为 Decimal。 (+55 more)

### Community 4 - "Community 4"
Cohesion: 0.03
Nodes (92): FeishuChannelProvider, JsonlMemoryProvider, LocalPathChannelProvider, _normalize(), Default runtime providers used by the host runtime., Normalize a Feishu/Lark event payload into the host contract., Persist runtime events into runtime logs., Store short-term episodic memory in a local JSONL file. (+84 more)

### Community 5 - "Community 5"
Cohesion: 0.04
Nodes (48): _extract_text_block(), FeishuPathChannelService, FeishuPathMessage, LocalPathChannelService, parse_feishu_payload(), Channel/local-path task ingress service., Normalize local-path messages and execute the import pipeline., Normalized Feishu local-path message. (+40 more)

### Community 6 - "Community 6"
Cohesion: 0.04
Nodes (48): _DesktopActionProvider, _DesktopObservationProvider, _NullPersistenceProvider, 负责触发真实京麦窗口验证，并由 TaskRunner 驱动执行计划。, 负责触发真实京麦窗口的 T1/T2 实机验证。, Observation provider for desktop runtime alignment., Observation provider for desktop runtime alignment., Action provider wrapper for host runtime alignment. (+40 more)

### Community 7 - "Community 7"
Cohesion: 0.11
Nodes (49): handle_run_desktop_check(), DesktopVerificationService, 负责触发真实京麦窗口验证，并由 TaskRunner 驱动执行计划。, WorkflowStepResult, Minimum session state for a runtime execution., Minimum session state for a runtime execution., 按 observe -> decide -> act -> verify -> repeat 驱动最小闭环。, 按 observe -> decide -> act -> verify -> repeat 驱动最小闭环。 (+41 more)

### Community 8 - "Community 8"
Cohesion: 0.05
Nodes (14): DesktopAutomationAdapter, 按 automation_id 激活表格单元格或输入控件。, 向当前激活的系统文件对话框写入本地文件路径。, 向当前激活的系统文件对话框写入本地文件路径。, 桌面自动化适配器协议。      这里先抽象出窗口发现、激活、点击与截图能力，     后续可替换为 pywinauto / UIA / Win32 真实实现。, 点击已存在图片的 SKU 图片槽位，用于替换已有图片。, 点击已存在图片的 SKU 图片槽位，用于替换已有图片。, 按 automation_id 选择下拉值。 (+6 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (34): build_parser(), handle_cleanup_runtime_logs(), handle_init_db(), handle_run_draft_e2e(), handle_run_feishu_path_task(), handle_run_import(), handle_run_local_path_task(), main() (+26 more)

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (17): Base, Base, init_database(), _migrate_legacy_publish_tasks(), 兼容旧版 publish_tasks 表结构。      SQLAlchemy `create_all()` 只会创建不存在的表，不会为已有表补列。     当, DeclarativeBase, JDProductSnapshotRepository, default_expire_at() (+9 more)

### Community 11 - "Community 11"
Cohesion: 0.16
Nodes (24): _assert_existing_file(), DraftE2EOptions, DraftE2EOrchestrator, _extract_step_success(), _optional_decimal_text(), Excel 到京麦草稿箱的端到端编排服务。, 把导入、数据准备和桌面草稿保存串成一个可复现入口。, 执行草稿 E2E。          该入口故意不支持正式发布，只把页面推进到保存草稿成功。 (+16 more)

### Community 12 - "Community 12"
Cohesion: 0.12
Nodes (14): calculate_file_sha256(), ImageProcessResult, infer_extension_from_url(), inspect_image(), ProductImageService, 确保图片格式满足业务要求，必要时做格式转换。, 处理单张图片，完成下载/查重/转换/落库。, ProductImageRepository (+6 more)

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): 构造 SQLAlchemy 使用的 MySQL 连接串。

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): 从京东抓取 payload 构建可写入京麦详情编辑器的图文内容。

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): 悬浮 SKU 图片上传槽位，触发本地上传悬浮入口。

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): 按 automation_id 向输入框写值。

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): 按 automation_id 向输入框写值。

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): 向当前激活的系统文件对话框写入本地文件路径。

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): 构造 SQLAlchemy 使用的 MySQL 连接串。

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): 加载项目配置。      参数:         root_dir: 项目根目录。为空时默认使用当前文件的上级目录。

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): 按 automation_id 激活表格单元格或输入控件。

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): Lightweight provider registry for the host runtime.

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (1): Return a structured view of the registered providers.

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): 按 automation_id 向输入框写值。

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): 按 automation_id 激活表格单元格或输入控件。

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): 按 automation_id 选择下拉值。

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): 按 automation_id 激活表格单元格或输入控件。

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): 向当前激活的系统文件对话框写入本地文件路径。

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): 向当前激活的系统文件对话框写入本地文件路径。

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): 按 automation_id 向输入框写值。

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): 基于已有 Excel 种子数据构建首版京东商品快照。

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): 按 automation_id 选择下拉值。

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): 按 automation_id 激活表格单元格或输入控件。

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

## Knowledge Gaps
- **366 isolated node(s):** `Command line entrypoints.`, `配置加载模块。  当前项目以 `.env` 作为统一配置事实源。这里先提供最小可用配置， 支撑数据库、日志与任务运行时的基础初始化。`, `从本地 `.env` 文件加载环境变量。      只在对应环境变量尚未存在时写入，避免覆盖外部注入配置。`, `构造 SQLAlchemy 使用的 MySQL 连接串。`, `加载项目配置。      参数:         root_dir: 项目根目录。为空时默认使用当前文件的上级目录。` (+361 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 15`** (1 nodes): `构造 SQLAlchemy 使用的 MySQL 连接串。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `从京东抓取 payload 构建可写入京麦详情编辑器的图文内容。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `悬浮 SKU 图片上传槽位，触发本地上传悬浮入口。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `按 automation_id 向输入框写值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `按 automation_id 向输入框写值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `向当前激活的系统文件对话框写入本地文件路径。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `构造 SQLAlchemy 使用的 MySQL 连接串。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `加载项目配置。      参数:         root_dir: 项目根目录。为空时默认使用当前文件的上级目录。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `按 automation_id 激活表格单元格或输入控件。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `Lightweight provider registry for the host runtime.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `Return a structured view of the registered providers.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `按 automation_id 向输入框写值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `按 automation_id 激活表格单元格或输入控件。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `按 automation_id 选择下拉值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `按 automation_id 激活表格单元格或输入控件。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `向当前激活的系统文件对话框写入本地文件路径。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `向当前激活的系统文件对话框写入本地文件路径。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `按 automation_id 向输入框写值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `基于已有 Excel 种子数据构建首版京东商品快照。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `按 automation_id 选择下拉值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `按 automation_id 激活表格单元格或输入控件。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `WindowInfo` connect `Community 0` to `Community 8`, `Community 1`, `Community 2`, `Community 4`?**
  _High betweenness centrality (0.463) - this node is a cross-community bridge._
- **Why does `RuntimeLogRepository` connect `Community 4` to `Community 1`, `Community 3`, `Community 5`, `Community 6`, `Community 7`, `Community 10`, `Community 12`?**
  _High betweenness centrality (0.202) - this node is a cross-community bridge._
- **Why does `WindowManager` connect `Community 4` to `Community 0`, `Community 1`, `Community 6`, `Community 7`, `Community 8`?**
  _High betweenness centrality (0.196) - this node is a cross-community bridge._
- **Are the 346 inferred relationships involving `WindowInfo` (e.g. with `UIATuningConfig` and `RealWindowsUIAAdapter`) actually correct?**
  _`WindowInfo` has 346 INFERRED edges - model-reasoned connections that need verification._
- **Are the 118 inferred relationships involving `RuntimeLogRepository` (e.g. with `RuntimeLog` and `RuntimeLogPersistenceProvider`) actually correct?**
  _`RuntimeLogRepository` has 118 INFERRED edges - model-reasoned connections that need verification._
- **Are the 117 inferred relationships involving `WindowManager` (e.g. with `DesktopAutomationAdapter` and `WindowInfo`) actually correct?**
  _`WindowManager` has 117 INFERRED edges - model-reasoned connections that need verification._
- **Are the 67 inferred relationships involving `JingmaiWorkflowService` (e.g. with `DesktopVerificationService` and `_DesktopObservationProvider`) actually correct?**
  _`JingmaiWorkflowService` has 67 INFERRED edges - model-reasoned connections that need verification._