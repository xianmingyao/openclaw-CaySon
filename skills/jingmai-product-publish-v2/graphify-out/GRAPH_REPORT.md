# Graph Report - jingmai-product-publish-v2  (2026-05-14)

## Corpus Check
- 36 files · ~127,554 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 290 nodes · 589 edges · 9 communities detected
- Extraction: 57% EXTRACTED · 43% INFERRED · 0% AMBIGUOUS · INFERRED: 256 edges (avg confidence: 0.66)
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
- [[_COMMUNITY_Community 9|Community 9]]

## God Nodes (most connected - your core abstractions)
1. `WindowInfo` - 35 edges
2. `RealWindowsUIAAdapter` - 32 edges
3. `UploadJobRepository` - 27 edges
4. `RuntimeLogRepository` - 21 edges
5. `JingmaiWorkflowService` - 18 edges
6. `DummyAdapter` - 17 edges
7. `WindowManager` - 16 edges
8. `ProductImageService` - 16 edges
9. `ImportPipelineService` - 16 edges
10. `DesktopAutomationAdapter` - 15 edges

## Surprising Connections (you probably didn't know these)
- `执行真实京麦窗口的 T1~T5 实机验证。` --uses--> `ImportPipelineService`  [INFERRED]
  jingmai_publish\cli.py → jingmai_publish\services\import_pipeline.py
- `init_database()` --calls--> `handle_init_db()`  [INFERRED]
  jingmai_publish\bootstrap.py → jingmai_publish\cli.py
- `handle_init_db()` --calls--> `test_handle_init_db()`  [INFERRED]
  jingmai_publish\cli.py → tests\test_cli.py
- `handle_run_import()` --calls--> `create_session_factory()`  [INFERRED]
  jingmai_publish\cli.py → jingmai_publish\db\session.py
- `handle_run_import()` --calls--> `ImportPipelineService`  [INFERRED]
  jingmai_publish\cli.py → jingmai_publish\services\import_pipeline.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (36): WindowInfo, test_expand_target_texts_merges_aliases_without_duplicates(), test_import_pywinauto_error_message(), test_normalize_handle_supports_string_and_int(), test_score_candidate_prefers_exact_button_match(), test_score_candidate_supports_alias_match(), _normalize_handle(), 真实 Windows UIA 适配器第一版。 (+28 more)

### Community 1 - "Community 1"
Cohesion: 0.07
Nodes (31): 执行真实京麦窗口的 T1/T2 实机验证。, 执行真实京麦窗口的 T1/T2 实机验证。, 执行真实京麦窗口的 T1/T2 实机验证。, calculate_market_price(), calculate_purchase_price(), ExcelIngestService, _normalize_decimal(), ParsedExcelRow (+23 more)

### Community 2 - "Community 2"
Cohesion: 0.1
Nodes (19): DesktopVerificationService, 负责触发真实京麦窗口的 T1/T2 实机验证。, JingmaiWorkflowService, WorkflowStepResult, test_desktop_verification_service_returns_debug_on_t1_failure(), test_desktop_verification_service_run_both(), test_desktop_verification_service_t4_requires_fields(), test_desktop_verification_service_t5_input_probe() (+11 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (25): init_database(), build_parser(), handle_init_db(), handle_run_desktop_check(), handle_run_import(), main(), _parse_click_aliases(), 执行真实京麦窗口的 T1~T5 实机验证。 (+17 more)

### Community 4 - "Community 4"
Cohesion: 0.1
Nodes (13): Base, Base, DeclarativeBase, default_expire_at(), JDProductSnapshot, ProductImage, PublishTask, PublishTaskStep (+5 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (14): calculate_file_sha256(), ImageProcessResult, infer_extension_from_url(), inspect_image(), ProductImageService, 确保图片格式满足业务要求，必要时做格式转换。, 处理单张图片，完成下载/查重/转换/落库。, ProductImageRepository (+6 more)

### Community 6 - "Community 6"
Cohesion: 0.11
Nodes (6): DesktopAutomationAdapter, 桌面自动化适配器协议。      这里先抽象出窗口发现、激活、点击与截图能力，     后续可替换为 pywinauto / UIA / Win32 真实实现。, 按 automation_id 向输入框写值。, 按 automation_id 选择下拉值。, 按 automation_id 激活表格单元格或输入控件。, Protocol

### Community 7 - "Community 7"
Cohesion: 0.4
Nodes (3): PreparedImageData, PreparedProductData, 合并 Excel 与京东快照，生成可上架标准数据。

### Community 9 - "Community 9"
Cohesion: 1.0
Nodes (1): 构造 SQLAlchemy 使用的 MySQL 连接串。

## Knowledge Gaps
- **30 isolated node(s):** `配置加载模块。  当前项目以 `.env` 作为统一配置事实源。这里先提供最小可用配置， 支撑数据库、日志与任务运行时的基础初始化。`, `从本地 `.env` 文件加载环境变量。      只在对应环境变量尚未存在时写入，避免覆盖外部注入配置。`, `构造 SQLAlchemy 使用的 MySQL 连接串。`, `加载项目配置。      参数:         root_dir: 项目根目录。为空时默认使用当前文件的上级目录。`, `桌面自动化适配器协议。      这里先抽象出窗口发现、激活、点击与截图能力，     后续可替换为 pywinauto / UIA / Win32 真实实现。` (+25 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 9`** (1 nodes): `构造 SQLAlchemy 使用的 MySQL 连接串。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RuntimeLogRepository` connect `Community 1` to `Community 2`, `Community 4`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.280) - this node is a cross-community bridge._
- **Why does `JingmaiWorkflowService` connect `Community 2` to `Community 1`?**
  _High betweenness centrality (0.238) - this node is a cross-community bridge._
- **Why does `WindowInfo` connect `Community 0` to `Community 2`, `Community 6`?**
  _High betweenness centrality (0.209) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `WindowInfo` (e.g. with `UIATuningConfig` and `RealWindowsUIAAdapter`) actually correct?**
  _`WindowInfo` has 34 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `RealWindowsUIAAdapter` (e.g. with `WindowInfo` and `.__init__()`) actually correct?**
  _`RealWindowsUIAAdapter` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `UploadJobRepository` (e.g. with `UploadJob` and `UploadJobItem`) actually correct?**
  _`UploadJobRepository` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `RuntimeLogRepository` (e.g. with `RuntimeLog` and `ImageProcessResult`) actually correct?**
  _`RuntimeLogRepository` has 17 INFERRED edges - model-reasoned connections that need verification._