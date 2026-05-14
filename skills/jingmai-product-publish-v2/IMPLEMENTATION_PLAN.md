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

业务事实输入：
- `京麦上架流程.docx`
- `湖南上架表格.xlsx`

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
- 必须严格百分百复刻 `京麦上架流程.docx` 描述的上架顺序与必填规则
- 必须以 `湖南上架表格.xlsx` 的字段结构作为当前表格输入基线
- 必须支持通过飞书聊天面板发送本地文件路径来驱动上架任务
- 必须覆盖完整能力链：
  - `读取 Excel`
  - `区分单品/批量`
  - `抓取京东商品`
  - `图片本地化`
  - `MySQL 持久化`
  - `按京麦流程执行上架`
  - `截图视觉校验`
  - `失败最多重试 3 次`

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

但业务闭环必须始终围绕以下最终目标设计：

1. 飞书发送本地文件路径
2. 系统读取本地 `Excel`
3. 识别单品/批量任务
4. 从京东商品链接抓取商品数据
5. 自动补齐缺失字段
6. 自动抓取并本地保存商品图片
7. 若图片格式不符合要求则自动转换
8. 将商品数据持久化到 `MySQL`
9. 严格按 `京麦上架流程.docx` 执行桌面上架
10. 每步截图并进行视觉校验
11. 单步失败最多重试 `3` 次

---

## 2.1 京麦业务流程硬规则

根据 `京麦上架流程.docx`，当前项目必须严格复刻以下业务流程：

### A. 入口流程

标准路径：
- 首页
- 商品
- 发布商品
- 选择商品所属类目

要求：
- 类目必须从一级到末级依次选择
- 末级类目选定后系统自动匹配品牌
- 若自动匹配品牌不正确，必须展开全部品牌重新确认
- 确认品牌后点击“下一步，完善其他品牌信息”

### B. 商品基本信息硬规则

文档明确必填项：
- 商品标题
- 品牌
- 型号
- 是否厂直商品

业务要求：
- 所有品牌选择必须保持一致
- 标题必须体现卖点、功能、材质、颜色、规格等参数
- 标题长度不能超过 100 字符
- “是否厂直商品”必须选择“是”

### C. 采销价格硬规则

必须满足：
- 市场价 > 京东价 > 采购价

当前价格计算规则固定为：
- `采购价 = 京东价 * 0.95`
- `市场价 = 京东价 / 0.85`

补充说明：
- 用户要求市场价通常控制在高于京东价 `20%` 以内
- 当前默认公式按 `1 / 0.85` 计算，约等于高于京东价 `17.65%`

### D. 商品图片硬规则

主图要求：
- 至少 `3` 张
- 最多 `10` 张
- 比例 `1:1`
- 宽高均大于 `480px`
- 推荐尺寸 `1440 * 1440`
- 支持 `jpg / jpeg / png`

透明图要求：
- 仅商品主体
- 无底色
- 至少 `480 * 480`
- 比例 `1:1`
- 仅支持 `png`

### E. 商品详情硬规则

必须支持三种编辑路径：
- 高级编辑模式
- 代码编辑模式
- 图文编辑模式

详情图要求：
- 宽度 `750px - 1500px`
- 高度 `< 1500px` 时大小 `<= 3M`
- 高度 `>= 1500px` 时大小 `<= 5M`

### F. 物流售后硬规则

必须覆盖：
- 商品重量
- 包装长宽高
- 包装规格
- 包装清单
- 特殊发货时效标记
- 质保期

补充规则：
- 质保期至少 `1` 年（快消品除外）

### G. 提交流程硬规则

最终流程必须严格遵守：
- 检查所有带星号字段填写完整
- 点击“发布商品”
- 点击“继续发布”
- 进入采销审核阶段

任何实现如果跳过以上流程，都视为不满足业务文档。

---

## 2.2 Excel 输入基线

当前以 `湖南上架表格.xlsx` 第一张表 `上架模板` 为字段基线。

已识别核心字段：
- 上架序号
- 申请业务（自营/慧采）
- 商品名称（对应京东开票内容）
- 品牌
- 商品型号
- 长（mm）
- 宽（mm）
- 高（mm）
- 重（KG）
- 单位
- 京东挂网价（下单金额）
- 只能读取京东链接（无链接请通过其他方式新增商品）
- 商品资质（PDF格式）
- 商品简述（有特殊参数要求可以填）
- 备注（特殊要求）

后续所有 Excel 读取与字段映射，必须以这组字段为准。

---

## 2.3 任务输入方式硬规则

任务触发方式必须支持：

1. 飞书聊天面板发送一个文件
2. 该文件内容是一个“本地保存文件路径”
3. 系统读取该路径指向的 Excel 文件
4. 基于 Excel 生成上架任务

说明：
- 当前默认优先支持本地路径型任务
- 后续如扩展直接上传附件，不得影响当前路径型模式

---

## 2.4 数据补全与图片本地化硬规则

系统必须支持以下能力链：

1. 读取 Excel 行数据
2. 识别是单品任务还是批量任务
3. 从京东商品链接抓取商品数据
4. 将抓取到的图片下载到本地文件夹
5. 检查图片格式、尺寸、比例
6. 不符合要求时自动转换为有效格式
7. 如字段缺失，结合：
   - Excel 已有字段
   - 京东抓取字段
   - 商品标题/型号/品牌
   - 业务规则
   进行上架前数据补全

注意：
- 文本字段允许规则推断补全
- 图片字段必须先本地化后再上传，不允许直接远程链接上传
- 图片本地化后，必须将本地路径、来源链接、文件指纹、关联商品信息写入 `MySQL`
- 后续下载前必须先查重，避免重复下载相同图片资源

图片唯一性最小持久化字段：
- `image_source_url`
- `image_local_path`
- `image_sha256`
- `image_format`
- `image_width`
- `image_height`
- `product_id`
- `sku_or_row_id`
- `downloaded_at`

图片去重规则：
- 优先按 `image_source_url` 查重
- 其次按 `image_sha256` 查重
- 若已存在有效本地文件，则直接复用，不重复下载
- 若文件丢失或损坏，则允许重新下载并更新记录

---

## 2.5 持久化与重试硬规则

系统必须支持：
- 商品数据写入 `MySQL`
- 动作过程留存截图
- 视觉校验
- 单步失败最多重试 `3` 次
- 严格记录运行日志：
  - 成功日志
  - 错误日志
  - 准备日志
  - 运行过程日志
- 运行日志保留 `3` 天
- 超过 `3` 天的运行日志必须自动清理

重试规则：
- 重试计数必须按步骤记录
- 第 1 次失败：同 lane 重试
- 第 2 次失败：切换 lane 或 operator
- 第 3 次失败：转人工或标记失败

运行日志规则：
- 日志必须按任务维度归档
- 日志必须至少支持按：
  - `session_id`
  - `task_id`
  - `product_id`
  - `step_id`
  查询
- 日志清理任务必须自动执行，不能依赖人工手动清理

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

---

## 12. 当前已落地代码基座（2026-05-14）

本轮已经完成的基础实现如下：

### 12.1 配置与数据库基座

已实现：
- `.env` 配置加载
- `Settings` 配置对象
- SQLAlchemy `Base`
- 数据库 `Engine / SessionFactory` 创建

对应文件：
- `jingmai_publish/config.py`
- `jingmai_publish/db/base.py`
- `jingmai_publish/db/session.py`

### 12.2 ORM 模型

已实现表模型：
- `upload_jobs`
- `upload_job_items`
- `jd_product_snapshots`
- `product_images`
- `publish_tasks`
- `publish_task_steps`
- `runtime_logs`

对应文件：
- `jingmai_publish/models.py`

### 12.3 Repository 基座

已实现 Repository：
- `UploadJobRepository`
- `ProductImageRepository`
- `PublishTaskRepository`
- `PublishTaskStepRepository`
- `RuntimeLogRepository`

对应文件：
- `jingmai_publish/repositories/`

### 12.4 Service 基座

已实现：
- `ExcelIngestService`
- `ProductImageService`
- `PublishTaskService`

当前已固化业务规则：
- `采购价 = 京东价 * 0.95`
- `市场价 = 京东价 / 0.85`
- 图片按来源链接判重，避免重复下载

对应文件：
- `jingmai_publish/services/`

### 12.5 领域模型

已实现：
- `PreparedProductData`
- `PreparedImageData`

对应文件：
- `jingmai_publish/domain/prepared_product.py`

### 12.6 当前验证结果

已完成：
- 基础单元测试通过
- 配置加载验证通过
- `graphify update .` 已执行

### 12.7 已落地命令入口

已实现 CLI 命令：
- `init-db`
- `run-import`

当前能力：
- 可初始化数据库表结构
- 可从本地 Excel 文件路径触发导入主链路
- 可创建 `upload_jobs / upload_job_items / publish_tasks` 的代码入口

---

## 13. 下一步直接开发内容

紧接着进入以下实现，不再停留在设计层：

1. `Excel 真实解析入库`
   - 从 `湖南上架表格.xlsx` 读取真实表头和数据行
   - 过滤空行
   - 计算采购价/市场价
   - 创建 `upload_jobs` 与 `upload_job_items`

2. `任务创建主链路`
   - 基于导入批次逐行创建 `publish_tasks`
   - 建立 `job -> row -> task` 主链路
   - 为后续 `T1/T2/T4` 执行预留状态入口

3. `飞书本地路径输入兼容准备`
   - 当前先支持“本地文件路径字符串”导入
   - 后续无缝接到飞书聊天面板

当前实现目标：
- 证明 `Excel -> MySQL/Repository -> PublishTask` 主链路成立

### 13.1 已继续落地的主链路能力

已新增：
- `JDProductFetchService`
  - 提取京东商品 ID
  - 生成最小抓取快照
- `ProductDataPrepareService`
  - 合并 Excel 行与京东快照
  - 输出标准化 `PreparedProductData`

当前状态：
- 已完成“抓取骨架 + 字段补全骨架”
- 已完成图片下载/查重/格式转换主链路第一版
- 已完成 `T1/T2` 京麦桌面工作流骨架
- 已完成 `RealWindowsUIAAdapter` 第一版
- 已完成 `run-desktop-check` 调试增强输出
- 已完成 `click_text` 候选打分与命中策略优化
- 已完成定向调优接口（窗口关键词 / 控件类优先级 / 点击文本别名）
- 已完成命中失败回退策略（首选类 / 别名 / 总分回退）
- 已完成 T1 失败时的窗口快照回传
- 下一步继续进入真实抓取与京麦真实窗口实机验证
