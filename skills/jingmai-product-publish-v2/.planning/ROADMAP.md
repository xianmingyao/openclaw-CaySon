# Roadmap: 京麦桌面商品上架系统补完计划

## Current Sync - 2026-05-17

The previous 55/100 baseline in this document is stale. The current conservative delivery baseline is `90/100`: Phase B and Phase C core architecture are implemented, audit tables are implemented, and DX/security P0 hardening has been added. The score is not raised further until BL-086A screenshot evidence is physically present or recaptured.

Authoritative current evidence index: `.planning/BL-086A_SCREENSHOT_EVIDENCE.md`.

Immediate gate:
- `BL-086A`: `IN_PROGRESS`
- Evidence problem: runtime logs reference screenshots, but the referenced PNG files are missing from `resources/screenshots/` and `logs/screenshots/`.
- Next action: restore or recapture P0 screenshots, then re-evaluate the 92+ score gate.

## Overview

当前项目基线为 `55/100`。后续路线不再按旧的 `95/100` 乐观状态推进，而是围绕“真实完成一次京麦商品上架”反推架构和工程缺口。

## Phases

- [x] **Phase 0: 管理基线重置**
- [ ] **Phase 1: P0 业务闭环补齐**
- [x] **Phase 2: Agent 决策层与运行时主循环**
- [x] **Phase 3: Reflection 与视觉校验真实化**  *(核心完成：BL-092/BL-095)*
- [ ] **Phase 4: 数据入口与商品准备质量验证**
- [ ] **Phase 5: 持久化、运维与多 Agent 协作**
- [ ] **Phase 6: 端到端 UAT 与交付评分回升**

## Phase Details

### Phase 0: 管理基线重置

**Goal**: 把项目计划、backlog、状态从旧的乐观完成度切回 `55/100` 事实源。  
**Status**: Completed

Exit criteria:
- `task_plan.md`、`findings.md`、`progress.md` 已创建
- `.planning/PROJECT.md`、`.planning/ROADMAP.md`、`.planning/BACKLOG.md`、`.planning/STATE.md` 已同步

### Phase 1: P0 业务闭环补齐

**Goal**: 真实完成京麦 T6/T8 关键业务闭环，让系统能产出保存草稿或发布结果。  
**Status**: Pending

Scope:
- 主图上传真实闭环（DONE）
- 透明图上传真实闭环（DONE）
- 详情编辑器真实写入（DONE）
- 保存草稿（DONE）
- 发布提交（需用户明确许可后执行）
- P0 实机日志和截图证据

### Phase 2: Agent 决策层与运行时主循环

**Goal**: 从顺序步骤执行升级为 `observe -> decide -> act -> verify -> repeat`。  
**Status**: Completed

Scope:
- Planner / Executor / Reflection 分层
- ActionPlan / Observation / VerificationResult 数据结构
- Provider manifest 风格能力声明
- TaskRunner 接入决策层
- Retry Lane Switching 三级重试策略

### Phase 3: Reflection 与视觉校验真实化

**Goal**: 将当前文本检查和重试计数升级为可验证的视觉闭环。  
**Status**: In progress (核心完成：BL-092/BL-095)

Scope:
- before/after 截图差异 (待 BL-086B)
- 控件状态验证
- Ollama vision provider ✅ (BL-092, ~505L, 36 tests)
- DOM / Vision / Anchor 三路 grounding ✅ (BL-095, ~460L, 35 tests)
- lane/operator 切换重试 ✅ (BL-103)
- 失败反思写入记忆 (待 BL-094A)

### Phase 4: 数据入口与商品准备质量验证

**Goal**: 让京东抓取、字段补全、飞书入口从“可运行”变成“质量可验证”。  
**Status**: Pending

Scope:
- JD 抓取样本集
- 品牌/型号/价格/图片/详情准确率验证
- 缺失字段推理规则
- 飞书 payload 到真实任务

### Phase 5: 持久化、运维与多 Agent 协作

**Goal**: 补齐生产运行所需的状态、锁、长期记忆、清理和角色协作。  
**Status**: Pending

Scope:
- Redis Streams / 状态 / 锁
- Milvus 长期向量记忆
- 日志与截图 3 天自动清理
- `field_binding` / `reflection_case` 表
- Planner / Grounding / Executor / Reflection / Memory / Task API 六类 Agent

### Phase 6: 端到端 UAT 与交付评分回升

**Goal**: 用真实端到端证据重新评分，而不是自评。  
**Status**: Pending

Scope:
- Excel -> MySQL -> JD 补全 -> 图片本地化 -> 京麦 T1~T8
- 保存草稿或发布结果证据
- 全量回归测试
- 生产部署文档
- 评分复核

## Progress

| Phase | Status | Notes |
|-------|--------|-------|
| 0. 管理基线重置 | Completed | planning-with-files 与 `.planning` 已同步 |
| 1. P0 业务闭环补齐 | In progress | `BL-088-1` 主图、`BL-088-2` 透明图、`BL-088-3` 详情编辑器、`BL-089` 保存草稿已实机闭环；下一步为正式发布提交或转入 `BL-086` |
| 2. Agent 决策层与运行时主循环 | Completed | BL-091/BL-100/BL-101/BL-103 全部完成；231 passed |
| 3. Reflection 与视觉校验真实化 | In progress | BL-092/BL-095 已完成；BL-086B/BL-094A 待补齐 |
| 4. 数据入口与商品准备质量验证 | Pending | 抓取质量和飞书入口待验证 |
| 5. 持久化、运维与多 Agent 协作 | Pending | 生产运行能力不足 |
| 6. 端到端 UAT 与交付评分回升 | Pending | 最终验收阶段 |

## Score Recovery Path

| Score Band | Required Evidence |
|------------|-------------------|
| 55 -> 65 | P0 中至少主图、透明图、详情、草稿保存有两个以上真实闭环 |
| 65 -> 75 | T6/T8 全部真实闭环，具备截图和日志证据 |
| 75 -> 85 | Agent 主循环和视觉校验接入主流程 |
| 85 -> 92 | Redis/Milvus/运维治理/飞书入口/UAT 完成 |
| 92+ | 多 Agent 协作、生产部署和稳定性证据充分 |

## 100 Score Recovery Gates

详见项目根目录 `100_SCORE_RECOVERY_PLAN.md`。后续提分按以下门禁执行，不允许跳级。

| Gate | Score | Required Evidence | Status |
|---|---:|---|---|
| A | 70 | Excel 单行到京麦草稿箱 E2E；T1-T8 关键截图/日志证据包 | In progress |
| B | 80 | Runtime event queue；Provider manifest；`observe -> decide -> act -> verify` 主循环；Retry Lane Switching | Complete |
| C | 88 | Ollama vision provider；截图 diff；DOM/Vision/Anchor 三路 grounding | In progress (BL-092/BL-095 ✅; BL-086B/BL-094A 待补齐) |
| D | 94 | 京东抓取样本集；字段补全；飞书实时入口；业务预校验 | Pending |
| E | 98 | Redis 锁/事件流；Milvus 记忆；日志截图清理；多 Agent 角色拆分 | Pending |
| F | 100 | 20 次草稿回归；正式发布 UAT；部署文档；独立评分复核 | Pending |

## Current Next Milestones

1. `BL-086B`：before/after 截图 diff 视觉验证 — 接入 `OllamaVisionProvider.compare_screenshots()` 并产出行级证据。
2. `BL-094A`：失败反思持久化 — `AgentReflection` 写入 JSONL 和 Milvus 兼容接口。
3. `BL-086A`：T1-T8 关键动作 before/after 截图证据包（已有截图，需分类归档）。
4. `BL-102`：补齐 `ui_artifact`、`action_event`、`reflection_case` 审计表。
5. `BL-097A`：P0 UAT 证据包，支撑 88+ 分门禁。
