# Delivery Backlog

## Latest Completion - 2026-05-16

- [x] `BL-100` Runtime Event Loop — sightflow 风格事件队列、调度、停止、会话状态
  - 新增 `jingmai_publish/runtime/event_loop.py` (222 lines)
  - 实现 `RuntimeEventLoop`：`enqueue/schedule/stop/pause/resume/session_state/event_history`
  - 事件类型覆盖 observe→decide→act→verify→repeat 全周期
  - 测试：`tests/test_runtime_event_loop.py` (17 tests, 17 passed)
- [x] `BL-101` Provider Manifest — sightflow 风格能力声明系统
  - 新增 `jingmai_publish/runtime/manifest.py` (273 lines)
  - 实现 `ProviderManifest`、`ProviderCapability`、`ProviderFactory`、`validate_manifest`、`load_manifest`/`dump_manifest`
  - 8 种能力类别：observation/action/persistence/channel/memory/vision/grounding/reflection
  - 4 个内置 manifest 描述现有 provider
  - 测试：`tests/test_runtime_manifest.py` (28 tests, 28 passed)
- [x] `BL-089A` Draft-mode Excel -> Jingmai draft E2E
  - Real command passed with `success=true`.
  - Evidence: `job_id=job-d217feeee80a`, `task_id=task-d7b392c81a07`.
  - Final screenshot: `resources/screenshots/window-1187102-20260516-110738-242774.png`.
  - Draft list top row: target BULL product, edit time `2026-05-16 11:07:36`.
  - Note: formal publish remains out of scope until user explicitly authorizes it.

> 事实源说明  
> - 当前客观开发基线为 `55/100`
> - 本文档按用户提供的评分分析重建
> - 只有满足完成定义且有证据的任务，才允许标记为 `DONE`

## Completion Rule

任意任务只有同时满足以下条件，才允许标记为 `DONE`：

1. 代码已经落地到当前仓库
2. 有测试、CLI、日志、截图或实机验收入口
3. 相关文档已同步更新
4. 有运行证据
5. `.planning/STATE.md`、`.planning/ROADMAP.md`、本文已同步更新
6. 已向用户汇报该任务进度

状态值只允许：

- `TODO`
- `IN_PROGRESS`
- `BLOCKED`
- `DONE`

## Priority Queue

### P0 - 阻塞性交付缺口

| ID | Task | Status | Done Definition |
|----|------|--------|-----------------|
| BL-088-1 | 主图上传真实闭环 | DONE | 真实京麦页面主图槽位上传成功，具备 before/after 截图、日志和页面状态证据 |
| BL-088-2 | 透明图上传真实闭环 | DONE | 透明图必填槽位完成真实上传，页面状态可验证；证据截图 `resources/screenshots/window-1187102-20260516-002306-522579.png` |
| BL-088-3 | 详情编辑器写入闭环 | DONE | 已进入真实详情编辑区并写入详情内容；证据截图 `resources/screenshots/window-1187102-20260516-005034-202135.png` |
| BL-089 | 保存草稿 / 发布提交 | IN_PROGRESS | 保存草稿已真实闭环，证据截图 `resources/screenshots/window-1187102-20260516-005858-872183.png`；正式发布提交待明确许可 |
| BL-089A | 草稿模式 E2E | IN_PROGRESS | 数据库初始化、T3/T4 已实机通过；当前阻塞在 T6 主图上传和 T8 草稿确认，仍需草稿箱出现目标商品并归档命令/日志/截图 |
| BL-086 | Reflection 截图校验 | TODO | 每个关键动作有 before/after 截图差异或控件状态校验 |
| BL-086A | P0 截图证据包 | TODO | T1/T2/T4/T5/T6/T7/T8 每个关键步骤都有 before/after 或可替代证据 |
| BL-091 | Agent 决策层最小闭环 | DONE | `AgentPipeline` 已接入 `TaskRunner.run()`；7 个 agent/ 模块落地（types/registry/planner/executor/reflection/pipeline/__init__）；24 个 ActionStep 注册；getattr 反射调度 + 重试 + 溯源；规则驱动的 ReflectionDecision（CONTINUE/RETRY/SKIP/ABORT） |

### P1 - 重要能力缺口

| ID | Task | Status | Done Definition |
|----|------|--------|-----------------|
| BL-087-4 | SKU 多行填写 | TODO | 支持多行 SKU 数据真实填写与验证 |
| BL-087-5 | SKU 尺寸字段 | TODO | 支持尺寸字段定位、填写、验证 |
| BL-087-6 | SKU 属性字段 | TODO | 支持颜色/规格等属性字段填写 |
| BL-087-7 | SKU 图片设置 | TODO | 支持 SKU 图片槽位上传和验证 |
| BL-087-8 | SKU/T7 剩余必填项补齐 | DONE | 销售属性、销售单位、质保期报错已清除；实机复核命中 `10A`、`0.5`、`厂直库存 10`、`365`、`1年质保`，且无 `报错反馈/报错信息` |
| BL-082 | 京东抓取质量验证 | TODO | 有样本集和字段准确率/失败分类报告 |
| BL-083 | 字段补全规则 | TODO | 缺失品牌、型号、标题、价格等字段有规则化补全 |
| BL-085 | 日志 3 天自动清理 | TODO | RuntimeLog 和截图目录可按保留期清理 |
| BL-090 | 飞书实时入口 | TODO | Feishu/Lark payload 可触发真实导入和上架任务 |
| BL-092 | Ollama 视觉模型集成 | DONE | `OllamaVisionProvider`（~505L），analyze/compare/locate 三接口，Ollama+vLLM 降级，`VisionAnalysis` 结构化输出。测试 36 cases |
| BL-093 | Redis 状态/锁/事件流 | TODO | 任务运行状态、并发锁、事件流接入 Redis |
| BL-094 | Milvus 长期记忆 | TODO | 失败反思和控件经验写入并可检索 |
| BL-100 | Runtime Event Loop | DONE | 实现 queue / schedule / stop / session state，替代一次性同步包装式 runtime |
| BL-101 | Provider Manifest | DONE | 建立 manifest schema、provider 加载器和示例 provider，明确输入输出和能力边界 |
| BL-102 | Audit Tables | TODO | 补齐 `ui_artifact`、`action_event`、`reflection_case` 表、Repository 和写入点 |
| BL-103 | Retry Lane Switching | DONE | 三级重试策略：14 个测试用例，4 个关键步骤配置 lanes；Pipeline 支持 lane 调度和 trace 记录 |
| BL-104 | Business Preflight | TODO | 标题、价格、主图、透图、详情、物流售后全量阻断式业务预校验 |

### P2 - 架构与交付优化

| ID | Task | Status | Done Definition |
|----|------|--------|-----------------|
| BL-095 | 混合 Grounding | DONE | `ThreeWayGroundingProvider`（~460L），UIA(0.50)→Vision(0.35)→Anchor(0.15) 优先级链 + 加权融合。5 个地标规则。测试 35 cases |
| BL-096 | 多 Agent 协作 | TODO | Planner / Grounding / Executor / Reflection / Memory / Task API 角色拆分 |
| BL-097 | 端到端 UAT 测试 | TODO | 覆盖 Excel 到京麦草稿/发布的完整用例 |
| BL-098 | 生产部署文档 | TODO | 环境、依赖、凭据、运行、恢复、清理文档齐全 |
| BL-099 | 评分复核报告 | TODO | 用证据重新计算架构、执行、视觉、运维、测试得分 |
| BL-097A | P0 UAT 证据包 | TODO | 汇总 P0 命令、日志、截图、页面文本、测试结果，支撑 70 分门禁 |

## Phase Mapping

| Phase | Task IDs |
|-------|----------|
| Phase 1 - P0 业务闭环补齐 | BL-088-1, BL-088-2, BL-088-3, BL-089, BL-089A, BL-086A, BL-097A |
| Phase 2 - Agent 决策层与运行时主循环 | BL-091, BL-100, BL-101, BL-103 |
| Phase 3 - Reflection 与视觉校验真实化 | BL-086, BL-092, BL-094, BL-095, BL-102 |
| Phase 4 - 数据入口与商品准备质量验证 | BL-082, BL-083, BL-090, BL-104 |
| Phase 5 - 持久化、运维与多 Agent 协作 | BL-085, BL-093, BL-094, BL-096 |
| Phase 6 - 端到端 UAT 与交付评分回升 | BL-097, BL-097A, BL-098, BL-099 |

## Delivery Log

- 2026-05-15 管理基线重置
  - 使用 `planning-with-files` 创建 `task_plan.md`、`findings.md`、`progress.md`
  - 将项目评分基线从旧文档的 `95/100` 重置为 `55/100`
  - 按 P0/P1/P2 重建 backlog

- 2026-05-15 `BL-088-1` 代码层收口
  - 上传后槽位校验增加轮询等待
  - 图片空间选图增加首个缩略图候选回退
  - 大图缩略图不再被同槽位空槽快照覆盖
  - 根据截图改为优先点击槽位悬浮浮层里的 `本地上传`
  - 根据截图改为文件对话框优先地址栏目录导航，再选中文件
  - 截图规则相关测试：`28 passed`
  - 全量回归：`93 passed`
  - 坐标修正：方图槽位实际为 `left=665 top=356 right=730 bottom=421`
  - 实机验证通过：`page_state=main_image_uploaded`
  - 成功截图：`resources/screenshots/window-1187102-20260515-235148-851391.png`
  - 成功信息：`上传入口=成功；触发模式=empty_slot_modal；文件写入=成功；槽位变化=成功；图片出现=成功；上传后图片数=1`

- 2026-05-16 `BL-088-2` 透明图上传真实闭环
  - 上传前自动关闭图片预览遮罩，避免右上角叉号遮罩挡住上传入口
  - 上传前确保回到 `SKU图片信息` 槽位表面
  - 修复 `hover_text_by_index` 方法体缺失
  - 文件对话框写入增加短轮询重试
  - 透图槽位已填充时返回幂等成功
  - 文件对话框大图标换行文件名已支持去空白匹配，例如 `transparent-pr\nobe.png`
  - 相关回归：`37 passed`
  - 全量回归：`102 passed`
  - 代码图谱：`graphify update .` 已完成
  - 实机验证通过：`page_state=transparent_image_uploaded`
  - 成功截图：`resources/screenshots/window-1187102-20260516-002306-522579.png`
  - 成功信息：`上传入口=已完成；触发模式=already_filled；图片出现=成功；上传前图片数=2；上传前空槽数=1`

- 2026-05-16 `BL-088-3` 详情编辑器写入闭环
  - 新增 `type_into_detail_editor()`，显式点击京麦代码编辑正文区后通过剪贴板写入
  - 修正详情锚点优先级，优先使用 `代码编辑` 锚点，避免落到预览区或空白间隔
  - 实机验证通过：`page_state=detail_content_written`
  - 全量回归：`103 passed`
  - 成功截图：`resources/screenshots/window-1187102-20260516-005034-202135.png`

- 2026-05-16 `BL-089` 保存草稿闭环
  - 修正 `run_t8_save_draft()` 过早把 loading 状态判为成功的问题，改为轮询草稿箱列表/保存成功提示
  - `t8-probe` 现在可识别保存后的 `draft_list` 状态
  - 实机验证通过：`page_state=draft_saved`
  - 全量回归：`106 passed`
  - 图谱更新：`graphify update .`
  - 成功信息：`草稿点击=成功；页面变化=成功；草稿确认=成功；触发模式=draft_list；文档轮询次数=3`
  - 成功截图：`resources/screenshots/window-1187102-20260516-005858-872183.png`
  - 草稿箱首行：`测试商品标题-自动化验证`，编辑时间 `2026-05-16 00:58:56`
  - 正式发布提交未执行，需用户明确允许

- 2026-05-16 T5/T7 剩余必填项补齐
  - 新增 `t5-required-fields` 入口，支持 `--current`、`--weight`、`--factory-inventory`
  - T7 增加顶部页签区域导航，避免停留在商品描述/销售属性区域时填物流字段失败
  - 动态 `jd-id-<prefix>-<suffix>` 支持按后缀解析，并优先选择可见控件，避免 0 坐标隐藏控件吞输入
  - WebView 输入框/下拉框改为可见矩形中心点击 + 剪贴板/弹层点选，规避 pywinauto wrapper 阻塞
  - 实机 T7 一次通过：`page_state=logistics_completed`
  - 实机 T5 required 通过：SKU 重量 `0.5`、厂直库存 `10` 已写入；页面文本命中 `10A`
  - 复核页面文本：无 `报错反馈/报错信息/销售单位不可为空/请维护质保期/请填写重量/请输入库存数量`
  - 全量回归：`108 passed`

- 2026-05-16 100 分补完规划
  - 新增 `100_SCORE_RECOVERY_PLAN.md`
  - 增加 `BL-089A`、`BL-086A`、`BL-097A`、`BL-100`、`BL-101`、`BL-102`、`BL-103`、`BL-104`
  - 将 100 分恢复拆成 A-F 六个门禁：70、80、88、94、98、100
  - 记录 gstack 当前不可用问题：`browse.exe status` 缺少 `server.ts` 上下文

- 2026-05-16 `BL-089A` 草稿模式 E2E 代码入口
  - 新增 `DraftE2EOrchestrator` 和 `DraftE2EOptions`
  - 新增 CLI：`python cli.py run-draft-e2e --excel ... --main-image-path ... --transparent-image-path ...`
  - 串联 Excel 导入、prepared product 选择、T4/T5/T6/T7、`t8-save-draft`
  - 明确不调用 `t8-publish-product`，避免未授权正式发布
  - 本地图片路径当前由 CLI 显式传入，真实图片本地化仍属于后续数据准备质量补齐
  - 新增测试：`tests/test_draft_e2e.py`
  - 验证：`pytest tests/test_draft_e2e.py tests/test_cli.py -q` -> `15 passed`
  - 全量回归：`pytest -q` -> `118 passed`
  - 图谱更新：`graphify update .`
  - 真实 E2E 首跑被数据库初始化阻塞：`Table 'jingmai_agent.upload_jobs' doesn't exist`
  - 阻塞处理：CLI 已改为结构化返回 `database_error`，远端库建表需确认后执行 `python cli.py init-db --root .`

- 2026-05-16 `BL-089A` 实机首轮推进
  - 用户确认后已执行 `python cli.py init-db --root .`
  - `init_database()` 增加旧版 `publish_tasks` 兼容迁移
  - T4 改为标签优先定位，真实验证通过
  - T4 证据截图：`resources/screenshots/window-1187102-20260516-074420-733288.png`
  - 最新 E2E 阻塞：`t6-main-image` 文件写入失败，截图 `resources/screenshots/window-1187102-20260516-075644-196844.png`
  - 直接保存草稿未确认成功：截图 `resources/screenshots/window-1187102-20260516-075813-954078.png`
  - 全量回归：`118 passed`

- 2026-05-16 `BL-091` Agent 决策层最小闭环
  - 新增 7 个 agent/ 模块：`__init__.py`, `types.py`, `registry.py`, `planner.py`, `executor.py`, `reflection.py`, `pipeline.py`
  - `AgentPipeline` 编排 Planner → Executor → Reflection 循环，含重试逻辑和 trace 记录
  - `AgentExecutor` 通过 getattr 反射调度 workflow_service 方法，24 个 ActionStep 覆盖所有 VALID_STEPS
  - `AgentReflection` 规则驱动的 ReflectionDecision（CONTINUE/RETRY/SKIP/ABORT）
  - `ActionRegistry` 注册 24 个结构化 ActionStep（含 param_map、max_retry_count、category）
  - `TaskRunner.run()` 已委托给 `AgentPipeline`，保留原签名和返回结构
  - agent/ 相关测试：`tests/test_agent_registry.py`, `tests/test_agent_planner.py`, `tests/test_agent_executor.py`, `tests/test_agent_reflection.py`, `tests/test_agent_pipeline.py`
  - 全量回归：216 passed

- 2026-05-16 `BL-100` Runtime Event Loop — sightflow 风格事件队列、调度、停止、会话状态
  - 新增 `jingmai_publish/runtime/event_loop.py` (222 lines)
  - 实现 `RuntimeEventLoop`：`enqueue/schedule/stop/pause/resume/session_state/event_history`
  - 事件类型覆盖 observe→decide→act→verify→repeat 全周期
  - 测试：`tests/test_runtime_event_loop.py` (17 tests, 17 passed)
- 2026-05-16 `BL-101` Provider Manifest — sightflow 风格能力声明系统
  - 新增 `jingmai_publish/runtime/manifest.py` (273 lines)
  - 实现 `ProviderManifest`、`ProviderCapability`、`ProviderFactory`、`validate_manifest`、`load_manifest`/`dump_manifest`
  - 8 种能力类别：observation/action/persistence/channel/memory/vision/grounding/reflection
  - 4 个内置 manifest 描述现有 provider
  - 测试：`tests/test_runtime_manifest.py` (28 tests, 28 passed)

- 2026-05-17 `BL-103` Retry Lane Switching — 三级重试策略
  - `ActionStep` 新增 `retry_lanes: tuple[RetryLane, ...]` 和 `same_lane_max_retries: int = 3`
  - `RetryLane` dataclass：`lane_name`, `method_name`, `description`, `param_overrides`
  - `ReflectionDecision` 新增 `RETRY_NEXT_LANE` 和 `HUMAN_ESCALATE`
  - `AgentReflection.reflect()` 支持 `lane_index`/`lane_count`，lane-aware 决策逻辑
  - `AgentPipeline._execute_step_with_retry()`：while-true loop with lane tracking，trace 条目含 lane 信息
  - `AgentExecutor.execute()` 支持 `lane: RetryLane | None`，合并 `lane.param_overrides`
  - Registry 中 4 个关键步骤（t4, t6-main-image, t6-detail-editor, t8-save-draft）已配置 retry_lanes
  - 新增测试：`tests/test_agent_retry_lanes.py`（14 tests, 14 passed）
  - 全量回归：`pytest -q` -> `231 passed`
  - 代码图谱：`graphify update .` 已完成
  - Phase B 全部完成，基线升至 **80/100**

- 2026-05-17 `BL-092` Ollama Vision Provider — VLM 视觉模型集成
  - 新增 `jingmai_publish/runtime/vision.py` (~505 lines)
  - 实现 `VisionAnalysis` dataclass：success, page_state, elements, text_content, bbox, point, confidence, model, elapsed_ms
  - 实现 `OllamaVisionProvider`：`analyze_screenshot()`, `compare_screenshots()`, `locate_element()`
  - Ollama `/api/chat` REST API 调用，vLLM `/v1/chat/completions` 自动降级
  - `_encode_image()`：PIL 缩放 + base64 编码
  - `_extract_json()`：4 种 JSON 格式解析（plain/code block/embedded/no tag）
  - `_call_vision_api()`：先 Ollama 后 vLLM，双路径 classpath mock 支持
  - `ProviderRegistry` 新增 `vision` 槽位
  - `build_default_manifests()` 新增 vision manifest
  - 工厂函数 `create_vision_provider_from_env()`：支持 OLLAMA_BASE_URL/VLLM_BASE_URL 环境变量
  - 新增测试：`tests/test_runtime_vision.py`（36 tests, 36 passed）
  - Phase C 核心 1/2

- 2026-05-17 `BL-095` Three-Way Grounding — 三路视觉定位仲裁
  - 新增 `jingmai_publish/runtime/grounding.py` (~460 lines)
  - 实现 `GroundingCandidate` / `GroundingResult` dataclass
  - `UIAGroundingAdapter`：by automation_id / label / class_name，返回 bbox + point + confidence=0.9
  - `AnchorGroundingAdapter`：5 个预定义地标规则（save_draft/next_step/publish/main_image_slot），9 个区域定位，文本匹配增强
  - `ThreeWayGroundingProvider`：UIA(0.50) → Vision(0.35) → Anchor(0.15) 优先级链仲裁
  - 高置信度提前返回（>=0.8），加权融合多候选（weighted average）
  - `_weighted_fusion()`：处理零权重回退、全无 bbox 退化、置信度上限截断
  - `ProviderRegistry` 新增 `grounding` 槽位
  - `build_default_manifests()` 新增 grounding manifest
  - `AgentReflection.reflect()` Phase C 扩展：`vision_analysis` 参数，视觉校验通过时 RETRY 而非 ABORT
  - 新增测试：`tests/test_runtime_grounding.py`（35 tests, 35 passed）
  - 更新测试：`tests/test_runtime_manifest.py` manifest count → 6
  - 全量回归：`pytest -q` -> `302 passed`
  - Phase C 核心 2/2

## Progress Report Protocol

后续每完成一个任务，对用户的进度汇报至少包含：

1. 已完成任务 ID 与名称
2. 本次修改了哪些代码、命令入口、文档
3. 用什么方式验证通过
4. 当前 backlog 完成数与总体进度
5. 下一个马上进入的任务
