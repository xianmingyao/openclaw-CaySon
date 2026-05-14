# 京麦自动化发布项目实施进度

最后更新：2026-05-14  
管理方式：按 `gstack` 风格维护阶段、状态、下一步与验收条件，不依赖对话上下文。

## 总体状态

当前阶段：Phase 5  
总体进度：75%  
项目状态：进行中

## 阶段总览

| 阶段 | 名称 | 状态 | 说明 |
|---|---|---|---|
| Phase 0 | 需求与参考架构对齐 | 已完成 | 已读取需求文档，并对齐 `UI-TARS` 与 `SightFlow` 的核心设计思想。 |
| Phase 1 | Python CLI MVP 骨架 | 已完成 | 已完成 CLI、Planner、Grounding、Executor、Reflection、Mock Provider、Mock Operator、测试。 |
| Phase 2 | 执行器主链路与兜底链路 | 已完成 | 已完成 `PlaywrightJingmaiOperator + RpaScriptOperator + ResilientJingmaiOperator` 骨架，并接入真实 `playwright` / 脚本桥接入口。 |
| Phase 3 | 真实 Hybrid Grounding | 已完成 | 已完成 DOM / 视觉 / 锚点三路仲裁骨架，并接入 CLI 默认运行链路。 |
| Phase 4 | 京麦字段级策略与校验层 | 已完成 | 已完成字段级 operations、首版 `ReflectionAgent`、首版 `sku_strategy`、首版 `field map` 配置文件。 |
| Phase 5 | 任务状态持久化与事件审计 | 进行中 | 已接入本地必落盘归档，并补 MySQL / Redis / Milvus 适配器骨架。 |
| Phase 6 | 飞书/OpenClaw 集成 | 未开始 | 命令入口、状态回传、人工中止 / 恢复。 |
| Phase 7 | UAT 与上线准备 | 未开始 | 白名单店铺测试、草稿模式回归、正式发布审批。 |

## 已完成

- 已读取需求文档：`C:\Users\Administrator\Downloads\deep-research-report (3).md`
- 已拉取并分析参考仓库：
  - `https://github.com/bytedance/UI-TARS-desktop`
  - `https://github.com/sightflow-dev/sightflow-desktop-agent`
- 已建立 Python 包骨架
- 已实现预校验、计划生成、事件流、编排器主循环
- 已实现 mock provider / mock operator
- 已实现 `Playwright -> RPA fallback` 执行器链路
- 已接入 `.env` 作为配置事实源
- 已实现 `HybridGroundingProvider`
- 已补字段级 `selector / operations` 生成骨架
- 已实现首版 `ReflectionAgent` 页面级校验
- 已实现首版 `sku_strategy`
- 已实现首版 `field map` 配置文件与加载器
- 已补真实 `Playwright` 集成测试骨架
- 已接入本地持久化归档
- 已补 MySQL / Redis / Milvus 适配器骨架
- 已补基础测试，当前通过 `14` 项

## 当前进行中

### Phase 5：任务状态持久化与事件审计

目标：

- 让事件、报告、反思结果不再只存在内存中
- 为后续 MySQL / Redis / Milvus 真实接入铺路

当前状态：

- 已完成本地 JSONL / JSON 归档
- 已完成外部适配器骨架
- 已完成 orchestrator 持久化钩子
- 未完成 MySQL / Redis / Milvus 真实写入
- 未完成截图 / artifact 二进制归档

验收条件：

- 每次运行至少落盘 `events.jsonl` 和 `report.json`
- Orchestrator 自动调用持久化管理器
- 后续可以无缝切换到真实数据库 / 向量库

## 下一步

1. 扩展 `.env` 到 provider / 持久化开关层
2. 接入飞书 / OpenClaw 入口
3. 增加 artifact 截图归档
4. 增加 MySQL / Redis / Milvus 真实写入
5. 开始 UAT 所需的运行基线与样本

## 当前风险

- 当前 MySQL / Redis / Milvus 仍是适配器骨架，不是实际写入
- 当前没有飞书入口与人工审批闭环
- 当前没有真实京麦页面集成测试样本
- 当前 artifact 还没有单独落盘管理

## 里程碑验收

### M1：本地真实浏览器闭环

标准：

- 能在本地浏览器中完成真实截图、点击、输入、上传
- 能在一次失败后触发 RPA 兜底

### M2：京麦页面真实字段流

标准：

- 能走通类目、基础信息、SKU、图片、详情、物流售后、保存草稿

### M3：系统级接入

标准：

- 飞书可触发、任务可中止、状态可回传、证据可追溯

## 进度更新规则

每次开发后都要更新：

- 当前阶段
- 已完成项
- 下一步
- 风险变化
- 是否达到新的里程碑
