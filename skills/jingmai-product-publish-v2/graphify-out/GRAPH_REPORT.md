# Graph Report - jingmai-product-publish-v2  (2026-05-15)

## Corpus Check
- 55 files · ~972,622 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 861 nodes · 1908 edges · 34 communities detected
- Extraction: 51% EXTRACTED · 49% INFERRED · 0% AMBIGUOUS · INFERRED: 942 edges (avg confidence: 0.64)
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
- [[_COMMUNITY_Community 14|Community 14]]
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

## God Nodes (most connected - your core abstractions)
1. `WindowInfo` - 155 edges
2. `RuntimeLogRepository` - 83 edges
3. `JingmaiWorkflowService` - 74 edges
4. `RealWindowsUIAAdapter` - 70 edges
5. `WindowManager` - 64 edges
6. `WorkflowStepResult` - 54 edges
7. `ImportPipelineService` - 43 edges
8. `DummyT6T8Adapter` - 40 edges
9. `DesktopAutomationAdapter` - 30 edges
10. `TaskRunner` - 30 edges

## Surprising Connections (you probably didn't know these)
- `WindowInfo` --uses--> `真实 Windows UIA 适配器第一版。`  [INFERRED]
  jingmai_publish\desktop\adapter.py → jingmai_publish\desktop\uia_adapter.py
- `WindowInfo` --uses--> `基于 pywinauto 的真实 Windows UIA 适配器。      当前目标：     - 列举桌面顶层窗口     - 激活京麦窗口     - 在`  [INFERRED]
  jingmai_publish\desktop\adapter.py → jingmai_publish\desktop\uia_adapter.py
- `WindowInfo` --uses--> `按顺序返回可用桌面后端。          原因：         - 某些窗口在 `uia` 下标题不完整         - 某些窗口在 `win32` 下`  [INFERRED]
  jingmai_publish\desktop\adapter.py → jingmai_publish\desktop\uia_adapter.py
- `WindowInfo` --uses--> `延迟导入 pywinauto，避免测试环境硬依赖。`  [INFERRED]
  jingmai_publish\desktop\adapter.py → jingmai_publish\desktop\uia_adapter.py
- `WindowInfo` --uses--> `按句柄获取 pywinauto 窗口对象。`  [INFERRED]
  jingmai_publish\desktop\adapter.py → jingmai_publish\desktop\uia_adapter.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (52): 负责触发真实京麦窗口验证，并由 TaskRunner 驱动执行计划。, 负责触发真实京麦窗口的 T1/T2 实机验证。, 执行重量列格式探针，确认京麦真实接受的重量输入格式。, 执行重量列格式探针，确认京麦真实接受的重量输入格式。, 执行重量列格式探针，确认京麦真实接受的重量输入格式。, 执行重量列格式探针，确认京麦真实接受的重量输入格式。, 执行重量列格式探针，确认京麦真实接受的重量输入格式。, Observation provider for desktop runtime alignment. (+44 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (55): test_expand_target_texts_merges_aliases_without_duplicates(), test_import_pywinauto_error_message(), test_is_image_upload_slot_candidate_excludes_header_icon(), test_is_image_upload_slot_candidate_matches_real_empty_slot_controls(), test_merge_image_upload_slot_snapshot_prefers_empty_over_filled_for_same_slot(), test_normalize_handle_supports_string_and_int(), test_normalize_image_upload_slot_snapshot_ignores_small_plus_icon(), test_normalize_image_upload_slot_snapshot_marks_empty_list_item_as_empty_slot() (+47 more)

### Community 2 - "Community 2"
Cohesion: 0.02
Nodes (106): WindowInfo, 向当前焦点控件发送键盘输入。          该方法用于 SKU 虚拟化单元格实验。它只负责键盘注入和结果观测，         不负责目标单元格定位。, 枚举窗口内指定 automation_id 的所有候选控件。, 向当前焦点控件发送键盘输入。          该方法用于 SKU 虚拟化单元格实验。它只负责键盘注入和结果观测，         不负责目标单元格定位。, 通过剪贴板粘贴文本，避免小数点在键盘注入时丢失。, 构建 SKU 区域探针结果。          目的：         - 观察动态 automation_id 是否会短暂出现         - 区, 向当前激活的系统文件对话框写入本地文件路径。          优先接管当前激活窗口，只处理典型的资源管理器/文件选择窗口：         - `Cabine, 通过剪贴板粘贴文本，避免小数点在键盘注入时丢失。 (+98 more)

### Community 3 - "Community 3"
Cohesion: 0.04
Nodes (42): Base, Base, read_excel_path_from_message(), DeclarativeBase, 按业务规则计算采购价。          规则：采购价 = 京东价 * 0.95, 按业务规则计算市场价。          规则：市场价 = 京东价 / 0.85, 将 Excel 单元格值归一化为 Decimal。, 按业务规则计算采购价。          规则：采购价 = 京东价 * 0.95 (+34 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (39): 协调“本地 Excel -> 入库 -> 抓取 -> 标准化准备 -> 创建上架任务”的主链路。, _extract_attributes(), _extract_detail_html(), _extract_detail_text(), _extract_images(), extract_jd_item_id(), _extract_price(), _fetch_via_requests() (+31 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (54): _extract_text_block(), FeishuPathChannelService, FeishuPathMessage, LocalPathChannelService, parse_feishu_payload(), Channel/local-path task ingress service., Normalize local-path messages and execute the import pipeline., Normalized Feishu local-path message. (+46 more)

### Community 6 - "Community 6"
Cohesion: 0.05
Nodes (35): FeishuChannelProvider, JsonlMemoryProvider, LocalPathChannelProvider, _normalize(), Default runtime providers used by the host runtime., Normalize a Feishu/Lark event payload into the host contract., Persist runtime events into runtime logs., Store short-term episodic memory in a local JSONL file. (+27 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (47): DesktopVerificationService, 负责触发真实京麦窗口验证，并由 TaskRunner 驱动执行计划。, Structured workflow step result., WorkflowStepResult, _apply_workflow_result(), _build_failure_signature(), _extract_after_state(), _is_verified() (+39 more)

### Community 8 - "Community 8"
Cohesion: 0.09
Nodes (17): Run the full import flow from a local message file., calculate_market_price(), calculate_purchase_price(), ExcelIngestService, _normalize_decimal(), ParsedExcelRow, 执行 Excel 导入入库并创建上架任务。, calculate_file_sha256() (+9 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (34): init_database(), build_parser(), handle_cleanup_runtime_logs(), handle_init_db(), handle_run_desktop_check(), handle_run_feishu_path_task(), handle_run_import(), handle_run_local_path_task() (+26 more)

### Community 10 - "Community 10"
Cohesion: 0.05
Nodes (10): DesktopAutomationAdapter, 向当前激活的系统文件对话框写入本地文件路径。, 读取指定 automation_id 当前对应控件的文本与边界信息。, 向当前激活的系统文件对话框写入本地文件路径。, 桌面自动化适配器协议。      这里先抽象出窗口发现、激活、点击与截图能力，     后续可替换为 pywinauto / UIA / Win32 真实实现。, 悬浮 SKU 图片上传槽位，触发本地上传悬浮入口。, 点击已存在图片的 SKU 图片槽位，用于替换已有图片。, 按 automation_id 向输入框写值。 (+2 more)

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (14): calculate_file_sha256(), ImageProcessResult, infer_extension_from_url(), inspect_image(), ProductImageService, 确保图片格式满足业务要求，必要时做格式转换。, 处理单张图片，完成下载/查重/转换/落库。, ProductImageRepository (+6 more)

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (1): 构造 SQLAlchemy 使用的 MySQL 连接串。

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): 构造 SQLAlchemy 使用的 MySQL 连接串。

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): 加载项目配置。      参数:         root_dir: 项目根目录。为空时默认使用当前文件的上级目录。

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): 按 automation_id 选择下拉值。

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): 按 automation_id 激活表格单元格或输入控件。

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): Lightweight provider registry for the host runtime.

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (1): Return a structured view of the registered providers.

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (1): 按 automation_id 向输入框写值。

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (1): 按 automation_id 激活表格单元格或输入控件。

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): 按 automation_id 选择下拉值。

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): 按 automation_id 激活表格单元格或输入控件。

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): 向当前激活的系统文件对话框写入本地文件路径。

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (1): 向当前激活的系统文件对话框写入本地文件路径。

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): 按 automation_id 向输入框写值。

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): 基于已有 Excel 种子数据构建首版京东商品快照。

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): 按 automation_id 选择下拉值。

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): 按 automation_id 激活表格单元格或输入控件。

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): 读取指定 automation_id 当前对应控件的文本与边界信息。

## Knowledge Gaps
- **175 isolated node(s):** `Command line entrypoints.`, `配置加载模块。  当前项目以 `.env` 作为统一配置事实源。这里先提供最小可用配置， 支撑数据库、日志与任务运行时的基础初始化。`, `从本地 `.env` 文件加载环境变量。      只在对应环境变量尚未存在时写入，避免覆盖外部注入配置。`, `构造 SQLAlchemy 使用的 MySQL 连接串。`, `加载项目配置。      参数:         root_dir: 项目根目录。为空时默认使用当前文件的上级目录。` (+170 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 14`** (1 nodes): `构造 SQLAlchemy 使用的 MySQL 连接串。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (1 nodes): `构造 SQLAlchemy 使用的 MySQL 连接串。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `加载项目配置。      参数:         root_dir: 项目根目录。为空时默认使用当前文件的上级目录。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `按 automation_id 选择下拉值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `按 automation_id 激活表格单元格或输入控件。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `Lightweight provider registry for the host runtime.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (1 nodes): `Return a structured view of the registered providers.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `按 automation_id 向输入框写值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `按 automation_id 激活表格单元格或输入控件。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `按 automation_id 选择下拉值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `按 automation_id 激活表格单元格或输入控件。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `向当前激活的系统文件对话框写入本地文件路径。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `向当前激活的系统文件对话框写入本地文件路径。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `按 automation_id 向输入框写值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `基于已有 Excel 种子数据构建首版京东商品快照。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `按 automation_id 选择下拉值。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `按 automation_id 激活表格单元格或输入控件。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `读取指定 automation_id 当前对应控件的文本与边界信息。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `WindowInfo` connect `Community 2` to `Community 0`, `Community 1`, `Community 10`?**
  _High betweenness centrality (0.300) - this node is a cross-community bridge._
- **Why does `RuntimeLogRepository` connect `Community 5` to `Community 0`, `Community 3`, `Community 4`, `Community 6`, `Community 7`, `Community 8`, `Community 11`?**
  _High betweenness centrality (0.244) - this node is a cross-community bridge._
- **Why does `JingmaiWorkflowService` connect `Community 0` to `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`?**
  _High betweenness centrality (0.199) - this node is a cross-community bridge._
- **Are the 154 inferred relationships involving `WindowInfo` (e.g. with `UIATuningConfig` and `RealWindowsUIAAdapter`) actually correct?**
  _`WindowInfo` has 154 INFERRED edges - model-reasoned connections that need verification._
- **Are the 79 inferred relationships involving `RuntimeLogRepository` (e.g. with `RuntimeLog` and `RuntimeLogPersistenceProvider`) actually correct?**
  _`RuntimeLogRepository` has 79 INFERRED edges - model-reasoned connections that need verification._
- **Are the 49 inferred relationships involving `JingmaiWorkflowService` (e.g. with `DesktopVerificationService` and `_DesktopObservationProvider`) actually correct?**
  _`JingmaiWorkflowService` has 49 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `RealWindowsUIAAdapter` (e.g. with `WindowInfo` and `当前没有激活文件对话框时，应返回结构化失败结果。`) actually correct?**
  _`RealWindowsUIAAdapter` has 11 INFERRED edges - model-reasoned connections that need verification._