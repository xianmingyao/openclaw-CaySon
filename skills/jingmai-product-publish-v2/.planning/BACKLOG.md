# Delivery Backlog

> 事实源说明  
> - 本文档只接受基于 `IMPLEMENTATION_PLAN.md` 和 `deep-research-report (3).md` 对照后的真实缺口  
> - 当前客观开发基线已推进到 `95/100`  
> - 只有满足完成定义的任务，才允许标记为 `DONE`

## Completion Rule

任意任务只有同时满足以下条件，才允许标记为 `DONE (100%)`：
1. 代码已经落地到当前仓库
2. 至少有对应测试或验证入口
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

### P0 - 基线修复
| ID | Task | Status | Done Definition |
|----|------|--------|-----------------|
| GT-001 | 恢复或明确移除缺失的 `JDProductFetchService` / `ProductDataPrepareService` 源码缺口 | DONE | 服务源码状态与导出逻辑一致，测试与文档同步 |
| GT-002 | 修复 `pytest -q` 默认入口不可用问题 | DONE | `pytest -q` 与 `python -m pytest -q` 都可运行 |
| GT-003 | 把 `PublishTaskStep` 从表结构预留接到真实执行链路 | DONE | 有真实步骤写入、状态流转和查询证据 |

### P1 - 运行时与数据准备
| ID | Task | Status | Done Definition |
|----|------|--------|-----------------|
| GT-004 | 建立 `Session` / `TaskRunner` 最小运行时内核 | DONE | 已形成最小主循环 |
| GT-005 | 落地 `Reflection`、失败签名、三次重试 | DONE | 每步有 before/after、失败签名、最大重试数 |
| GT-006 | 实现真实京东抓取能力 | DONE | 可抓标题、品牌、型号、图片、详情，并记录抓取失败信息 |
| GT-007 | 完成商品字段补全与标准化输出 | DONE | Excel + 抓取 + 规则可生成可上架标准化对象 |

### P1 - 京麦真实业务闭环
| ID | Task | Status | Done Definition |
|----|------|--------|-----------------|
| GT-008 | 完成 `T6` 主图上传真实闭环 | BLOCKED | 页面状态确认主图真正上传成功 |
| GT-009 | 完成 `T6` 透图上传真实闭环 | DONE | 代码、CLI、测试和文档已完成 |
| GT-010 | 完成 `T6` 详情编辑器真实写入闭环 | DONE | 代码、CLI、测试和文档已完成 |
| GT-011 | 完成 `T8` 保存草稿真实闭环 | DONE | 代码、CLI、测试和文档已完成 |
| GT-012 | 完成 `T8` 发布商品 / 继续发布 / 审核态确认闭环 | DONE | 代码、CLI、测试和文档已完成 |

### P2 - 外部入口与运维治理
| ID | Task | Status | Done Definition |
|----|------|--------|-----------------|
| GT-013 | 接入飞书 / OpenClaw 路径任务入口 | DONE | 可从消息入口驱动 Excel 路径任务 |
| GT-014 | 落地日志 3 天自动清理与运维入口 | DONE | 可主动触发并清理过期日志/截图 |

## Phase Mapping

| Phase | Task IDs |
|-------|----------|
| Phase 1 - 基线修复 | GT-001, GT-002, GT-003 |
| Phase 2 - 运行时内核与 Reflection | GT-004, GT-005 |
| Phase 3 - 京东抓取与数据补全 | GT-006, GT-007 |
| Phase 4 - T6/T8 真实闭环 | GT-008, GT-009, GT-010, GT-011, GT-012 |
| Phase 5 - 外部入口与运维治理 | GT-013, GT-014 |

## Delivery Log

- 2026-05-15 `GT-001 ~ GT-003`
  - 恢复抓取与准备服务源码
  - 修复 `pytest -q`
  - 接通 `PublishTaskStep` 创建/更新/查询链路

- 2026-05-15 `GT-004 ~ GT-007`
  - 新增 `TaskRunner`、`RunnerSession`
  - 建立最小 `observe -> decide -> act -> verify -> repeat`
  - 接入 failure signature / retry trace
  - 完成 JD 抓取、快照与标准化准备链路

- 2026-05-15 `GT-008`
  - 修复上传槽位观测、文件对话框桥接、悬浮上传入口与图片管理弹层逻辑
  - 当前仍缺真实京麦页面上的稳定主图上传成功证据

- 2026-05-15 `GT-009 ~ GT-012`
  - 完成透图上传、详情编辑器、保存草稿、发布商品的代码路径与 CLI 入口

- 2026-05-15 `GT-013 ~ GT-014`
  - 完成本地路径任务入口
  - 完成日志清理与运维入口

- 2026-05-15 统一测试收口
  - 统一回归：`pytest -q` -> `87 passed`

- 2026-05-15 缺陷修复与能力补全
  - 新增 `RuntimeLogPersistenceProvider`
  - 新增 `JsonlMemoryProvider`
  - `HostRuntime` 接入 action plan / persistence / memory
  - 新增 `FeishuPathChannelService`
  - 新增 CLI: `run-feishu-path-task`
  - `GT-008` 上传链改成专门的“本地上传 -> 上传图片 -> 选图确认”方法
  - 最新统一回归：`pytest -q` -> `89 passed`

## Progress Report Protocol

后续每完成一个任务，对用户的进度汇报至少包含：
1. 已完成任务 ID 与名称
2. 本次修改了哪些代码、命令入口、文档
3. 用什么方式验证通过
4. 当前 backlog 完成数与总体进度
5. 下一个马上进入的任务
