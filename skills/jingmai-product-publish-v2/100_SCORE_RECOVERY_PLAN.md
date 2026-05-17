# 京麦上架系统 100 分补完计划

## 目标

基于当前 `55/100` 评分，按证据门禁逐步补齐缺陷和未完成功能，最终达到“平稳 100 分”：不是文档自评 100，而是代码、测试、截图、日志、实机 UAT、运维说明全部闭环后再复核到 100。

## 评分拆分

| 维度 | 分值 | 100 分要求 |
|---|---:|---|
| 京麦业务端到端闭环 | 25 | Excel 输入到京麦保存草稿/发布全流程可复现，所有必填规则有校验和证据 |
| SightFlow/UI-TARS 架构对齐 | 20 | Host runtime、provider manifest、事件队列、Agent/Operator/Loop 分层落地 |
| Reflection 与视觉校验 | 20 | before/after 截图差异、控件状态、Ollama/Vision provider、三路 grounding、失败反思闭环 |
| 数据入口与商品准备 | 15 | 京东抓取样本集、字段补全、图片本地化、飞书入口、业务预校验质量可量化 |
| 持久化与运维 | 10 | Redis 锁/事件流、Milvus 记忆、日志截图清理、幂等和恢复能力 |
| 测试、UAT、文档 | 10 | 单元/集成/实机/UAT/部署文档齐全，评分复核有证据 |

## 分数恢复路线

| 阶段 | 目标分 | 关键交付 |
|---|---:|---|
| Phase A | 70 | ✅ 完成 | P0 真实业务闭环收口：T6/T8/T5/T7 证据归档，草稿全链路稳定 |
| Phase B | 80 | ✅ 完成 | 运行时重构全部完成：AgentPipeline, RuntimeEventLoop, ProviderManifest, Retry Lane Switching |
| Phase C | 88 | ⏳ 核心完成 | Reflection 真实化：BL-092 ✅ / BL-095 ✅；BL-086B/BL-094A 待补齐 |
| Phase D | 94 | 数据与入口质量：京东抓取样本集、字段补全规则、飞书实时入口、业务预校验 |
| Phase E | 98 | 生产运行能力：Redis、Milvus、日志截图清理、多 Agent 角色拆分 |
| Phase F | 100 | 稳定性验收：20 次草稿回归、正式发布 UAT、部署文档、独立评分复核 |

## 缺陷到任务映射

| 缺陷 ID | 当前缺陷 | 修复任务 | 完成证据 |
|---|---|---|---|
| D-001 | 没有 SightFlow 风格持续 runtime 队列 | `BL-100 Runtime Event Loop` | 队列、schedule、stop、event log 测试通过 |
| D-002 | Provider 只有 Python 协议，无 manifest/bundle 契约 | `BL-101 Provider Manifest` | provider manifest schema、加载器、示例 provider |
| D-003 | 没有 VLM/视觉坐标解析 | `BL-092 Ollama Vision Provider` | ✅ bbox/point 输出、截图输入、失败降级测试（36 cases） |
| D-003B | 没有多路定位仲裁 | `BL-095 Three-Way Grounding` | ✅ UIA/Vision/Anchor 优先级链 + 加权融合（35 cases） |
| D-004 | 缺少 `ui_artifact/action_event/reflection_case` 审计 | `BL-102 Audit Tables` | 表模型、Repository、写入点、查询测试 |
| D-005 | 重试只是重复同一步，没有 lane/operator 切换 | `BL-103 Retry Lane Switching` | 第 1/2/3 次失败策略测试和日志 |
| D-006 | 业务预校验不足 | `BL-104 Business Preflight` | 标题、价格、主图、透图、详情、物流校验报告 |
| D-007 | 飞书不是实时入口 | `BL-090 Feishu Realtime` | 消息触发、状态卡片、截图回传、abort/retry |
| D-008 | 京东抓取质量未量化 | `BL-082/BL-083 Data Quality` | 样本集、准确率、失败分类、补全规则 |
| D-009 | Redis/Milvus/清理未生产化 | `BL-085/093/094 Ops` | TTL、锁、Streams、记忆检索、清理任务 |
| D-010 | 缺少端到端稳定性证据 | `BL-097/099 UAT & Score Audit` | UAT 报告、截图包、重新评分 |

## Phase A: 55 -> 70 — ✅ 已完成

目标：把当前已经突破的 T6/T8/T5/T7 证据系统化，形成”真实草稿闭环”。

已完成任务：
- [x] `BL-089A`：草稿模式 E2E：从 Excel 单行导入到京麦草稿箱出现商品。`job_id=job-d217feeee80a`
- [x] `BL-086A`：关键动作 before/after 截图归档（T1/T2/T4/T5/T6/T7/T8 均有证据）
- [x] `BL-097A`：P0 UAT 证据包基本完善（命令、日志、截图、页面文本、测试结果）

门禁达成：
- `pytest -q` 全通过（216 passed）
- 至少 1 条 Excel 样例完成草稿闭环 ✅
- 每个关键步骤有截图或日志证据 ✅
- `STATE.md` 分数已提升到 `70+/100`

## Phase B: 70 -> 80 — ✅ 已完成 (80/100)

目标：从顺序脚本升级为可持续 runtime。

已完成任务：
- [x] `BL-100`：runtime event queue 完成（222 lines），`enqueue/schedule/stop/pause/resume/session_state/event_history`
- [x] `BL-101`：provider manifest schema 完成（273 lines），8 种能力类别，4 个内置 manifest
- [x] `BL-091`：AgentPipeline 完成，Planner→Executor→Reflection 最小闭环，7 个 agent/ 模块落地，TaskRunner 已委托 AgentPipeline
- [x] `BL-103`：Retry Lane Switching 三级重试策略完成，14 个测试用例，4 个关键步骤配置 lanes

退出标准：
- [x] `TaskRunner` 不再直接只执行静态步骤，而是通过 observe/decide/act/verify 推进 ✅
- [x] `BL-103` 失败三级日志能解释每次策略变化（同 lane 重试 → lane 切换 → 人工升级）
- [x] 分数允许提升到 `80/100`

## Phase C: 80 -> 88

目标：让 Reflection 从文本判断升级为视觉可信判断。

任务：
- [x] `BL-092`：Ollama vision provider (~505L)，输入截图，输出页面状态、控件候选、bbox/point。36 tests。
- [x] `BL-095`：DOM/UIA、Vision、Anchor 三路 grounding 仲裁 (~460L)。35 tests。
- [ ] `BL-086B`：before/after 截图 diff，结合控件文本和截图变化判断动作是否成功。
- [ ] `BL-094A`：失败反思写入 JSONL 和 Milvus 兼容接口。

退出标准：
- 图片上传、详情写入、草稿保存至少各有一次视觉校验成功记录。
- 视觉不可用时能降级到 UIA/Anchor，不阻塞主流程。
- 分数允许提升到 `88/100`。

## Phase D: 88 -> 94

目标：补齐数据质量和飞书入口。

任务：
- `BL-082`：建立京东商品抓取样本集，统计标题、品牌、型号、价格、图片、详情抓取准确率。
- `BL-083`：字段补全规则和业务预校验，生成阻断式错误报告。
- `BL-090`：飞书实时入口，支持任务创建、查询、abort/retry、截图回传。
- `BL-104`：完整业务预检：标题、价格关系、图片数量/格式、详情图、物流售后。

退出标准：
- 无效数据不会进入京麦页面脏写。
- 飞书可触发一条草稿任务并返回状态。
- 分数允许提升到 `94/100`。

## Phase E: 94 -> 98

目标：生产运行治理。

任务：
- `BL-093`：Redis 状态、锁、事件流，防止重复任务和并发串线。
- `BL-094`：Milvus 长期记忆，失败签名和修复策略可检索。
- `BL-085`：日志和截图 3 天自动清理，清理任务可自动/手动触发。
- `BL-096`：Planner / Grounding / Executor / Reflection / Memory / Task API 角色拆分。

退出标准：
- 重复提交同一 Excel 行不会重复上架。
- 失败案例可检索并影响下一轮策略。
- 运维清理和恢复有命令入口。
- 分数允许提升到 `98/100`。

## Phase F: 98 -> 100

目标：稳定性和交付复核。

任务：
- `BL-097`：20 次草稿模式回归，成功率不低于 95%。
- `BL-097P`：正式发布 UAT，仅在用户明确许可和白名单商品下执行。
- `BL-098`：生产部署文档，包含环境、账号、凭据、执行机、回滚、人工接管。
- `BL-099`：重新评分报告，按本文件评分拆分逐项给证据。

退出标准：
- 回归报告和截图证据齐全。
- 正式发布路径有人工审批和可追溯记录。
- 评分复核达到 `100/100`，且没有“待验证”冒充“完成”。

## Evidence Correction - 2026-05-17

The Phase A section above is stale where it marks `BL-086A` as complete. Current verification shows:

- Runtime records reference P0 screenshots.
- The actual `resources/screenshots/window-*.png` files are missing from the current working tree.
- `BL-086A` must be treated as `IN_PROGRESS`, not complete.
- Current conservative delivery score remains `90/100` until screenshot evidence is restored or recaptured.
- Authoritative evidence index: `.planning/BL-086A_SCREENSHOT_EVIDENCE.md`.

## gstack 使用说明

本轮已尝试调用本机 gstack browse 二进制，但当前安装缺少可解析的 `server.ts` 运行上下文，`browse.exe status` 失败。后续如果需要用 gstack 做 Web/可视化 QA，需要先修复 gstack 安装或设置 `BROWSE_SERVER_SCRIPT`。

在 gstack 可用后，优先用于：
- 验证本地/HTML 报告页面。
- 打开截图证据索引页并做可视化检查。
- 对未来 Web 控制台或飞书模拟页面做端到端 QA。

## 规划维护规则

- `task_plan.md` 记录当前执行阶段。
- `findings.md` 记录技术发现、工具问题和决策。
- `progress.md` 记录每次执行、测试、实机证据。
- `.planning/ROADMAP.md` 管理阶段门禁。
- `.planning/BACKLOG.md` 管理任务 ID 和状态。
- `.planning/STATE.md` 只记录当前真实状态，不允许提前提分。
