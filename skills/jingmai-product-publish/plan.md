# 京麦应用商城商品上架 Skill 方案评审

## 评审视角

采用 **OpenClaw / CEO（龙虾）视角** 做判断，不看“谁架构最炫”，只看三件事：

1. **最短路径能不能稳定把商品上架跑通**
2. **失败时能不能定位、恢复、续跑**
3. **未来 1-3 个月能不能持续演进，而不是越改越乱**

结论先行：

- **当前最适合直接承担京麦商品上架任务的版本：`jingmai-product-publish`**
- **最有平台能力、适合做底座能力输入的版本：`desktop-control-cli`**
- **最懂历史场景、但最需要收敛重构的版本：`jingmai-product-publish-v1`**
- **最像“通用智能体平台”的版本：`jingmai-putaway`，但不适合直接作为本次主交付版本**

---

## 一句话判断

### 推荐顺序

1. **主线推荐：`E:\workspace\skills\jingmai-product-publish`**
2. **能力借鉴：`E:\workspace\skills\desktop-control-cli`**
3. **经验回收：`E:\workspace\skills\jingmai-product-publish-v1`**
4. **暂不作为主线：`E:\workspace\skills\jingmai-putaway`**

### 推荐原因

`jingmai-product-publish` 是四者里最接近“可交付产品”的版本：它已经具备 `plan -> execute -> verify -> batch -> resume` 的闭环，有独立 action 层、planner、executor、memory、db、tests，复杂度比平台型项目低，收敛成本最低，最适合尽快做成一个真正可复用的京麦上架 skill。

---

## 版本对比

## 1. `jingmai-product-publish-v1`

### 优点

- 场景非常聚焦，明显是围绕京麦商品发布反复试出来的。
- UIA、坐标、弹窗、价格、分类、属性等细节积累很多。
- 脚本数量大，说明历史上踩坑多、覆盖面广。
- 对“怎么点、怎么填、哪里会卡”有很强的一线经验价值。

### 缺点

- 结构明显偏“脚本堆积”，`scripts/` 下文件过多，维护成本高。
- 缺少统一编排层，很多逻辑是一次性脚本或局部修补。
- 缺少稳定的任务模型、计划模型、恢复模型。
- 测试与契约化不足，不利于长期演进。
- 很容易出现“修一个点，坏另一个点”的问题。

### CEO 判断

这是一个 **战场遗迹型版本**。它不是最优交付形态，但它保存了最多的真实战斗经验。不能继续当主干长期扩写，但必须把其中的有效策略抽出来，喂给新主线。

---

## 2. `desktop-control-cli`

### 优点

- 平台能力最强，覆盖 `ufo / evolution / bridge / agents / vision / mcp`。
- `agents publish` 已支持 `--use-vision`、`--loop-count`、`--resume` 等能力。
- 通用性强，后续可复用到别的桌面自动化任务。
- 测试数量和工程规模明显更成熟，适合作为能力底座。

### 缺点

- 过重。项目体量极大，对“京麦上架”这个单任务来说认知负担太高。
- 平台型抽象多，专项问题定位链路会更长。
- 京麦专项知识分散在大平台里，不利于快速迭代一个单 skill。
- 一旦要修京麦业务问题，容易牵动平台层，改动半径过大。

### CEO 判断

这是 **平台，不是刀**。它适合输出基础能力，不适合直接作为“京麦上架 skill”的主仓。正确姿势不是迁移过去，而是从里面借能力。

建议借鉴的能力：

- 视觉识别兜底
- `resume/progress` 批量续跑
- bridge/browser 辅助采集
- 更成熟的 agent CLI 体验

---

## 3. `jingmai-putaway`

### 优点

- 有完整 CLI、memory、rag、skills、status 等系统化设计。
- 有内置 `jingmai_product_publish` 资源 skill，并考虑了 `start_from_phase`。
- 对 Session 隔离问题有显式设计，说明作者意识到远程桌面/服务会话问题。
- 适合做“更通用的京麦智能体系统”。

### 缺点

- 系统依赖重，明显比当前任务所需复杂。
- 更偏通用 agent 框架，而不是单目标高确定性工具。
- RAG / memory / skills / async service 等能力很多，但对“今天把商品稳定上架”不是第一优先级。
- 架构收益需要更大业务规模才能摊薄，不适合当前快速交付。

### CEO 判断

这是 **中远期平台路线候选**，不是当前最优主线。它值得借鉴 Session 对齐、skill runtime、混合人工/自动阶段执行的思路，但现在直接采用，交付速度会变慢。

---

## 4. `jingmai-product-publish`

### 优点

- 已具备明确的主入口：`publish / plan / execute / batch / scrape / think / status / memory`
- 已经形成独立层次：
  - `actions/`
  - `agents/`
  - `infrastructure/`
  - `memory/`
  - `llm/`
- 明确采用 `Plan-and-Solve + ReAct + Reflection` 执行模式。
- 具备计划持久化、任务状态、步骤状态、失败恢复基础能力。
- 有行为测试，覆盖 planner、executor、locator、verify、batch、plan 兼容等关键路径。
- 相比 v1，已经把“经验脚本”收敛成可维护工程。

### 缺点

- 仍然混有一部分“实验性智能化”设计，真实稳定性还需继续压实。
- `verification` 仍偏弱，更多是 UIA/文本探测，不够“业务结果导向”。
- 图片上传、属性填写、类目切换、弹窗恢复等高风险路径还需要更细的状态机。
- 目前 tests 数量还不算多，对真实京麦页面变化的防御还不够。
- 对 Session、人工接管、断点恢复的用户操作手册还不够强。

### CEO 判断

这是 **最合理的当前主线**。它已经从“脚本集合”进化到“可交付系统”，但还没进化到“强鲁棒生产工具”。最优策略不是换仓，而是继续在这个仓里做第二轮产品化收敛。

---

## 总结评分

| 版本 | 直接完成京麦上架 | 可维护性 | 工程复杂度控制 | 平台扩展性 | 当前推荐度 |
|---|---:|---:|---:|---:|---:|
| `jingmai-product-publish-v1` | 7 | 3 | 2 | 4 | 6 |
| `desktop-control-cli` | 6 | 8 | 3 | 10 | 7 |
| `jingmai-putaway` | 6 | 7 | 4 | 8 | 6 |
| `jingmai-product-publish` | 8 | 8 | 8 | 7 | **9** |

---

## 核心建议

## 推荐架构策略

**不要重选主仓。**

主仓继续使用：

- `E:\workspace\skills\jingmai-product-publish`

同时做两件事：

1. **从 `jingmai-product-publish-v1` 回收领域脚本经验**
2. **从 `desktop-control-cli` 借鉴通用能力，而不是整体迁移**

`jingmai-putaway` 仅保留为未来平台化参考，不作为当前主线。

---

## 为什么不是别的版本

### 不是 `v1`

因为它更像“积累经验的脚本仓”，不是“稳定交付的产品仓”。

### 不是 `desktop-control-cli`

因为它是平台，太大太重。你现在要的是“把京麦上架做成”，不是“做一个完整桌面自动化操作系统”。

### 不是 `jingmai-putaway`

因为它的系统野心大于当前任务刚需，交付效率会被架构复杂度吃掉。

---

## 最优优化方向

目标不是继续堆智能，而是做 **高确定性、可恢复、可观测** 的上架 skill。

### 优先级 P0：把当前 skill 做成“稳定工具”

1. **固化业务状态机**
   - 明确 Phase 0~N：
   - `window_ready`
   - `publish_page_ready`
   - `category_ready`
   - `basic_info_ready`
   - `price_ready`
   - `attributes_ready`
   - `media_ready`
   - `draft_saved`
   - `publish_submitted`
   - `publish_verified`

2. **每个 Phase 增加前置校验 + 退出条件**
   - 不再只看 action 成败
   - 要看“页面是否真的处于预期业务态”

3. **把高风险步骤改成显式恢复策略**
   - 类目选择失败
   - 属性未展开
   - 价格回读失败
   - 弹窗遮挡
   - 图片上传卡住
   - 发布后未返回成功提示

4. **把 batch 真正做成可续跑**
   - 每个商品一个 `task_id`
   - 每个商品保存最后成功 phase
   - 支持从 phase 恢复，而不是只能从 step 恢复

### 优先级 P1：吸收 v1 的有效资产

把 `v1/scripts` 里高价值能力迁入当前工程，但必须经过重构，不允许直接复制一堆独立脚本进主线。

优先迁移类型：

- 稳定的 UIA 查找器
- 分类搜索/选择策略
- 价格填写和校验策略
- 弹窗关闭策略
- 属性填写特例逻辑
- 保存草稿/发布后的结果确认逻辑

迁移原则：

- 迁入 `actions/` 或 `infrastructure/`
- 每个迁入能力必须带统一接口
- 每个迁入能力至少补 1 个测试

### 优先级 P2：借用 `desktop-control-cli` 的平台能力

重点借能力，不借系统。

建议借入：

1. **Vision 兜底层**
   - 当前 UIA 定位失败时，增加视觉识别 fallback
   - 只用于高风险关键点，不要全流程都靠视觉

2. **批量进度模型**
   - 参考 `loop-count / resume / progress-file`
   - 为当前 `batch` 增加明确的进度文件格式

3. **浏览器桥能力**
   - 用于商品采集、页面信息补充、图片源下载
   - 不建议主流程上架依赖 browser bridge

### 优先级 P3：借用 `jingmai-putaway` 的两点思路

1. **`start_from_phase` 混合执行**
   - 允许人工完成 Phase 1-2，skill 从 Phase 3 开始
   - 这对远程桌面、会话隔离、类目难选场景非常关键

2. **Session 显式检查**
   - 在 CLI 启动和执行前都检查当前会话
   - 明确提示用户“现在不能自动操作 GUI”的原因

---

## 推荐执行方案

## 方案 A：最小可交付方案（推荐）

### 目标

在 `jingmai-product-publish` 内，把“单商品稳定上架 + 批量续跑”做扎实。

### 交付范围

- 保留当前架构
- 引入 phase 状态机
- 引入更强恢复机制
- 吸收 v1 的关键脚本经验
- 增加批量续跑与业务验证

### 优点

- 变更半径最小
- 交付速度最快
- 风险最低
- 最容易快速看到效果

### 缺点

- 平台通用性不如 `desktop-control-cli`
- 长期想做通用桌面 agent，后面还要再抽象

---

## 方案 B：平台能力注入方案

### 目标

主仓仍是 `jingmai-product-publish`，但引入部分 `desktop-control-cli` 能力模块。

### 适合场景

- 你已经确认需要视觉识别和更强批量能力
- 愿意接受更复杂的集成工作

### 风险

- 接口风格不统一
- 依赖变重
- 集成问题可能吞掉大量时间

---

## 方案 C：迁移到通用平台（不推荐当前执行）

### 目标

以 `desktop-control-cli` 或 `jingmai-putaway` 为主仓，京麦上架成为其中一个 skill。

### 为什么当前不推荐

- 这不是最短交付路径
- 迁移成本远高于业务收益
- 你会先陷入框架整合，而不是解决上架稳定性

---

## 最终推荐

**选择方案 A，并吸收方案 B 的少量能力。**

一句话说就是：

**以 `jingmai-product-publish` 为主线，回收 `v1` 的领域经验，定点借用 `desktop-control-cli` 的 vision/progress 能力，暂不迁移到更重的平台。**

---

## 分阶段落地计划

## Phase 1：主线收敛（1-2 天）

目标：把当前仓的行为边界定义清楚。

任务：

1. 盘点当前 `actions` 和真实页面 phase 的映射关系
2. 明确每个 phase 的进入条件、成功条件、失败条件
3. 设计统一的 phase 恢复数据结构
4. 明确哪些步骤必须 UIA，哪些步骤允许视觉兜底

产出：

- `docs/phase-model.md`
- `data/plans/` 的新计划结构草案

## Phase 2：经验回收（2-3 天）

目标：把 v1 里真正有用的脚本资产抽成当前可维护模块。

任务：

1. 给 `v1/scripts` 做分类：
   - 可迁移
   - 可废弃
   - 仅供参考
2. 优先迁移 5 类能力：
   - 类目搜索/选择
   - 属性填写
   - 价格处理
   - 弹窗恢复
   - 发布确认
3. 所有迁移必须进入 `actions/` 或 `infrastructure/`

产出：

- 新的统一 action
- 对应测试用例

## Phase 3：恢复与续跑（2 天）

目标：失败后不是重头再来，而是从业务 phase 恢复。

任务：

1. 扩展 task/step 持久化模型，增加 `phase`
2. batch 输出进度文件
3. 支持：
   - 从商品级恢复
   - 从 phase 级恢复
   - 人工接管后继续执行

产出：

- `resume --from-phase`
- `batch progress.json`

## Phase 4：视觉兜底（可选，2-4 天）

目标：只在 UIA 不稳定的关键点启用视觉识别。

任务：

1. 接入轻量视觉定位接口
2. 仅对以下步骤开放 fallback：
   - 类目搜索结果选择
   - 发布按钮定位
   - 弹窗确认按钮
   - 图片上传确认
3. 增加日志：
   - 当前使用的是 UIA 还是 Vision
   - 视觉置信度

产出：

- `vision_fallback`
- 对应失败诊断日志

## Phase 5：生产化验收（1-2 天）

目标：验证它不是“能跑一次”，而是“能重复交付”。

验收清单：

1. 单商品成功上架 3 次
2. 5 个商品 batch 跑通
3. 中断后 resume 跑通
4. 至少 2 类故障可恢复：
   - 弹窗
   - 页面漂移/焦点丢失
5. 日志能定位失败原因

---

## 必须补的能力清单

1. **业务态验证**
   - 不能只看点击成功
   - 要看页面真的到了哪一步

2. **Phase 级恢复**
   - 这是生产可用和 demo 可用的分水岭

3. **图片上传与属性填写专项处理**
   - 这是京麦上架最容易卡死的区域

4. **人工/自动混合模式**
   - 支持用户手工选类目后，从表单阶段接管

5. **更强日志和失败分类**
   - `定位失败`
   - `写入失败`
   - `回读失败`
   - `页面状态错误`
   - `会话错误`

---

## 不建议做的事

1. 现在就整体迁移到 `desktop-control-cli`
2. 现在就把 `jingmai-putaway` 当主线重建
3. 继续在 `v1` 上新增更多散脚本
4. 全流程依赖 LLM/视觉判断

原因：

- 这些动作都不走最短交付路径
- 会让复杂度先于价值到来

---

## 最终决策

### 主线决策

使用 `E:\workspace\skills\jingmai-product-publish` 作为京麦应用商城商品上架任务的主实现版本。

### 改造策略

- 从 `jingmai-product-publish-v1` 回收专项经验
- 从 `desktop-control-cli` 借 vision/progress 思路
- 从 `jingmai-putaway` 借 `start_from_phase` 和 session 检查思路

### 交付目标

把当前 skill 从“能跑”升级为：

- **能稳定跑**
- **失败能恢复**
- **批量能续跑**
- **日志能诊断**

这才是一个真正可用的京麦上架 skill。
