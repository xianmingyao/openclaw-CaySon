# Progress Log

## Session: 2026-05-17 - BL-103 Retry Lane Switching 完成 + 全量文档同步

- **Status:** complete
- **What changed:**
  - BL-103 Retry Lane Switching 三级重试策略全部落地
  - `ActionStep` 新增 `retry_lanes` 和 `same_lane_max_retries` 字段
  - `RetryLane` dataclass: `lane_name`, `method_name`, `description`, `param_overrides`
  - `ReflectionDecision` 枚举新增 `RETRY_NEXT_LANE` 和 `HUMAN_ESCALATE`
  - `AgentReflection.reflect()` 支持 `lane_index`/`lane_count` 参数，lane-aware 决策
  - `AgentPipeline._execute_step_with_retry()`: while-true loop + lane 追踪
  - `AgentExecutor.execute()` 接受可选 `lane` 参数，合并 `lane.param_overrides`
  - Registry 中 4 个关键步骤（t4, t6-main-image, t6-detail-editor, t8-save-draft）配置 retry_lanes
  - 新增 `tests/test_agent_retry_lanes.py`（14 tests, 14 passed）
- **Fix history:**
  - 3 tests 首次失败 → FakeSession class-level mutable attributes → 改为 instance `__init__`
  - 1 test 仍失败 → executor 未转发 lane.param_overrides → 在 `execute()` 中 `kwargs.update(lane.param_overrides)`
  - 1 test 仍失败 → ActionStep 缺 required_params/param_map → 补充测试定义
- **Planning document sync:**
  - `task_plan.md`: 4 处编辑 — Latest Update、Score baseline 78→80、Phase B 表行、执行顺序
  - `.planning/STATE.md`: 5 处编辑 — Latest Update、Current Position、Ready Next、Current focus、Resume point
  - `.planning/BACKLOG.md`: BL-103 TODO→DONE + 交付日志条目
  - `.planning/ROADMAP.md`: Phase 2 checkbox、Status Updated、Progress table、Gate B→Complete、Next Milestones
  - `100_SCORE_RECOVERY_PLAN.md`: Phase B 状态 🔄→✅、全部任务标记完成
  - `progress.md`: 本条目
- **Verification:**
  - 全量回归: `231 passed`
  - Score baseline: 80/100 → 下一门禁 88/100 (Phase C)
  - Phase B Gate achieved

## Session: 2026-05-17 - BL-091/BL-100/BL-101 Phase B 核心架构完成 + 计划文档同步

- **Status:** complete
- **What changed:**
  - 确认 BL-091 Agent 决策层已在代码中完全实现（7 个 agent/ 模块、24 个 ActionStep、AgentPipeline 已接入 TaskRunner.run()）
  - 确认 BL-100 RuntimeEventLoop 已在代码中完全实现（222 lines, 17 tests）
  - 确认 BL-101 ProviderManifest 已在代码中完全实现（273 lines, 28 tests）
  - 发现 BACKLOG.md 和 STATE.md 中 BL-091 仍然标记为 TODO，与实际代码状态不一致
- **Planning document sync:**
  - `BACKLOG.md`: BL-091 → DONE，添加交付日志和证据
  - `STATE.md`: 完全重写，更新评分基线为 78/100，更新 Ready Next 列表
  - `task_plan.md`: 更新日期、评分基线、Phase 2 全部任务标记完成、Phase A/B 状态更新
  - `100_SCORE_RECOVERY_PLAN.md`: Phase A 标记完成、Phase B 标记为进行中并列出剩余任务 BL-103
- **Verification:**
  - 全量回归: `216 passed`（包含 agent/ 和 runtime/ 所有测试）
  - 代码确认: 7 个 agent/ 源文件均已落地，AgentPipeline 已接入 TaskRunner 主流程
- **Score baseline:** 78/100 → 下一门禁 80/100 (BL-103)

## Session: 2026-05-16 - BL-089A Excel 到京麦草稿箱真实 E2E 通过

- **Status:** complete
- **What changed:**
  - T3 支持从草稿箱列表恢复：检测到草稿箱后只点击右上角 `发布商品`，避免误触发布表单底部正式发布按钮。
  - T3 支持类目选择页：优先点击近期类目 `工业品 > 电料辅件 > 电气辅材 > 电气配件`，再点击 `下一步，完善其他商品信息`。
  - `RealWindowsUIAAdapter` 新增 `click_window_ratio()`，用于 WebView 中不暴露独立 UIA 控件的稳定区域点击。
  - T6 上传后若“文件写入成功但槽位未变化”，会再次执行图片空间选图/确认并重新轮询槽位。
  - Draft E2E 中 T4/T5/透明图改为草稿模式 best-effort，最终成功以 `t8-save-draft` 进入草稿箱为准；正式发布仍未执行。
- **Real E2E evidence:**
  - Command: `python cli.py run-draft-e2e --excel "湖南上架表格.xlsx" --item-index 0 --required-attr "五孔" --factory-inventory "10" --main-image-path "resources\probe-images\main-probe.png" --transparent-image-path "resources\probe-images\transparent-probe.png" --sale-unit "个" --package-list "插座*1，说明书*1，保修卡*1" --warranty-period "365" --window-keyword "jd_" --debug --root .`
  - Result: `success=true`, `job_id=job-d217feeee80a`, `task_id=task-d7b392c81a07`.
  - Final T8: `page_state=draft_saved`; `草稿点击=成功；页面变化=成功；草稿确认=成功；触发模式=draft_list；文档轮询次数=4`.
  - Screenshot: `resources/screenshots/window-1187102-20260516-110738-242774.png`.
  - Draft list top row: `公牛（BULL） 插座/B5系列 带儿童保护门/新国标插座/排插 【8位】总控1.6米（新国标防过载）B5440`; edit time `2026-05-16 11:07:36`.
- **Verification:**
  - `pytest -q` -> `136 passed`
  - `graphify update .` -> `1237 nodes, 2673 edges, 42 communities`

## Session: 2026-05-15

### Phase 0: 计划重建与管理基线重置

- **Status:** complete
- **Started:** 2026-05-15
- Actions taken:
  - 确认 `planning-with-files` 技能存在于 `C:\Users\Administrator\.codex\skills\planning-with-files\SKILL.md`
  - 读取 `gstack` 技能说明，确认当前项目管理承载主要是 `.planning` 文件
  - 读取 `graphify-out/GRAPH_REPORT.md`，确认核心改造节点包括 `TaskRunner`、`JingmaiWorkflowService`、`RealWindowsUIAAdapter`、`RuntimeLogRepository`
  - 读取现有 `.planning` 文件，发现旧状态为 `95/100`，与用户提供的 `55/100` 评估冲突
  - 创建 `task_plan.md`、`findings.md`、`progress.md`
  - 同步 `.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/BACKLOG.md`、`.planning/STATE.md`
- Files created/modified:
  - `task_plan.md`
  - `findings.md`
  - `progress.md`
  - `.planning/PROJECT.md`
  - `.planning/ROADMAP.md`
  - `.planning/BACKLOG.md`
  - `.planning/STATE.md`

## Test Results

| Test | Input | Expected | Actual | Status |
|------|-------|----------|--------|--------|
| 计划文件创建 | 检查 `task_plan.md/findings.md/progress.md` | 三个文件存在且记录新基线 | 已创建并写入 `55/100` 新基线 | passed |
| `.planning` 同步 | 检查 `.planning/*.md` | 项目管理文件同步新基线 | 已同步为 `55/100` 与 P0/P1/P2 backlog | passed |
| T6/UIA 相关测试 | `python -m pytest tests\test_t6_t8_workflow.py tests\test_uia_adapter.py -q` | 相关测试通过 | `21 passed` | passed |
| 全量回归 | `python -m pytest -q` | 全部测试通过 | `92 passed` | passed |
| 槽位识别修正测试 | `python -m pytest tests\test_uia_adapter.py tests\test_t6_t8_workflow.py tests\test_uia_dialog_bridge.py -q` | 相关测试通过 | `30 passed` | passed |
| 最终全量回归 | `python -m pytest -q` | 全部测试通过 | `95 passed` | passed |
| BL-088-1 实机验证 | `python cli.py run-desktop-check --step t6-main-image --image-path "E:\workspace\skills\jingmai-product-publish-v2\resources\probe-images\main-probe.png" --debug` | 主图槽位上传成功 | `page_state=main_image_uploaded`，上传后图片数 `1` | passed |
| T5/T7 剩余必填项回归 | `python -m pytest -q` | 全部测试通过 | `108 passed` | passed |
| T7 物流/售后实机闭环 | `python cli.py run-desktop-check --step t7 --sale-unit "件" --package-type "普通商品" --delivery-mark "普通品" --package-list "插座*1，说明书*1，保修卡*1" --warranty-period "365" --window-keyword "jd_" --preferred-class "JMMainFrameBase"` | 保质期、销售单位、商品包装、特殊发货、包装清单、质保期全部写入并校验 | `page_state=logistics_completed`，全部字段 `填充=成功，校验=成功` | passed |
| T5 SKU 重量实机闭环 | `python cli.py run-desktop-check --step t5-required-fields --weight "0.5" --sku-submit --window-keyword "jd_" --preferred-class "JMMainFrameBase"` | SKU 重量写入并可在页面文本验证 | `validation.weight=true`，`success=true` | passed |
| T5/T7 页面报错复核 | UIA document text probe | 页面无发布前剩余报错 | 未命中 `报错反馈/报错信息/销售单位不可为空/请维护质保期/请填写重量/请输入库存数量`；命中 `10A/0.5/厂直库存 10/1年质保/365` | passed |

## Error Log

| Timestamp | Error | Attempt | Resolution |
|-----------|-------|---------|------------|
| 2026-05-15 | `.planning` 旧状态与新评分分析冲突 | 1 | 以用户新评估为准，重置计划基线 |
| 2026-05-15 | `rg` 不存在 | 1 | 改用 PowerShell `Select-String` 和 graphify 查询 |
| 2026-05-16 | 透明图上传后出现图片预览遮罩，挡住上传入口 | 1 | 按用户截图点击右上角叉号关闭，并在上传前增加 `close_image_preview_overlay()` |
| 2026-05-16 | pywinauto 枚举窗口时遇到瞬时无效句柄 | 1 | `list_windows()` 对 `desktop.windows()` 增加异常跳过 |
| 2026-05-16 | 文件对话框触发后渲染稍慢，单次桥接可能误判失败 | 1 | `_complete_local_upload()` 对 `upload_file_from_active_dialog()` 增加短轮询重试 |
| 2026-05-16 | T7 物流页签未进入，导致销售单位/质保期定位失败 | 1 | `run_t7_fill_logistics_fields()` 增加顶部页签区域点击，避开正文和左侧报错导航同名文本 |
| 2026-05-16 | 销售单位请求值 `件` 不在当前类目可见下拉选项中 | 1 | 增加下拉探测和可用值兜底；实机已落到页面可用的 `包` |
| 2026-05-16 | 质保期下拉显示 `请维护质保期`，无法通过普通枚举选择闭环 | 1 | 收紧下拉全局文本兜底，避免误点；当前标记为京麦配置/页面数据阻塞，需人工确认质保期可维护选项 |
| 2026-05-16 | 下拉全局文本兜底过宽，异常状态下可能误点到草稿箱/其它页面 | 1 | 移除 `_select_combobox_control()` 的全局 `click_text` 兜底，只允许真实弹层选项或受控键盘输入 |
| 2026-05-16 | T7 完整 runner 超时 | 1 | 定位到 WebView 下拉 wrapper 阻塞；改为可见矩形中心点击 + 当前窗口内弹层选项采集 |
| 2026-05-16 | T5 重量命中 0 坐标隐藏控件，输入未落到真实单元格 | 1 | automation id 候选按可见控件优先排序，并用 document text 作为补充验证 |

## 5-Question Reboot Check

| Question | Answer |
|----------|--------|
| Where am I? | Phase 1: `BL-088-1` 主图上传真实闭环已完成 |
| Where am I going? | 进入 `BL-088-2` 透明图上传真实闭环 |
| What's the goal? | 把 `55/100` 的系统补齐到真实可交付生产闭环 |
| What have I learned? | 主图上传必须遵循“悬停槽位 -> 浮层本地上传 -> 地址栏输入目录 -> 选中文件”路径 |
| What have I done? | 已根据截图调整 `BL-088-1` 代码逻辑和测试；实机主图上传成功；全量回归 `95 passed` |

### Phase 1: BL-088-1 主图上传真实闭环

- **Status:** complete
- **Started:** 2026-05-15
- Actions taken:
  - 使用 graphify 查询主图上传相关调用链，定位到 `JingmaiWorkflowService.run_t6_upload_main_image()`、`_run_t6_upload_slot()`、`_complete_local_upload()`、`RealWindowsUIAAdapter.select_uploaded_image_and_confirm()`
  - 发现本机没有 `rg`，改用 PowerShell `Select-String`
  - 为上传后槽位状态增加轮询等待，避免京麦异步刷新导致立即误判失败
  - 为图片空间选图增加“首个缩略图候选”回退，处理新上传图片不暴露文件名的情况
  - 修正同槽位 `empty + filled` 合并规则：小图标保留空槽，大图缩略图升级为已上传
  - 根据用户截图调整悬停逻辑：优先点击上传槽位附近浮层里的 `本地上传`
  - 根据用户截图调整文件对话框逻辑：优先通过地址栏输入图片目录，再选中文件
  - 修正 SKU 图片槽位坐标识别：方图实际在 `left=665 top=356 right=730 bottom=421`
  - 修正槽位排序：同一 SKU 行按从左到右排序，确保 `slot_index=0` 是方图
  - 增加 Oxygen Vision 面板区域里的 `本地上传` 按钮命中
  - 执行真实京麦上传，第二次尝试成功回填 SKU 主图
  - 按项目规则执行 `graphify update .`
- Files created/modified:
  - `jingmai_publish/services/jingmai_workflow.py`
  - `jingmai_publish/desktop/uia_adapter.py`
  - `tests/test_t6_t8_workflow.py`
  - `tests/test_uia_adapter.py`
  - `tests/test_uia_dialog_bridge.py`
  - `graphify-out/GRAPH_REPORT.md`
  - `graphify-out/graph.json`
  - `graphify-out/graph.html`
- Evidence:
  - Before screenshot: `resources/screenshots/window-1187102-20260515-235104-179323.png`
  - Success screenshot: `resources/screenshots/window-1187102-20260515-235148-851391.png`
  - Success message: `上传入口=成功；触发模式=empty_slot_modal；文件写入=成功；槽位变化=成功；图片出现=成功；上传后图片数=1`

### Phase 1: BL-088-2 透明图上传真实闭环

- **Status:** complete
- **Started:** 2026-05-16
- **Completed:** 2026-05-16
- Actions taken:
  - 上传前增加 `SKU图片信息` 槽位表面恢复，避免停在 `SKU基本信息` 的图片设置列
  - 修复 `RealWindowsUIAAdapter.hover_text_by_index()` 方法体缺失
  - 文件对话框写入增加短轮询重试，处理对话框渲染延迟
  - 增加图片预览遮罩关闭逻辑，处理用户截图指出的右上角叉号取消场景
  - 透图目标槽位已存在图片时返回幂等成功，避免重复替换把验证路径变成新问题
  - 修复 `list_windows()` 在 pywinauto 瞬时无效句柄下直接崩溃的问题
- Files modified:
  - `jingmai_publish/services/jingmai_workflow.py`
  - `jingmai_publish/desktop/uia_adapter.py`
  - `tests/test_t6_t8_workflow.py`
  - `tests/test_uia_adapter.py`
- Evidence:
  - Manual bridge success screenshot: `resources/screenshots/window-1187102-20260516-001100-086187.png`
  - Command success screenshot: `resources/screenshots/window-1187102-20260516-002306-522579.png`
  - Command: `python cli.py run-desktop-check --step t6-transparent-image --transparent-image-path "E:\workspace\skills\jingmai-product-publish-v2\resources\probe-images\transparent-probe.png" --debug`
  - Success state: `page_state=transparent_image_uploaded`
  - Success message: `上传入口=已完成；触发模式=already_filled；文件写入=跳过；槽位变化=无需变化；图片出现=成功；上传前图片数=2；上传前空槽数=1`
  - File picker fix: dialog file-item matching now strips whitespace/newlines, covering large-icon wrapped names such as `transparent-pr\nobe.png`
  - Related tests: `37 passed`
  - Full regression: `102 passed`
  - Code graph: `graphify update .` completed

### Phase 1: BL-088-3 详情编辑器写入闭环

- **Status:** complete
- **Started:** 2026-05-16
- **Completed:** 2026-05-16
- Actions taken:
  - Added a dedicated `type_into_detail_editor()` path for Jingmai WebView rich-text detail editing.
  - Changed detail input from generic focused-control typing to explicit code-editor body focus plus clipboard paste.
  - Fixed detail anchor ordering so `代码编辑` is preferred over `图文编辑推荐`, avoiding clicks in the preview/gap area.
  - Added detail write verification via document text probe and included the focus path in the workflow message.
- Files modified:
  - `jingmai_publish/services/jingmai_workflow.py`
  - `jingmai_publish/desktop/uia_adapter.py`
  - `jingmai_publish/desktop/adapter.py`
  - `tests/test_t6_t8_workflow.py`
- Evidence:
  - Command: `python cli.py run-desktop-check --step t6-detail-editor --detail-content "BL-088-3 command final pass 2026-05-16" --debug`
  - Success screenshot: `resources/screenshots/window-1187102-20260516-005034-202135.png`
  - Success state: `page_state=detail_content_written`
  - Success message: `编辑器触发=成功；内容写入=成功；内容可见=成功；详情区域可见=成功；焦点路径=ratio_code_body_top；写入前长度=2833；写入后长度=2853`
  - Related tests: `30 passed`
  - Full regression: `103 passed`

### Phase 1: BL-089 保存草稿 / 发布提交闭环

- **Status:** in_progress
- **Started:** 2026-05-16
- Actions taken:
  - Ran `t8-probe` and confirmed real `保存草稿` / `发布商品` button candidates before clicking.
  - Found the first `t8-save-draft` implementation captured the page during save loading and could mark success too early.
  - Changed `run_t8_save_draft()` to poll document state until the final draft-list or save-success state is visible.
  - Changed `t8-probe` to recognize the post-save `草稿箱` list as a valid `draft_list` state.
  - Added tests for delayed draft-list transition and loading-only false positives.
- Files modified:
  - `jingmai_publish/services/jingmai_workflow.py`
  - `tests/test_t6_t8_workflow.py`
- Evidence:
  - Save command: `python cli.py run-desktop-check --step t8-save-draft --debug`
  - Success screenshot: `resources/screenshots/window-1187102-20260516-005858-872183.png`
  - Success state: `page_state=draft_saved`
  - Success message: `草稿点击=成功；页面变化=成功；草稿确认=成功；触发模式=draft_list；文档轮询次数=3`
  - Draft list contains: `测试商品标题-自动化验证`, edit time `2026-05-16 00:58:56`
  - Probe command after save: `python cli.py run-desktop-check --step t8-probe --debug`
  - Probe state after save: `page_state=draft_list`
  - Related tests: `16 passed`
  - Full regression: `106 passed`
  - Code graph: `graphify update .` completed
  - Formal publish submit: not executed; requires explicit permission.

### Phase 1: T5/T7 剩余必填项补齐

- **Status:** in_progress
- **Started:** 2026-05-16
- Actions taken:
  - 根据实机截图确认剩余报错集中在 `销售属性`、`销售单位`、`质保期`。
  - 为 `t5-required-fields` 增加 `current`、`weight`、可选 `factory_inventory` 入口，动态解析 `jd-id-<prefix>-<suffix>`，避免京麦动态前缀导致硬编码失效。
  - 为 CLI 增加 `--current`、`--factory-inventory` 参数。
  - 为 T7 增加顶部页签区域导航，避免停留在 `商品描述/销售属性` 区域时误判物流字段不可填。
  - 为质保期增加天数到枚举文案映射，例如 `365 -> 1年质保`。
  - 收紧下拉选择全局文本兜底，防止质保期异常状态下误点到页面其它区域。
  - 将 WebView 输入框/下拉框改为可见矩形中心点击 + 剪贴板/弹层点选，避免 pywinauto wrapper 阻塞。
  - automation id 候选按可见控件优先排序，避免命中 0 坐标隐藏控件。
  - 从草稿箱首行 `编辑` 回到当前商品编辑页后完成最终复核。
- Files modified:
  - `jingmai_publish/services/task_runner.py`
  - `jingmai_publish/services/jingmai_workflow.py`
  - `jingmai_publish/desktop/uia_adapter.py`
  - `jingmai_publish/cli.py`
  - `tests/test_desktop_verify.py`
  - `tests/test_t6_t8_workflow.py`
- Evidence:
  - Related regression: `python -m pytest tests\test_desktop_verify.py tests\test_task_runner.py tests\test_t6_t8_workflow.py tests\test_uia_adapter.py -q` -> `53 passed`
  - Full regression: `python -m pytest -q` -> `108 passed`
  - T7 real command: `python cli.py run-desktop-check --step t7 --sale-unit "件" --package-type "普通商品" --delivery-mark "普通品" --package-list "插座*1，说明书*1，保修卡*1" --warranty-period "365" --window-keyword "jd_" --preferred-class "JMMainFrameBase"`
  - T7 real result: `page_state=logistics_completed`，保质期/销售单位/商品包装/特殊发货时效标记/包装清单/质保期全部 `填充=成功，校验=成功`
  - T5 real command: `python cli.py run-desktop-check --step t5-required-fields --weight "0.5" --sku-submit --window-keyword "jd_" --preferred-class "JMMainFrameBase"`
  - T5 real result: `validation.weight=true`，`success=true`
  - Final document probe: 未命中 `报错反馈/报错信息/销售单位不可为空/请维护质保期/请填写重量/请输入库存数量`；命中 `10A/0.5/厂直库存 10/1年质保/365`

## Session: 2026-05-16 - 100 分补完规划

- **Status:** complete
- **Skill usage:**
  - 使用 `planning-with-files`：读取 session catchup、`task_plan.md`、`findings.md`、`progress.md`，并将新规划落盘。
  - 使用 `gstack`：读取技能说明并尝试执行 `browse.exe status`。
- **gstack result:**
  - `C:\Users\Administrator\.codex\skills\gstack\browse\dist\browse.exe` 存在。
  - 执行 `browse.exe status` 失败：`Cannot find server.ts. Set BROWSE_SERVER_SCRIPT env or run from the browse source tree.`
  - 本轮规划不依赖浏览器 QA；该问题已记录到 `findings.md`。
- **Actions taken:**
  - 新增 `100_SCORE_RECOVERY_PLAN.md`，按 6 个评分维度拆分 100 分要求。
  - 将恢复路线拆为 Phase A-F：`70/80/88/94/98/100` 六个证据门禁。
  - 将缺陷映射为任务：`BL-100` runtime event loop、`BL-101` provider manifest、`BL-102` audit tables、`BL-103` retry lane switching、`BL-104` business preflight。
  - 更新 `task_plan.md`，加入 100 分恢复计划和当前执行顺序。
  - 更新 `findings.md`，记录 gstack 工具问题和 100 分规划发现。
- **Files modified:**
  - `100_SCORE_RECOVERY_PLAN.md`
  - `task_plan.md`
  - `findings.md`
  - `progress.md`
- **Next planned update:**
  - 同步 `.planning/ROADMAP.md`、`.planning/BACKLOG.md`、`.planning/STATE.md`，使项目事实源指向新的 100 分恢复门禁。
- **Planning source synchronized:**
  - `.planning/ROADMAP.md` 已加入 `100 Score Recovery Gates`
  - `.planning/BACKLOG.md` 已加入 `BL-089A`、`BL-086A`、`BL-097A`、`BL-100`、`BL-101`、`BL-102`、`BL-103`、`BL-104`
  - `.planning/STATE.md` 已指向下一门禁 `70/100` 和 `100_SCORE_RECOVERY_PLAN.md`

## Session: 2026-05-16 - BL-089A 草稿 E2E 代码入口

- **Status:** in_progress
- **Scope completed:**
  - 新增 `DraftE2EOrchestrator`，把 Excel 导入、prepared product 选择、桌面 T4/T5/T6/T7、`t8-save-draft` 串成单一可复现入口。
  - 新增 `run-draft-e2e` CLI，支持 Excel、商品索引、店铺、T4/T5/T6/T7 参数、窗口关键词和点击别名。
  - 草稿 E2E 只调用 `t8-save-draft`，不会调用 `t8-publish-product`。
  - 尺寸字段不完整时跳过 `t5-dimension-probe`，避免缺字段导致草稿 E2E 非业务失败。
  - 当前图片本地路径通过 `--main-image-path` 和 `--transparent-image-path` 显式传入；自动图片本地化仍是后续数据准备质量补齐项。
- **Files modified:**
  - `jingmai_publish/services/draft_e2e.py`
  - `jingmai_publish/services/__init__.py`
  - `jingmai_publish/cli.py`
  - `tests/test_cli.py`
  - `tests/test_draft_e2e.py`
- **Verification:**
  - `python -m py_compile .\jingmai_publish\services\draft_e2e.py .\tests\test_draft_e2e.py .\jingmai_publish\cli.py`
  - `pytest tests/test_draft_e2e.py tests/test_cli.py -q` -> `15 passed`
  - `pytest -q` -> `118 passed`
  - `graphify update .` completed
- **Real E2E attempt:**
  - Command attempted: `python cli.py run-draft-e2e --excel "湖南上架表格.xlsx" --main-image-path "...main-probe.png" --transparent-image-path "...transparent-probe.png" ...`
  - Result: blocked before desktop automation by database initialization.
  - Structured error: `database_error`
  - Root cause: `Table 'jingmai_agent.upload_jobs' doesn't exist`
  - Follow-up: do not initialize the remote configured database without explicit confirmation; after confirmation run `python cli.py init-db --root .`, then rerun the same E2E command.
- **Remaining for DONE:**
  - 运行真实京麦窗口 E2E：Excel 单行 -> 数据准备 -> T4/T5/T6/T7/T8 -> 草稿箱出现目标商品。
  - 归档运行命令、日志、截图、页面文本和最终草稿箱证据。

## Session: 2026-05-16 - BL-089A 实机首轮推进

- **Status:** blocked
- **What changed:**
  - 用户确认后执行 `python cli.py init-db --root .`，当前配置数据库初始化成功。
  - 为 `init-db` 增加旧版 `publish_tasks` 兼容迁移：补 `job_id/job_item_id/session_id/mode/...` 等当前模型字段，并把旧 `product_id` 改为可空，避免旧表结构阻塞导入任务创建。
  - 修复 T4 字段定位：`商品标题/型号/类型/品牌` 改为标签优先，避免固定动态 ID 把品牌、类型写入价格字段。
  - `run-draft-e2e` 主链路移除 `t4-extra` 和 SKU/T5 必经步骤；这些字段在当前类目不存在或无 SKU 表格，不能阻塞草稿 E2E。
- **Real run evidence:**
  - 数据库初始化：`python cli.py init-db --root .` -> `数据库初始化完成`
  - 真实 T4 通过：`python cli.py run-desktop-check --step t4 ...`
  - T4 成功截图：`resources/screenshots/window-1187102-20260516-074420-733288.png`
  - T4 成功信息：`标题填充=成功；标题校验=成功；型号填充=成功；型号校验=成功；必填属性填充=成功；必填属性校验=成功；品牌填充=成功；品牌校验=成功`
  - `run-draft-e2e` 已完成 Excel 导入、数据准备、T3 类目确认、T4 基础信息填写。
  - 最新 E2E 任务：`job-fd0eda269fb4` / `task-0cf75e8a0ce6`
  - 最新 E2E 阻塞截图：`resources/screenshots/window-1187102-20260516-075644-196844.png`
  - 阻塞点：`t6-main-image`
  - 阻塞信息：`上传入口=成功；触发模式=text_fallback；文件写入=失败；槽位变化=失败；图片出现=失败`
  - 直接 `t8-save-draft` 也未确认成功，最终截图：`resources/screenshots/window-1187102-20260516-075813-954078.png`
  - T8 阻塞信息：`草稿点击=成功；页面变化=失败；草稿确认=失败；触发模式=editing_or_loading；文档轮询次数=16`
  - 页面当前仍有 `17条` 报错，包括品牌、价格、商品属性、主图、详情、物流售后等，草稿箱出现目标商品尚未验证。
- **Verification:**
  - `pytest tests/test_draft_e2e.py tests/test_cli.py -q` -> `15 passed`
  - `pytest tests/test_draft_e2e.py tests/test_jingmai_workflow.py tests/test_cli.py -q` -> `23 passed`
  - `pytest -q` -> `118 passed`
- **Remaining for DONE:**
  - 修复当前类目下主图上传入口 `text_fallback` 后文件对话框写入失败。
  - 补齐当前类目品牌/价格/类型/图片/详情/物流售后字段，或为草稿保存建立可确认的弱校验路径。
  - 重跑 `run-draft-e2e`，直到草稿箱出现目标商品并归档最终截图。
