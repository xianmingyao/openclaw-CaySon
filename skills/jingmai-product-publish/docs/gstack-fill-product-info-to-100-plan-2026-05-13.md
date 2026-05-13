# fill_product_info 100分修复单 2026-05-13

## 当前结论

当前完成度评估为 `64/100`。

这轮最大阻塞不是点击坐标，而是 `fill_product_info` 的 `precheck` 误杀了本来可以继续执行的正确页面。

证据：

- 运行日志：[publish_20260513_162539.log](E:/workspace/skills/jingmai-product-publish/logs/publish_20260513_162539.log)
- acceptance 产物：[caa0589c.json](E:/workspace/skills/jingmai-product-publish/data/acceptance-runs/acceptance-20260513-162532-a6122f/caa0589c.json)
- 记忆记录：[6ac030b8.json](E:/workspace/skills/jingmai-product-publish/logs/memory/short_term/6ac030b8.json)
- 截图：
  - [caa0589c_precheck_fill_product_info_1778660741.png](E:/workspace/skills/jingmai-product-publish/resources/screenshots/caa0589c_precheck_fill_product_info_1778660741.png)
  - [caa0589c_recovery_recovery_fill_product_info_1_1778660771.png](E:/workspace/skills/jingmai-product-publish/resources/screenshots/caa0589c_recovery_recovery_fill_product_info_1_1778660771.png)
- [caa0589c_precheck_fill_product_info_1778660788.png](E:/workspace/skills/jingmai-product-publish/resources/screenshots/caa0589c_precheck_fill_product_info_1778660788.png)
- [caa0589c_precheck_fill_product_info_1778660807.png](E:/workspace/skills/jingmai-product-publish/resources/screenshots/caa0589c_precheck_fill_product_info_1778660807.png)

## 当前进度

- `P0-4` 已完成：
  已为计划字段补充 `component_type` 与 `interaction_strategy`，并覆盖商品名称输入、品牌下拉、SKU 横向滚动表格、图片上传等关键交互类型。
- `P0-3` 已部分完成：
  已扩展 `required_visual_fields` 覆盖更多必填字段，并新增 `required_field_report`，可区分字段是 `provided / inferred / missing`。
- 仍待完成：
  - `P0-1` precheck 误杀彻底闭环
  - `P0-2` 模板缺失时的降级链与模板补齐
  - `P1-1` 统一结构化日志
  - `P1-2` 拆分 `actions/form.py`
  - `P2-1` acceptance 实机验收

## 失败根因

### 根因 1：precheck 状态映射错误

- 首次 `precheck` 拦住“京东智铺 | 详情”弹窗页是正确的。
- 恢复后页面已经回到商品基础信息页。
- 视觉自然语言结论明确表示“当前页面是商品信息页面，可安全继续”。
- 但执行器仍把结果记成 `status=error`，并重试到失败。

结论：`doc_strict precheck` 的结果解析、状态映射、最终放行条件存在冲突。

### 根因 2：模板链缺失导致预检退化

日志中持续出现模板缺失：

- `product_title_label.png`
- `market_price_label.png`
- `jd_price_label.png`

结论：当前 `fill_product_info` 的页面确认过度依赖本地模板，但模板资产并不完整，需要补齐或降级到结构化弱信号。

### 根因 3：商品字段生成仍不完整

`caa0589c.json` 中虽然已经有：

- `title`
- `brand`
- `market_price`
- `jd_price`
- `description_images`
- `images`
- 尺寸重量基础字段

但仍缺少或明显脏值的字段包括：

- `model`
- `unit`
- `socket_config`
- `rated_voltage`
- `cable_length`
- `protection_level`
- `pole_count`
- `current`
- `current_order`
- `short_title`
- `purchase_price`
- `gross_margin`
- `sku_attributes`
- `sku_square_image`
- `sku_transparent_image`
- `shelf_life_days`
- `package_type`
- `sales_unit`
- `special_delivery_mark`
- `packing_list`
- `warranty_period`

结论：计划生成的数据还没有覆盖商品信息页所有星号必填字段，必须在抓取不足时做推理补全。

## 100分定义

达到 `100/100`，必须同时满足：

1. `fill_product_info` 在正确商品信息页时 `precheck` 返回 `ok`，不再误杀。
2. 缺失模板不会导致流程报错，系统会自动切换到降级判定链。
3. 计划数据能补齐商品信息页和相关分区的全部必填字段。
4. `fill_product_info` 能真实进入字段填写，而不是停在“识别并恢复”。
5. acceptance / live-run 有一轮完整证据，证明字段填写、详情图上传、发布前检查都能走通。
6. 代码结构和日志足够清晰，后续再出问题时能快速定位到具体分区、字段、判定链。

## 优先级任务

## P0-1 修 precheck 误杀

目标：

- 让“正确商品信息页”返回 `ok`，而不是 `error`。

范围：

- `actions/form.py`
- 与 `doc_strict precheck`、页面状态分类、视觉结论解析相关的调用链

要做：

- 对齐“视觉描述已确认安全继续”与 `status/state` 的最终映射规则。
- 区分三类状态：
  - 真错页：必须恢复
  - 真正页：直接放行
  - 不确定页：允许进入降级确认链，而不是直接失败
- 把 `unknown` 从“硬失败”改成“条件性二次确认”。

完成标准：

- 对本次样本页面，`precheck` 不再报错。
- 新增测试覆盖“自然语言确认正确页但结构化状态为 unknown”的放行场景。

## P0-2 补模板或做降级

目标：

- `product_title_label.png / market_price_label.png / jd_price_label.png` 缺失时，流程仍能继续。

范围：

- 模板资源目录
- `fill_product_info` 页确认逻辑

要做：

- 先检查是否已有可生成模板的稳定截图来源。
- 若可生成，则补齐轻量模板。
- 若模板仍不可靠，则降级为弱信号链：
  - `market_input=True`
  - `jd_input=True`
  - `sku_batch=True`
  - 页面标题/区块标题
  - 星号字段数量
- 允许“模板缺失但结构足够像商品信息页”时继续执行。

完成标准：

- 日志中不再因为这 3 个模板缺失直接中断。
- 新增测试覆盖“模板缺失但弱信号充分”的放行场景。

## P0-3 补字段生成

目标：

- 让计划数据覆盖商品信息页、SKU、物流、售后、详情图上传的必填字段。

范围：

- 计划生成与数据补全过程
- `cli.py`
- 抓取/补全逻辑相关模块

以 `data/acceptance-runs/acceptance-20260513-162532-a6122f/caa0589c.json` 为样本，重点补齐：

- 商品基本信息
  - 商品标题
  - 品牌
  - 型号
  - 孔型配置
  - 额定电压
  - 电缆长度
  - 防护等级
  - 极数
- SKU 基本信息
  - 电流
  - 电流顺序
  - 商品名称
  - 短标题
  - 市场价
  - 采购价
  - 京东价
  - 毛利
  - SKU 属性
  - 重量
  - 长
  - 宽
  - 高
- 图片
  - 主图设置
  - SKU 方图
  - SKU 透图
  - 商品详情图上传
- 物流与其他
  - 保质期(天)
  - 商品包装
  - 销售单位
  - 特殊发货时效标记
  - 包装清单
  - 质保期

补全策略：

- 优先使用爬取数据。
- 爬取缺失时，从标题、品牌、类目、主图、详情图、规格文本中推理。
- 推理结果必须带来源说明或补全原因，便于回溯。

完成标准：

- 生成后的 product payload 不再出现明显脏值。
- 对上述必填字段给出“已填 / 推理填 / 仍缺失”的结构化报告。

## P0-4 建立截图驱动的组件识别与交互计划

目标：

- 不再把所有表单字段都当成“找文字后点击再输入”。
- 基于截图视觉识别，把商品信息页各分区的表单组件类型分析清楚，再生成对应交互动作。

范围：

- 计划生成层
- `fill_product_info` 分区执行层
- SKU 表格区域的视觉与交互策略

要做：

- 为每个字段增加 `component_type` 与 `interaction_strategy`。
- 至少支持以下组件类型：
  - `text_input`
  - `textarea`
  - `dropdown_single`
  - `dropdown_searchable`
  - `radio_group`
  - `checkbox_group`
  - `image_uploader`
  - `table_cell_input`
  - `table_cell_dropdown`
  - `scrollable_table`
- 为每种组件定义标准动作链，而不是运行时临时猜。

字段级动作规范：

- 商品名称这类输入框：
  - 识别为 `text_input`
  - 动作为点击输入框
  - 校验焦点进入后直接输入
  - 输入后做回读校验
- 品牌这类下拉框：
  - 识别为 `dropdown_single` 或 `dropdown_searchable`
  - 动作为点击下拉框
  - 等待下拉面板出现
  - 优先使用鼠标移动到目标值上悬浮后点击
  - 若鼠标方案不稳定，则退回键盘 `ArrowDown` 定位后 `Enter` 确认
  - 选择后做值回读校验
- 销售属性中的 SKU 基本信息表格：
  - 识别为 `scrollable_table`
  - 要求能识别表格存在左右滑动
  - 为每一列记录“当前可见 / 需横向滚动后可见”
  - 横向滚动后再执行单元格输入或下拉选择
  - 对表格列头和单元格值分别做定位校验

建议先建立组件映射清单：

- 商品基本信息
  - 商品标题：输入框
  - 品牌：下拉框
  - 型号：输入框
  - 其他属性：输入框 / 下拉框 / 单选组，按截图识别归类
- 价格与采销
  - 市场价、采购价、京东价：输入框
- 销售属性
  - SKU 基本信息：可横向滚动表格
  - SKU 图片信息：图片上传控件
- 商品描述
  - 详情图：图片上传控件
- 物流与售后
  - 保质期、销售单位、包装清单、质保期等：输入框 / 下拉框 / 文本域

计划输出要求：

- 在计划步骤里显式写出：
  - 字段名
  - 组件类型
  - 动作链
  - 备选动作链
  - 成功校验方式
- 不允许再只写“填写品牌”“填写 SKU 信息”这类粗粒度动作。

完成标准：

- 同一字段在计划中能明确看出应该“输入”“选择”“上传”还是“滚动表格后再编辑”。
- 品牌下拉选择和 SKU 横向滚动表格都有明确的执行预案。
- 新增测试或夹具，验证计划生成结果中已包含 `component_type` 和 `interaction_strategy`。

## P1-1 完善日志与追溯

目标：

- 一眼看出失败发生在哪个分区、哪个字段、哪条判定链。

范围：

- `actions/form.py`
- 执行器日志

要做：

- 为每个分区输出统一日志前缀：
  - `basic_info`
  - `procurement_pricing`
  - `product_attributes`
  - `sales_attributes`
  - `sku_images`
  - `description`
  - `logistics`
  - `after_sale_other`
- 对 `precheck / page_state / template / fallback / field_fill` 增加结构化日志。
- 明确记录：
  - 进入哪个分区
  - 放行依据
  - 缺字段列表
  - 跳过原因
  - 恢复动作

完成标准：

- 一份日志足以定位失败分区和字段，不必再靠人工读整段自然语言。

## P1-2 拆分 actions/form.py

目标：

- 降低 `actions/form.py` 的复杂度，把逻辑按表单模块拆开。

建议拆分：

- `actions/form_basic_info.py`
- `actions/form_procurement_pricing.py`
- `actions/form_product_attributes.py`
- `actions/form_sales_attributes.py`
- `actions/form_description.py`
- `actions/form_logistics.py`
- `actions/form_after_sale_other.py`

要求：

- 先抽公共上下文和日志工具，再拆各分区动作。
- 保留旧入口，避免一次性大爆炸重构。

完成标准：

- `actions/form.py` 只保留编排层和公共工具。
- 各分区逻辑可以独立测试。

## P2-1 实机验收闭环

目标：

- 证明系统不仅会“识别并恢复”，而且会“继续执行并完成”。

验收命令：

```powershell
python -m cli acceptance-run --file "湖南上架表格.xlsx" --start-from-phase product_info_ready
```

通过标准：

- `fill_product_info` 不再死于 `precheck`
- 日志进入真实字段填写
- 至少覆盖：
  - 基础信息
  - 价格
  - SKU
  - 物流/售后
  - 商品描述图片上传
- 生成新的日志、截图、acceptance 产物，且失败从“预检误杀”转移到更细字段层，或直接成功

## 建议执行顺序

1. `P0-1` 修 `precheck` 误杀
2. `P0-2` 模板降级或补齐
3. `P0-3` 字段生成补全
4. `P0-4` 建立组件识别与交互计划
5. `P1-1` 统一日志
6. `P1-2` 拆分 `actions/form.py`
7. `P2-1` 跑 acceptance 实机验收

## 当前判断

最先该做的不是坐标优化，而是：

- 让正确页面先能放行
- 让模板缺失不再把流程挡死
- 让 product payload 足够完整，避免刚放行就因为字段缺失再次失败

这三件做完，分数才有机会从 `64` 拉到 `85+`。  
实机 acceptance 再走通一轮，才有资格报 `100`。
