# 京麦桌面商品上架系统实施计划

最后更新：2026-05-14
适用范围：
- `E:\workspace\skills\jingmai-product-publish-v2\IMPLEMENTATION_PROGRESS.md`
- `C:\Users\Administrator\Downloads\deep-research-report (3).md`
- `https://github.com/bytedance/UI-TARS-desktop`
- `https://github.com/sightflow-dev/sightflow-desktop-agent`

本文档用途：
- 作为项目实施管理基线
- 将架构目标转换为可执行批次
- 用于跟踪提交计划、测试点、依赖关系与阶段验收

---

## 1. 实施原则

本项目只以以下两份文档为硬约束：
- `IMPLEMENTATION_PROGRESS.md`
- `deep-research-report (3).md`

所有实施决策必须满足：
- 京麦被视为 `Windows 桌面应用`
- 主执行链路必须优先采用 `UIA/Win32`
- 系统必须支持任务拆解式执行，而不是单函数直跑
- 每个关键动作后必须具备校验与证据留存能力
- 必须为后续 `CDP/Playwright`、`Vision/OCR`、`RPA fallback` 预留接口
- `.env` 作为统一配置事实源
- 必须严格对齐并借鉴：
  - `UI-TARS-desktop`
  - `sightflow-desktop-agent`

补充说明：
- 这里的“严格百分百按照”解释为：核心架构思想、模块边界、运行时循环、能力插件化方式必须强对齐。
- 业务适配层允许按京麦桌面应用现实情况做最小必要改造。
- 不做脱离当前业务的机械照搬，但必须能明确说明“当前实现分别对应两个参考仓库的哪个能力设计”。

---

## 1.1 参考仓库强制对齐规则

### A. UI-TARS-desktop 强制对齐项

当前项目必须对齐以下设计：
- `Agent / Operator / Loop` 分层
- 固定主循环：`observe -> decide -> act -> verify -> repeat`
- `Operator` 只负责执行，不负责决策
- 事件流必须可持续输出
- 截图/状态观察必须是循环中的一等公民

在当前项目中的对应关系：
- `Planner / Executor / Reflection` -> `Agent 决策层`
- `UIAOperator / CDPOperator / RPAOperator` -> `Operator 执行层`
- `TaskRunner` -> `Loop 驱动层`
- `ArtifactManager + EventBus` -> `事件流与观察层`

### B. sightflow-desktop-agent 强制对齐项

当前项目必须对齐以下设计：
- Host runtime 与能力 provider 解耦
- provider 以能力边界提供服务，不侵入主循环
- 配置、能力声明、调用协议清晰分离
- 输出统一结构化事件

在当前项目中的对应关系：
- `Runtime Kernel` -> `Host runtime`
- `Grounding / Vision / LLM / Persistence / Channel` -> `Provider 能力层`
- `.env + Config` -> `配置事实层`
- `ActionResult / ReflectionResult / Event` -> `结构化输出协议`

### C. 强制验收规则

后续每个核心模块在设计说明中都必须回答两个问题：

1. 它对齐 `UI-TARS-desktop` 的哪一部分？
2. 它对齐 `sightflow-desktop-agent` 的哪一部分？

如果回答不清楚，则视为架构偏离，不进入实现。

---

## 2. 实施目标

第一阶段目标不是一次性做完整上架系统，而是验证以下核心闭环：

1. 能接管京麦桌面窗口
2. 能进入商品发布入口
3. 能执行最小基础字段写入
4. 能以任务方式推进步骤
5. 能留下动作与结果证据

这 5 点成立后，才继续扩展：
- SKU
- 图片与详情
- 物流售后
- 草稿/发布
- Feishu/OpenClaw
- MySQL/Redis/Milvus

---

## 3. 批次计划总览

| 批次 | 名称 | 范围 | 目标 | 状态 |
|---|---|---|---|---|
| Batch-1 | 桌面基础执行层 | `WindowManager` + `UIAOperator` | 证明京麦桌面窗口可接管、可点、可输 | 未开始 |
| Batch-2 | 任务运行时内核 | `Session` + `TaskRunner` | 建立任务上下文与阶段驱动能力 | 未开始 |
| Batch-3 | 发布入口链路 | `T1 + T2` | 证明可进入商品发布入口 | 未开始 |
| Batch-4 | 基础信息最小闭环 | `T4` | 证明可写入最小商品基础信息 | 未开始 |

---

## 3.1 参考仓库映射矩阵

| 当前项目模块 | 对齐 UI-TARS-desktop | 对齐 sightflow-desktop-agent | 说明 |
|---|---|---|---|
| `TaskRunner` | 主循环驱动 | Host runtime | 负责驱动任务步骤，不直接执行业务控件 |
| `Session` | 运行上下文 | Host 状态容器 | 负责运行态上下文与任务状态 |
| `Planner / Executor / Reflection` | Agent 决策链 | Provider 调用消费者 | 负责决策，不直接点控件 |
| `UIA / CDP / RPA Operators` | Operator | 被 runtime 调度的能力实现 | 只执行动作，不决定动作 |
| `GroundingRouter` | Observe 阶段扩展 | Provider 聚合器 | 聚合 UIA/CDP/Vision/Anchor |
| `ArtifactManager / EventBus` | 事件流 | 结构化输出 | 负责证据、日志、事件归档 |
| `Config/.env` | 运行配置 | Provider 配置层 | 统一配置事实源 |
| `Persistence adapters` | 运行支撑 | Provider 化基础设施 | MySQL/Redis/Milvus/Local |

---

## 4. Batch-1 提交计划

### 4.1 范围

- `BL-009` `WindowManager`
- `BL-013` `UIAOperator.click`
- `BL-014` `UIAOperator.fill`

### 4.2 提交目标

目标：
- 枚举并识别京麦桌面窗口
- 激活并聚焦窗口
- 支持桌面控件点击
- 支持桌面输入框写值并复核

### 4.3 建议提交拆分

#### Commit 1
主题：
- 新增 `WindowManager` 骨架与窗口识别协议

内容：
- 窗口枚举
- 标题/类名/进程匹配
- 返回 `window_handle`

#### Commit 2
主题：
- 新增窗口激活、截图与失败分类

内容：
- 激活窗口
- 前置焦点
- 窗口截图
- `window_not_found / window_capture_failed`

#### Commit 3
主题：
- 新增 `UIAOperator.click`

内容：
- 按控件描述点击
- 点击后等待稳定
- 点击失败截图

#### Commit 4
主题：
- 新增 `UIAOperator.fill`

内容：
- 输入前清空
- 文本输入
- 输入后值复核
- `value_not_persisted`

### 4.4 测试点

功能测试：
- 能找到京麦窗口
- 能激活京麦窗口
- 能对目标窗口截图
- 能点击桌面控件
- 能对输入框写值
- 能读取回填值进行确认

异常测试：
- 京麦未启动
- 找到多个相似窗口
- 控件不可点击
- 控件不可编辑
- 输入后值未生效

验收标准：
- `window_handle` 获取稳定
- `click` 和 `fill` 都返回标准结果
- 每次失败都有截图和错误分类

---

## 5. Batch-2 提交计划

### 5.1 范围

- `BL-001` `Session`
- `BL-003` `TaskRunner`

### 5.2 提交目标

目标：
- 定义统一任务上下文
- 能按任务步骤推进执行
- 能记录每步状态

### 5.3 建议提交拆分

#### Commit 5
主题：
- 新增 `Session` 模型

内容：
- `session_id`
- `task_id`
- `product_id`
- `mode`
- `window_handle`
- `page_state`
- `current_step`
- `artifact_refs`
- `last_failure_signature`

#### Commit 6
主题：
- 新增 `TaskState` 与最小阶段流转

内容：
- `INIT`
- `ATTACHED`
- `RUNNING`
- `STEP_FAILED`
- `COMPLETED`

#### Commit 7
主题：
- 新增 `TaskRunner`

内容：
- 创建任务会话
- 驱动任务步骤
- 接收步骤结果
- 决定继续/失败

### 5.4 测试点

功能测试：
- 能创建新任务会话
- 能记录并更新当前步骤
- 能根据步骤结果流转状态
- 能在失败时记录失败签名

异常测试：
- 会话字段缺失
- 未定义状态流转
- 步骤返回非法结果

验收标准：
- `TaskRunner` 能驱动最小任务链
- `Session` 可序列化、可传递

---

## 6. Batch-3 提交计划

### 6.1 范围

- `BL-033` `TASK-T1-attach-window`
- `BL-034` `TASK-T2-enter-publish-entry`

### 6.2 提交目标

目标：
- 接管京麦窗口
- 进入商品发布入口
- 更新页面状态

### 6.3 建议提交拆分

#### Commit 8
主题：
- 新增 `T1` 接管京麦窗口任务

内容：
- 调用 `WindowManager`
- 截图当前窗口
- 初步识别页面状态
- 写入 `Session.window_handle`

#### Commit 9
主题：
- 新增 `T2` 进入商品发布入口任务

内容：
- 查找菜单/发布入口
- 点击进入
- 等待页面切换
- 更新 `page_state`

#### Commit 10
主题：
- 新增 `T1/T2` 结果标准化与失败分类

内容：
- `publish_entry_not_found`
- `navigation_blocked`
- `page_state_not_changed`

### 6.4 测试点

功能测试：
- 可在京麦首页完成窗口接管
- 可识别当前是否处于首页/工作台
- 可进入发布入口
- 进入后页面状态发生变化

异常测试：
- 首页结构变化
- 菜单被折叠
- 弹窗遮挡
- 页面切换超时

验收标准：
- 能完成 `T1 -> T2`
- 成功后 `page_state` 进入发布相关状态
- 失败时有前后截图与明确原因

---

## 7. Batch-4 提交计划

### 7.1 范围

- `BL-036` `TASK-T4-fill-base-info`

### 7.2 提交目标

目标：
- 在发布表单中写入最小基础信息
- 至少覆盖标题与一个基础必填属性

### 7.3 建议提交拆分

#### Commit 11
主题：
- 新增基础信息字段映射最小集

内容：
- 标题
- 品牌（若类目必需）
- 一个关键属性

#### Commit 12
主题：
- 新增 `T4` 基础信息填写任务

内容：
- 定位标题输入区
- 输入商品标题
- 写入基础属性
- 输入后复核

#### Commit 13
主题：
- 新增 `T4` 失败签名与最小校验

内容：
- `title_not_persisted`
- `required_attr_missing`
- `brand_not_selected`

### 7.4 测试点

功能测试：
- 能写入商品标题
- 能识别标题已生效
- 能完成至少一个基础属性填写
- 若品牌为必填，则能完成品牌选择

异常测试：
- 标题输入框未找到
- 输入后值被系统覆盖
- 属性区控件类型不稳定
- 品牌下拉加载失败

验收标准：
- 标题可见且已写入
- 至少一个基础必填项可确认完成
- 任务结果可进入后续 `T5/T6/T7`

---

## 8. 四个批次的依赖关系图

```text
Batch-1
  ├─ WindowManager
  ├─ UIAOperator.click
  └─ UIAOperator.fill
       │
       v
Batch-2
  ├─ Session
  └─ TaskRunner
       │
       v
Batch-3
  ├─ T1 attach window
  └─ T2 enter publish entry
       │
       v
Batch-4
  └─ T4 fill base info
```

扩展依赖：

```text
Batch-4
  ├─ 为 T5 SKU 提供表单上下文
  ├─ 为 T6 图片与详情提供页面基础状态
  ├─ 为 T7 物流售后提供前置字段完成状态
  └─ 为 T8 提交校验提供基础信息完成状态
```

---

## 9. 批次完成定义

### Batch-1 完成定义

- 京麦桌面窗口可被稳定识别
- 可完成基础点击与输入
- 失败有截图与错误分类

### Batch-2 完成定义

- 任务具备会话与状态流转
- 步骤执行结果可以驱动主流程推进

### Batch-3 完成定义

- 能进入京麦商品发布入口
- 页面状态能被更新与记录

### Batch-4 完成定义

- 能写入最小基础信息
- 标题与基础必填项可被确认成功

---

## 10. 当前实施优先级

当前只做以下顺序，不提前扩散：

1. Batch-1
2. Batch-2
3. Batch-3
4. Batch-4

暂不提前展开：
- SKU
- 图片与详情
- 物流售后
- 正式发布
- Feishu/OpenClaw
- MySQL/Redis/Milvus 真写入

原因：
- 当前首要目标是证明“桌面商品上架最小闭环成立”
- 只有这个成立，后续复杂模块才有实施价值

---

## 11. 更新规则

每次开发后必须同步更新本文档：
- 批次状态
- 已完成提交
- 新发现阻塞
- 测试结果
- 是否达到该批次完成定义

批次状态统一使用：
- `未开始`
- `进行中`
- `已完成`
- `阻塞`
- `待验证`
