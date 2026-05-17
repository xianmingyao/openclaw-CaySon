# 京麦桌面商品上架系统

## What This Is

这是一个面向京麦桌面端商品发布流程的自动化上架系统。目标不是单点 RPA 脚本，而是把 Excel 导入、京东商品补全、图片本地化、桌面操作、截图校验、失败反思、持久化运维和任务跟踪组织成一个可持续执行的工程化系统。

## Current Baseline

- 当前客观评分：`55 / 100`
- 评分来源：用户提供的《京麦桌面商品上架系统 — 代码开发评分分析》
- 旧自评处理：`IMPLEMENTATION_PROGRESS.md` 中的 `92/100` 和旧 `.planning` 中的 `95/100` 不再作为管理基线
- 当前判断：数据管道和基础桌面交互较扎实，但 Agent 决策、视觉校验、T6/T8 真实闭环、运维和多 Agent 仍不足以交付生产系统

## Core Value

必须把“从输入商品数据到京麦完成可验证的上架动作”做成真实、可追踪、可复现的闭环。探针成功、代码路径存在、单步点击成功，都不能替代真实上架结果。

## Requirements

### Validated

- [x] Excel -> MySQL -> Task 主链路基本完整
- [x] 图片下载、查重、格式转换、本地化链路基本完整
- [x] 京麦 T1~T4 基础页面接管和基础字段填写已形成闭环
- [x] ORM 和 Repository 底座已存在
- [x] 已有一批单元测试通过

### Active

- [ ] 完成 `T6` 主图上传真实闭环
- [ ] 完成 `T6` 透明图上传真实闭环
- [ ] 完成 `T6` 详情编辑器真实写入闭环
- [ ] 完成 `T8` 保存草稿 / 发布提交真实闭环
- [ ] 建立 `Planner / Executor / Reflection` Agent 决策层
- [ ] 将运行循环升级为 `observe -> decide -> act -> verify -> repeat`
- [ ] 接入真实视觉校验：截图前后对比、控件状态、视觉模型 provider
- [ ] 实现第 2 次失败切换 lane/operator 的重试策略
- [ ] 接入 Redis 状态/锁/事件流
- [ ] 接入 Milvus 长期反思记忆
- [ ] 完成日志和截图 3 天自动清理
- [ ] 建立端到端 UAT 和真实实机证据链

### Out of Scope

- 继续用 `IMPLEMENTATION_PROGRESS.md` 的乐观自评判断成熟度
- 将探针定位、按钮发现、代码路径存在标记为业务闭环完成
- 在 T6/T8 仍不可真实产出前扩散更多外围能力

## Constraints

- **Tech stack**: 维持现有 Python + SQLAlchemy + pywinauto/UIA + Playwright/HTTP 主链路
- **Architecture**: 后续改造必须对齐 UI-TARS 的 Agent loop 和 SightFlow 的 provider 解耦思想
- **Validation**: P0 任务完成必须有代码、测试、日志、截图或实机证据
- **Process**: 使用 `task_plan.md`、`findings.md`、`progress.md` 作为当前工作记忆；使用 `.planning` 作为项目管理事实源
- **Scoring**: 只有关闭真实缺口后才允许上调评分

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 将管理基线重置为 `55/100` | 新评估指出旧自评严重高估 | Active |
| P0 优先补 T6/T8 和 Reflection | 没有真实图片、详情、提交闭环，系统没有最终产出 | Active |
| Agent 决策层必须进入主架构 | 当前顺序执行无法满足 UI-TARS / SightFlow 对齐要求 | Active |
| `.planning` 只记录有证据的完成状态 | 防止再次出现“代码存在即完成”的偏差 | Active |

---
*Last updated: 2026-05-15 after re-baselining to 55/100*
