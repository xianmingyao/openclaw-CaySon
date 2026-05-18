# Task Plan: 京麦桌面商品上架系统补完

## Latest Update - 2026-05-17

Phase B 全部完成：BL-091 AgentPipeline、BL-100 RuntimeEventLoop、BL-101 ProviderManifest、BL-103 Retry Lane Switching 均已落地。

- `BL-091`: Agent 决策层最小闭环完成，7 个 agent/ 模块落地，AgentPipeline 接入 TaskRunner.run()
- `BL-100`: RuntimeEventLoop 完成（222 行），enqueue/schedule/stop/pause/resume/session_state/event_history
- `BL-101`: ProviderManifest 完成（273 行），8 种能力类别，4 个内置 manifest
- `BL-103`: Retry Lane Switching 三级重试策略完成，14 个测试用例，4 个关键步骤配置 lanes
- 全量回归: `pytest -q` -> `231 passed`
- 当前基线: **80/100** (Phase A 证据 + Phase B 完整)
- 下一门禁: **88/100** (Phase C: Ollama vision provider + 三路 grounding)

## Goal

把当前 `55/100` 的京麦桌面商品上架系统补齐到可交付生产闭环：真实完成一次商品上架，并具备 Agent 决策、视觉校验、失败反思、持久化运维和可复现验收证据。

## Current Phase

Phase 3: Reflection 与视觉校验真实化 (BL-103 收尾 Phase B → Phase C)

## Score Baseline

当前客观基线：`80 / 100`（Phase A 证据 + Phase B 完整）

评分口径以用户提供的代码开发评分分析为准，不再沿用 `IMPLEMENTATION_PROGRESS.md` 的 `92/100` 自评，也不沿用旧 `.planning` 中的 `95/100` 乐观状态。

## 100 分恢复计划

详细门禁见 `100_SCORE_RECOVERY_PLAN.md`。后续所有提分必须按以下路径推进：

| 阶段 | 目标分 | 状态 | 退出证据 |
|---|---:|---|---|
| Phase A | 70 | complete | Excel 单行到京麦草稿箱 E2E，T1-T8 关键步骤截图/日志证据 |
| Phase B | 80 | complete | AgentPipeline/BL-100/BL-101/BL-103 全部完成 |
| Phase C | 88 | pending | Ollama vision provider、截图 diff、DOM/Vision/Anchor 三路仲裁 |
| Phase D | 94 | pending | 京东抓取样本集、字段补全、飞书实时入口、业务预校验 |
| Phase E | 98 | pending | Redis、Milvus、日志截图清理、多 Agent 角色拆分 |
| Phase F | 100 | pending | 20 次草稿回归、正式发布 UAT、部署文档、评分复核 |

### 当前执行顺序

1. ~~完成 `Phase A`~~：P0 草稿闭环证据包已完成，`BL-089A` E2E 通过。
2. ~~进入 `Phase B`~~：AgentPipeline、RuntimeEventLoop、ProviderManifest 核心架构已落地。
3. ~~完成 `BL-103`~~：Retry Lane Switching 三级重试策略已完成（231 passed）。
4. 进入 `Phase C`：Reflection 视觉化，Ollama vision provider + 三路 grounding（**进行中**）。
5. 进入 `Phase D/E`：数据质量、飞书、Redis、Milvus、运维治理。
6. 进入 `Phase F`：稳定性回归和正式评分。

## Phases

### Phase 0: 计划重建与管理基线重置

- [x] 读取现有 `.planning` 项目管理文件
- [x] 读取 graphify 项目图谱报告
- [x] 记录评分分析中的 P0/P1/P2 缺口
- [x] 生成 `task_plan.md`、`findings.md`、`progress.md`
- [x] 同步 `.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/BACKLOG.md`、`.planning/STATE.md`
- **Status:** complete

### Phase 1: P0 业务闭环补齐

- [x] `BL-088-1` 主图上传真实闭环：上传后必须能从页面状态、截图或控件状态确认槽位已变更
  - [x] 代码层：上传后等待槽位异步刷新
  - [x] 代码层：图片空间选图增加缩略图候选回退
  - [x] 代码层：修正大图缩略图被空槽快照覆盖的问题
  - [x] 代码层：按截图改为悬停槽位后点击浮层 `本地上传`
  - [x] 代码层：按截图改为文件对话框优先地址栏输入图片目录再选中文件
  - [x] 实机层：真实京麦页面 before/after 截图和日志证据
- [x] `BL-088-2` 透明图上传：从本地文件到京麦必填透图槽位完成真实上传
  - [x] 代码层：上传前自动回到 `SKU图片信息` 槽位表面，避免停在 `SKU基本信息` 子页签
  - [x] 代码层：修复 `hover_text_by_index` 方法体缺失，恢复文本悬停回退能力
  - [x] 代码层：文件对话框增加短轮询重试，避免刚触发对话框就判定失败
  - [x] 代码层：关闭图片预览遮罩，处理用户指出的右上角叉号取消场景
  - [x] 代码层：目标透图槽位已填充时返回幂等成功，不强行重复替换
  - [x] 实机层：透明图已回填到 `*透图` 槽位，命令入口返回 `transparent_image_uploaded`
- [x] `BL-088-3` 详情编辑器写入：攻克资源选择弹层和真实编辑区定位，支持图文详情写入
  - [x] 代码层：新增 `type_into_detail_editor()`，优先点击代码编辑正文区域并通过剪贴板写入
  - [x] 代码层：详情编辑器验证从真实 document text 中确认探针内容出现
  - [x] 实机层：`t6-detail-editor` 返回 `detail_content_written`
- [ ] `BL-089` 保存草稿 / 发布提交：完成真实保存草稿、发布商品、继续发布、审核态确认
  - [x] 代码层：`run_t8_save_draft()` 点击后轮询最终态，只有草稿箱列表或保存成功提示才算 `draft_saved`
  - [x] 代码层：`t8-probe` 可识别保存后的草稿箱列表态，避免把缺少底部保存按钮误判为失败
  - [x] 测试层：覆盖延迟进入草稿箱、加载态不能误判成功、草稿箱列表探针
  - [x] 实机层：`t8-save-draft` 返回 `draft_saved`，京麦草稿箱出现 `测试商品标题-自动化验证`
  - [ ] 实机层：正式发布商品 / 继续发布 / 审核态确认仍需明确许可后执行
- [x] T5/T7 剩余必填项补齐：清除发布前 `销售属性`、`销售单位`、`质保期` 报错
  - [x] 代码层：`t5-required-fields` 支持动态 `current`、`weight` 和可选 `factory_inventory`
  - [x] 代码层：T7 进入顶部 `商品售后及其他/商品物流` 页签后再填物流字段
  - [x] 代码层：动态 automation id 按后缀解析，并优先选择可见控件，避免命中 0 坐标隐藏候选
  - [x] 代码层：WebView 输入/下拉改为可见矩形中心点击 + 剪贴板/弹层点选，避免 wrapper 阻塞
  - [x] 测试层：T5 动态 id、T7 页签导航/销售单位兜底/质保期映射已覆盖
  - [x] 实机层：销售单位、商品包装、特殊发货时效标记、包装清单、保质期、质保期校验成功
  - [x] 实机层：SKU 重量、厂直库存已写入并清除对应报错
  - [x] 实机层：复核页面已无 `报错反馈/报错信息/销售单位不可为空/请维护质保期/请填写重量/请输入库存数量`
- [ ] 为 T6/T8 增加实机验收命令、日志证据和截图证据
- [ ] `BL-089A` 草稿模式 E2E：从 Excel 单行导入到京麦草稿箱出现商品
  - [x] 代码层：新增 `run-draft-e2e` CLI，把 Excel 导入、数据准备、T4/T5/T6/T7/T8 保存草稿串成单一入口
  - [x] 代码层：草稿 E2E 强制只走 `t8-save-draft`，不调用正式发布动作
  - [x] 测试层：覆盖成功链路、失败即停止、尺寸字段缺失降级、本地图片路径校验和 CLI 参数传递
  - [x] 环境层：当前配置库已执行 `python cli.py init-db --root .`，并补旧版 `publish_tasks` 兼容迁移
  - [x] 实机层：Excel 单行已导入，T3 类目确认和 T4 基础信息填写通过
  - [ ] 实机层：当前阻塞在 `t6-main-image`，主图上传入口 `text_fallback` 文件写入失败
  - [ ] 实机层：直接 `t8-save-draft` 已点击但未确认进入草稿箱，页面仍有 17 条报错
  - [ ] 实机层：使用真实京麦窗口跑 Excel 单行到草稿箱，并归档命令、日志、截图、页面文本
- [ ] `BL-086A` T1-T8 关键动作 before/after 截图证据包
- [ ] `BL-097A` P0 UAT 证据包：命令、日志、截图、页面文本、测试结果
- **Status:** in_progress

### Phase 2: Agent 决策层与运行时主循环

- [x] `BL-091` Agent 决策层最小闭环：AgentPipeline 已接入 TaskRunner.run()，7 个 agent/ 模块落地
  - [x] `agent/types.py` — ActionStep / Plan / ReflectionDecision 数据类
  - [x] `agent/registry.py` — 24 个 ActionStep 注册，覆盖所有 VALID_STEPS
  - [x] `agent/planner.py` — AgentPlanner，拓扑排序生成 Plan
  - [x] `agent/executor.py` — AgentExecutor，getattr 反射调度 + 24 个 handler
  - [x] `agent/reflection.py` — AgentReflection，规则驱动 ReflectionDecision
  - [x] `agent/pipeline.py` — AgentPipeline，Planner → Executor → Reflection 循环 + 重试 + 溯源
  - [x] `agent/__init__.py` — 公开 API 导出
- [x] `BL-100` Runtime Event Loop：实现 queue / schedule / stop / pause / resume / session state / event history
  - [x] `jingmai_publish/runtime/event_loop.py` (222 lines)
  - [x] 事件类型覆盖 observe→decide→act→verify→repeat 全周期
  - [x] 测试：`test_runtime_event_loop.py` (17 tests, 17 passed)
- [x] `BL-101` Provider Manifest：实现 manifest schema、provider 加载器和示例 provider
  - [x] `jingmai_publish/runtime/manifest.py` (273 lines)
  - [x] 8 种能力类别：observation/action/persistence/channel/memory/vision/grounding/reflection
  - [x] 4 个内置 manifest 描述现有 provider
  - [x] 测试：`test_runtime_manifest.py` (28 tests, 28 passed)
- [x] 建立 `Planner -> Executor -> Reflection` 三层职责
- [x] 将当前 `for step in plan: execute(retry)` 改造成 `observe -> decide -> act -> verify -> repeat`（HostRuntime.kernel.py）
- [x] 定义 `Observation`、`ActionPlan`、`VerificationResult`、`ReflectionCase` 等核心数据结构
- [x] 让 `TaskRunner` 调用决策层，而不是只顺序执行预定义步骤
- [x] Provider 抽象升级为可声明能力、依赖、输入输出和运行边界的 manifest 风格
- [ ] `BL-103` Retry Lane Switching：同 lane、替代 operator、转人工三段策略
- **Status:** in_progress（BL-103 待做）

### Phase 3: Reflection 与视觉校验真实化

- [ ] 接入本地视觉模型通道，优先支持 Ollama vision provider
- [ ] 实现 before/after 截图对比校验，不再只检查 `document_text`
- [ ] 建立 DOM / Vision / Anchor 三路 grounding 候选分析
- [ ] 重试策略升级：第 1 次同 lane 重试，第 2 次切换 lane/operator，第 3 次进入反思与降级方案
- [ ] 将失败签名、截图路径、原因、修复策略写入长期记忆入口
- [ ] `BL-102` 审计表：补齐 `ui_artifact`、`action_event`、`reflection_case`
- **Status:** pending

### Phase 4: 数据入口与商品准备质量验证

- [ ] 验证 `JDProductFetchService` 抓取质量，覆盖品牌、型号、价格、图片、详情 HTML
- [ ] 增加抓取失败分类、重试和降级策略
- [ ] 增加字段补全规则：缺失字段推理、标题长度限制、品牌优先选择、类目字段映射
- [ ] 飞书入口从骨架推进到可驱动真实任务
- [ ] 增加 JD 抓取与标准化输出的回归样本集
- [ ] `BL-104` 业务预校验：标题、价格、主图、透图、详情、物流售后阻断式校验
- **Status:** pending

### Phase 5: 持久化、运维与多 Agent 协作

- [ ] 实现日志和截图 3 天自动清理硬规则
- [ ] 接入 Redis Streams / 状态 / 锁，支撑任务并发与运行态恢复
- [ ] 接入 Milvus 长期向量记忆，保存失败反思与控件定位经验
- [ ] 新增 `field_binding`、`reflection_case` 等研究文档要求的表
- [ ] 拆分六类 Agent：Planner / Grounding / Executor / Reflection / Memory / Task API
- **Status:** pending

### Phase 6: 端到端 UAT 与交付评分回升

- [ ] 构建真实端到端 UAT：Excel -> MySQL -> JD 补全 -> 图片本地化 -> 京麦保存草稿/发布
- [ ] 每个 P0 闭环必须有代码、测试、截图、日志和文档证据
- [ ] 更新 `IMPLEMENTATION_PROGRESS.md`，删除虚高评分，改为证据驱动评分
- [ ] 形成生产部署与运维说明
- [ ] 重新评分，只有 P0 全部闭环后才能上调到 `70+`
- **Status:** pending

## Priority Gates

| Gate | 进入条件 | 退出条件 |
|------|----------|----------|
| G0 管理基线 | 当前计划文件落盘 | `.planning` 全部改为 55 分事实源 |
| G1 可用闭环 | T6/T8 仍不可真实产出 | 主图、透图、详情、草稿/发布均有实机证据 |
| G2 智能闭环 | 只有顺序步骤执行 | 建立 observe/decide/act/verify/repeat |
| G3 视觉可信 | 只有文本校验 | 截图差异、视觉模型、lane 切换重试可运行 |
| G4 生产可管 | 只有 ORM 和本地日志 | Redis/Milvus/清理/多 Agent/UAT 完成 |

## Key Questions

1. 当前京麦页面的主图上传失败，是槽位定位错误、文件对话框写入失败、图片管理弹层确认失败，还是上传后验证逻辑错误？
2. 详情编辑器真实可编辑区域属于 DOM、嵌入 WebView、富文本 iframe，还是原生 UIA 控件？
3. Ollama 视觉模型是否已经在本机可用？如果不可用，第一版应如何做可替换 provider？
4. Redis / Milvus 是本机开发实例，还是需要对接已有服务器？
5. 多 Agent 是先做进程内角色拆分，还是直接做独立 worker / queue 架构？

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| 以 `55/100` 作为新基线 | 用户评分指出旧自评严重虚高，且 P0 闭环未完成 |
| 先补 P0 真实业务闭环，再扩展 P1/P2 | 没有主图、透图、详情、提交闭环，系统无法产生最终业务结果 |
| Agent 主循环必须成为架构主线 | 当前顺序执行无法对齐 UI-TARS / SightFlow 核心设计 |
| Reflection 必须从文本检查升级到视觉校验 | 京麦桌面 UI 的关键状态需要截图和控件状态共同验证 |
| `.planning` 与 planning-with-files 双轨使用 | `task_plan/findings/progress` 管理当前工作记忆，`.planning` 管理项目级 backlog 和状态 |

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| 旧 `.planning` 状态与新评估冲突 | 1 | 将项目管理基线重置为 `55/100`，重新拆分 P0/P1/P2 |

## Notes

- 未完成真实京麦页面闭环的任务，不得标记为 `DONE`。
- 探针成功只能算发现或定位能力，不能算业务闭环完成。
- 每完成一个阶段，必须同步更新 `task_plan.md`、`progress.md`、`.planning/STATE.md` 和 `.planning/BACKLOG.md`。
