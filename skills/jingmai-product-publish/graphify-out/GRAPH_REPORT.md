# Graph Report - jingmai-product-publish  (2026-06-10)

## Corpus Check
- 136 files · ~135,565 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1102 nodes · 3190 edges · 36 communities detected
- Extraction: 38% EXTRACTED · 62% INFERRED · 0% AMBIGUOUS · INFERRED: 1975 edges (avg confidence: 0.62)
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
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 33|Community 33]]
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

## God Nodes (most connected - your core abstractions)
1. `AgentResult` - 85 edges
2. `AgentContext` - 67 edges
3. `Command` - 61 edges
4. `GraphState` - 60 edges
5. `MySQLSettings` - 51 edges
6. `ReviewScorerSettings` - 47 edges
7. `ExcelProductImportService` - 44 edges
8. `ExcelProductParser` - 39 edges
9. `AsyncMySQLClient` - 39 edges
10. `MiniMaxReviewScoreStrategy` - 38 edges

## Surprising Connections (you probably didn't know these)
- `AgentResult` --uses--> `初始化 Win32 窗口检测 backend。`  [INFERRED]
  jm_ufo_agent\agents\base.py → jm_ufo_agent\backends\ufo_adapter.py
- `AgentResult` --uses--> `初始化 Win32 窗口检测 backend。`  [INFERRED]
  jm_ufo_agent\agents\base.py → jm_ufo_agent\backends\ufo_adapter.py
- `AgentResult` --uses--> `判断子窗口是否属于 WebView/Chromium 区域。`  [INFERRED]
  jm_ufo_agent\agents\base.py → jm_ufo_agent\backends\ufo_adapter.py
- `AgentResult` --uses--> `基于 Win32/UFO API 的桌面命令执行 backend。`  [INFERRED]
  jm_ufo_agent\agents\base.py → jm_ufo_agent\backends\ufo_adapter.py
- `AgentResult` --uses--> `用于测试和 dry-run 的静态窗口 backend。`  [INFERRED]
  jm_ufo_agent\agents\base.py → jm_ufo_agent\backends\ufo_adapter.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (83): GuardedActionStrategy, 使用外部注入 workflow 运行 dry-run。, run_dryrun_with_workflow(), assert_page_signature_node(), ASSERT_PAGE_SIGNATURE 节点入口。, calibrate_locators_node(), CALIBRATE_LOCATORS 节点入口。, AsyncMySQLSaver (+75 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (65): AgentContext, AgentResult, BaseAgent, MySQLImportPreflightReport, MySQLWriteNotConfirmedError, ExcelParseAgent, collect_and_halt(), HaltEvidenceCollector (+57 more)

### Community 2 - "Community 2"
Cohesion: 0.04
Nodes (48): run_dryrun(), build_parser(), _load_json_object(), _load_jsonl_objects(), _load_product_json(), main(), 兼容旧测试和旧脚本的商品 JSON 读取入口。, 兼容旧测试和旧脚本的商品 JSON 读取入口。 (+40 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (49): ArtifactRepository, AssetPipelineReport, AssetPipelineService, ProductAssetRepository, 读写 `jm_product_assets` 表。, 把 VLM 调用审计写入 repository。, 串起 ImageFetchAgent、ImageTransformAgent 和审计 repository。, 把数据库行转换为 ProductAssetRecord。 (+41 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (44): ClipboardFillResult, ClipboardFillService, 使用坐标和剪贴板填充 WebView 字段。, 使用坐标和剪贴板填充 WebView 字段。, SystemClipboardFillService, CoordinatePlan, CoordinatePlanner, Rect (+36 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (41): Command, 返回用于安全策略匹配的归一化文本。          # action/target/label 都可能承载“发布商品”等危险语义。         # 统一转, BaseAgent, ClickCommand, DesktopAgent, DesktopBackend, 桌面 Agent 与可替换 backend。, 只记录命令的 dry-run backend。 (+33 more)

### Community 6 - "Community 6"
Cohesion: 0.04
Nodes (47): _has_assert_allowed_near_start(), main(), 检查桌面动作入口是否调用 SafetyPolicy。, 判断方法体前几条语句是否调用 assert_allowed。, SafetyFinding, scan_file(), scan_path(), ExcelProductParser (+39 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (54): _commit_if_supported(), _fetchone(), _first_int(), import_excel_to_mysql(), import_excel_to_mysql_with_readback(), _missing_readback_rows(), MySQLExcelImportReport, preflight_mysql_import_schema() (+46 more)

### Community 8 - "Community 8"
Cohesion: 0.05
Nodes (36): CacheEntry, MilvusReflectionStore, Milvus failure reflections 写入边界。, 保存 Milvus collection-like 对象。, 封装 OCR/VLM/locator 的 Redis 缓存键。, 保存 Redis 客户端和 key 前缀。, RedisBusinessCache, 渲染多帧 dashboard，模拟实时进度流。 (+28 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (42): MiniMaxReviewClient, ParsedReviewScore, 评审器 HTTP transport 协议。, MiniMax OpenAI-compatible 评审客户端。, 检查 MiniMax-M3 模型是否可用。, 构造 chat/completions 请求体。, ReviewRubricItem, ReviewTransport (+34 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (29): E2ERunReport, E2EStageResult, 转换为 CLI/dashboard 可输出的字典。, draft_verification_from_save_evidence(), DraftVerificationSnapshot, HaltEvidenceSnapshot, normalize_halt_evidence(), 把任意 halt details 规范化为统一现场证据。 (+21 more)

### Community 11 - "Community 11"
Cohesion: 0.09
Nodes (16): DataFetchJob, DataFetchWorker, GuiJob, GuiWorker, ImageProcessJob, ImageProcessWorker, GuiLock, 基于 Redis NX EX 的行级锁封装。 (+8 more)

### Community 12 - "Community 12"
Cohesion: 0.19
Nodes (10): cosine_similarity(), 计算两个向量的余弦相似度。      # 向量维度必须一致，否则相似度没有意义。     # 任一向量为零向量时返回 0，避免除零并表达“没有方向信息”。, calculate_sale_price(), quantize_money(), 计算保守销售价。      # 默认取采购价的 1.2 倍作为候选价。     # 如果候选价超过市场价的 1.1 倍，就收敛到允许上限。     # 返回值始, 把输入金额规整为两位小数。      # 京麦价格字段最终都需要稳定的两位小数。     # 用 Decimal(str(value)) 避免 float 二进, test_calculate_sale_price_caps_by_market_upper_bound(), test_cosine_similarity_handles_normal_vectors() (+2 more)

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (1): `python -m jm_ufo_agent` 入口。

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (1): ASSESS_FORM_COMPLETION 节点入口。

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): MINIMAX_REVIEW_SCORE 节点入口。

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (1): 从 GraphState 或 state dict 构造展示状态。

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): 从 checkpoint 字典恢复 `GraphState`。

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): 从 checkpoint 字典恢复 `GraphState`。

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): 返回 WebView 和 HTML 控件可达性摘要。

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): 基于 Win32 的京麦窗口事实枚举 backend。

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): 判断子窗口是否属于 WebView/Chromium 区域。

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): 用于测试和 dry-run 的静态窗口 backend。

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (1): 返回 v2 计划适配的 UFO v1 底层文件。

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): 返回 WebView 和 HTML 控件可达性摘要。

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): 用于测试和 dry-run 的静态窗口 backend。

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): 从本机 UFO v1 包加载底层能力的占位适配器。

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): 返回 v2 计划适配的 UFO v1 底层文件。

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): 把中止原因、节点和现场证据写入 state.evidence。

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): 从 checkpoint 字典恢复 `GraphState`。

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): 读取商品 JSON。      # Windows PowerShell 对命令行 JSON 引号很容易二次处理。     # 支持 `@path.json`

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): 从 checkpoint 字典恢复 `GraphState`。

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): 读取商品 JSON。      # Windows PowerShell 对命令行 JSON 引号很容易二次处理。     # 支持 `@path.json`

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): 生成待填字段列表。          # verified_fields 是字段级断点恢复结果，已经验证过的字段直接跳过。         # 字段顺序固定，保

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): MiniMax-M3 评审循环的本地可测试边界。

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): 根据完成度和阻断项生成评审决策。          # 有阻断项时直接 halt，不能让评审器掩盖安全/证据问题。         # 完成度不足且仍有循环次数

## Knowledge Gaps
- **68 isolated node(s):** ``python -m jm_ufo_agent` 入口。`, `返回带新增证据的新上下文。          # 不直接修改原 evidence，避免多个节点共享引用后互相污染。         # key 使用调用方给出的`, `判断是否具备真实写操作所需的最小来源能力。`, `扫描本机 UFO v1 源码并生成能力报告。`, `返回 v2 需要适配的 UFO v1 来源文件。` (+63 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 13`** (2 nodes): `__main__.py`, ``python -m jm_ufo_agent` 入口。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (2 nodes): `ASSESS_FORM_COMPLETION 节点入口。`, `assess_form_completion.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (2 nodes): `minimax_review_score.py`, `MINIMAX_REVIEW_SCORE 节点入口。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `从 GraphState 或 state dict 构造展示状态。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `从 checkpoint 字典恢复 `GraphState`。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `从 checkpoint 字典恢复 `GraphState`。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `返回 WebView 和 HTML 控件可达性摘要。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `基于 Win32 的京麦窗口事实枚举 backend。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `判断子窗口是否属于 WebView/Chromium 区域。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `用于测试和 dry-run 的静态窗口 backend。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `返回 v2 计划适配的 UFO v1 底层文件。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `返回 WebView 和 HTML 控件可达性摘要。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `用于测试和 dry-run 的静态窗口 backend。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `从本机 UFO v1 包加载底层能力的占位适配器。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `返回 v2 计划适配的 UFO v1 底层文件。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `把中止原因、节点和现场证据写入 state.evidence。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `从 checkpoint 字典恢复 `GraphState`。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `读取商品 JSON。      # Windows PowerShell 对命令行 JSON 引号很容易二次处理。     # 支持 `@path.json``
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `从 checkpoint 字典恢复 `GraphState`。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `读取商品 JSON。      # Windows PowerShell 对命令行 JSON 引号很容易二次处理。     # 支持 `@path.json``
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `生成待填字段列表。          # verified_fields 是字段级断点恢复结果，已经验证过的字段直接跳过。         # 字段顺序固定，保`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `MiniMax-M3 评审循环的本地可测试边界。`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `根据完成度和阻断项生成评审决策。          # 有阻断项时直接 halt，不能让评审器掩盖安全/证据问题。         # 完成度不足且仍有循环次数`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `GraphState` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 9`, `Community 10`, `Community 11`?**
  _High betweenness centrality (0.108) - this node is a cross-community bridge._
- **Why does `main()` connect `Community 2` to `Community 0`, `Community 1`, `Community 4`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 10`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Why does `AgentResult` connect `Community 1` to `Community 0`, `Community 2`, `Community 4`, `Community 5`, `Community 8`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Are the 83 inferred relationships involving `AgentResult` (e.g. with `DesktopBackend` and `RecordingDesktopBackend`) actually correct?**
  _`AgentResult` has 83 INFERRED edges - model-reasoned connections that need verification._
- **Are the 65 inferred relationships involving `AgentContext` (e.g. with `ExcelParseAgent` and `DownloadedImage`) actually correct?**
  _`AgentContext` has 65 INFERRED edges - model-reasoned connections that need verification._
- **Are the 59 inferred relationships involving `Command` (e.g. with `DesktopBackend` and `RecordingDesktopBackend`) actually correct?**
  _`Command` has 59 INFERRED edges - model-reasoned connections that need verification._
- **Are the 53 inferred relationships involving `GraphState` (e.g. with `使用外部注入 workflow 运行 dry-run。` and `AsyncMySQLSaver`) actually correct?**
  _`GraphState` has 53 INFERRED edges - model-reasoned connections that need verification._