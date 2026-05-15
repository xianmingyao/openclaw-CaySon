# 京麦桌面商品上架系统

## What This Is

这是一个面向京麦桌面端商品发布流程的自动化上架系统。它的目标不是做单点 RPA 脚本，而是把 Excel 导入、京东商品补全、图片本地化、桌面操作、截图校验、失败重试和任务跟踪组织成一个可持续执行的工程化系统。

当前代码已经证明“能导入、能持久化、能操作京麦部分页面”，但还没有达到完整可交付状态。本项目接下来的工作重点是把这些分散能力收口为真实闭环。

## Core Value

必须把“从输入商品数据到京麦完成可验证的上架动作”做成真实、可追踪、可复现的闭环，而不是只停留在探针和局部实验成功。

## Requirements

### Validated

- [x] 支持从本地 Excel 文件路径创建导入批次和发布任务
- [x] 支持商品图片下载、本地化、去重、基础格式校验
- [x] 支持真实京麦窗口接管以及部分基础字段实机填写

### Active

- [ ] 建立符合 `IMPLEMENTATION_PLAN.md` 的运行时内核：`TaskRunner / Session / observe -> decide -> act -> verify -> repeat`
- [ ] 恢复并补齐真实 `JDProductFetchService` 与 `ProductDataPrepareService` 源码，实现真实京东抓取和字段补全
- [ ] 完成 `T6` 主图 / 透明图 / 详情编辑器真实页面闭环
- [ ] 完成 `T8` 保存草稿 / 发布商品 / 继续发布 / 审核态确认闭环
- [ ] 接入飞书 / OpenClaw 消息入口，形成外部任务驱动
- [ ] 落地 `Reflection`、失败签名、三次重试和日志 3 天自动清理
- [ ] 让任务与步骤级审计从表结构预留变成真实运行链路

### Out of Scope

- 继续用单纯“探针成功率”替代完整闭环完成度
- 继续按 `IMPLEMENTATION_PROGRESS.md` 的乐观自评分数判断项目成熟度
- 在运行时内核未成型前继续扩散更多外围能力

## Context

- 评估基线以 `IMPLEMENTATION_PLAN.md` 和 `deep-research-report (3).md` 为准。
- 当前仓库没有 `.planning` 管理骨架，导致任务、里程碑和真实完成定义没有统一事实源。
- 当前测试入口存在工程化缺口：`python -m pytest -q` 可通过，直接 `pytest -q` 会失败。
- 当前源码中 `JDProductFetchService` / `ProductDataPrepareService` 仅保留可选导出与 `pyc` 痕迹，源文件缺失。
- `T6` 与 `T8` 仍处于 probe/桥接阶段，不应算作完整业务闭环。

## Constraints

- **Tech stack**: 维持现有 Python + SQLAlchemy + pywinauto/UIA 主链路，不做无关栈迁移
- **Architecture**: 必须对齐 `UI-TARS-desktop` 与 `sightflow-desktop-agent` 的运行时思想
- **Validation**: 任务完成必须有代码、测试、文档、必要的实机/日志证据，才允许标记 100%
- **Process**: 每完成一个任务都要更新 `.planning/STATE.md`、`.planning/BACKLOG.md` 和对用户汇报进度
- **Scoring**: 当前客观基线分为 `76/100`，后续只有在真实缺口关闭后才允许上调

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 以 76/100 作为当前管理基线 | 该分数来自代码与计划对照，不来自自评文档 | ✅ Good |
| 优先补“源码完整性 + 运行时内核 + T6/T8 真闭环” | 这是当前影响交付判断的主要短板 | ✅ Good |
| 用 `.planning` 作为后续唯一任务事实源 | 需要让任务、阶段、完成定义和汇报规则稳定落盘 | ✅ Good |
| 未满足验收定义的任务不得标记完成 | 防止再次出现“探针成功等于闭环完成”的偏差 | ✅ Good |

---
*Last updated: 2026-05-15 after establishing gstack/GSD project management baseline*
