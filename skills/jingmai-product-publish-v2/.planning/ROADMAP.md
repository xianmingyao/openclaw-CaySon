# Roadmap: 京麦桌面商品上架系统补完计划

## Overview

当前项目已经完成：
- 数据导入与持久化底座
- 京东抓取与标准化准备链路
- 最小运行时主循环、失败签名、三次重试
- 京麦 `T1 ~ T8` 大部分代码路径与 CLI 入口
- 本地路径消息入口、飞书 payload 入口、运行日志治理入口
- host runtime 下的 persistence / memory / channel provider 最小实现

当前仍未完成的核心项只有一个：
- `GT-008` 主图上传真实页面闭环

## Phases

- [x] **Phase 1: 基线修复**
- [x] **Phase 2: 运行时内核与 Reflection**
- [x] **Phase 3: 京东抓取与数据补全**
- [ ] **Phase 4: T6/T8 真实闭环**
- [x] **Phase 5: 外部入口与运维治理**

## Phase Details

### Phase 1: 基线修复
**Goal**: 修复源码完整性、测试入口、步骤审计接线。  
**Status**: Completed

Completed:
- 恢复缺失源码
- 修复 `pytest -q`
- 接通 `PublishTaskStep`

### Phase 2: 运行时内核与 Reflection
**Goal**: 建立最小运行时、trace、失败签名、重试机制。  
**Status**: Completed

Completed:
- `TaskRunner`
- `RunnerSession`
- before/after trace
- failure signature
- retry loop
- `HostRuntime + ProviderRegistry` 最小运行时

### Phase 3: 京东抓取与数据补全
**Goal**: 从京东商品链接到标准化上架对象形成闭环。  
**Status**: Completed

Completed:
- `JDProductFetchService`
- `ProductDataPrepareService`
- 导入主链路接通抓取、快照、标准化输出

### Phase 4: T6/T8 真实闭环
**Goal**: 把图片、详情、草稿、发布从“代码存在”推进到“真实页面成功”。  
**Status**: In progress

Completed in code:
- `T6` 主图上传链已专门化为“本地上传 -> 上传图片 -> 选图确认”
- `T6` 透图上传流程
- `T6` 详情编辑器写入流程
- `T8` 保存草稿流程
- `T8` 发布商品 / 继续发布 / 审核提示流程

Still missing:
- `GT-008` 主图真实上传成功证据

### Phase 5: 外部入口与运维治理
**Goal**: 让系统具备正式任务入口与自清理能力。  
**Status**: Completed

Completed:
- `run-local-path-task`
- `run-feishu-path-task`
- `LocalPathChannelService`
- `FeishuPathChannelService`
- `cleanup-runtime-logs`
- `RuntimeRetentionService`

## Progress

| Phase | Status | Notes |
|-------|--------|-------|
| 1. 基线修复 | Completed | 已完成 |
| 2. 运行时内核与 Reflection | Completed | 已完成 |
| 3. 京东抓取与数据补全 | Completed | 已完成 |
| 4. T6/T8 真实闭环 | In progress | 只差 `GT-008` 实机成功证据 |
| 5. 外部入口与运维治理 | Completed | 已完成 |

## Final Acceptance Path

达到 `100/100` 的前置条件：
1. `GT-008` 完成真实京麦页面验收
2. 主图上传闭环具备稳定截图证据
3. 全量回归继续保持通过
4. 若要完全对齐研究报告，再接 Redis/Milvus/多 Agent 正式运行时
