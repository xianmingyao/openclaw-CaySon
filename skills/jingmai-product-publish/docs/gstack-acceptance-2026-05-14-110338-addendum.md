# gstack Acceptance Addendum 2026-05-14 11:03

## 本轮结论

基于以下实机证据：
- [summary.json](E:/workspace/skills/jingmai-product-publish/data/acceptance-runs/acceptance-20260514-110338-a0314f/summary.json)
- [publish_20260514_110345.log](E:/workspace/skills/jingmai-product-publish/logs/publish_20260514_110345.log)
- [precheck_contact_sheet.png](E:/workspace/skills/jingmai-product-publish/resources/screenshots/video-observer/9c4a94ac/step-05-fill_product_info/precheck_contact_sheet.png)
- [recovery_contact_sheet.png](E:/workspace/skills/jingmai-product-publish/resources/screenshots/video-observer/9c4a94ac/step-05-recovery_fill_product_info_1/recovery_contact_sheet.png)

本轮失败点已经前移：

- 不是“正确商品信息页被 `fill_product_info` 误杀”
- 而是系统从 `product_info_ready` 断点续跑时，真实页面仍停在 `categorySelect / 类目选择发品`
- 因此 `fill_product_info` 报 `still on category selection page` 是正确拦截

## 实机证据

日志反复出现：

- `category page detected before restore`
- `still on category selection page; select_category must complete before fill_product_info`

视频观察显示：

- `precheck / recovery / postcheck` 三段都停在 `.../categorySelect`
- 页面主体始终是类目面板和“下一步，完善其他商品信息”按钮
- 没有进入商品基础信息表单页

## 当前评分

我给当前完成度 **58/100**。

分项：
- 错页识别：`88/100`
- 正确页放行：`72/100`
- 断点续跑 phase 一致性：`25/100`
- 实机闭环推进度：`20/100`
- 综合：`58/100`

这次比上一轮低，不是回退，而是暴露了更前置的新阻塞：
- 之前主要卡在 step 5 内部误杀
- 现在主阻塞已经变成 step 5 之前的 phase gating 不成立

## 新的 gstack 优先级

### P0-0 修断点续跑 phase gating

目标：
- `--start-from-phase product_info_ready` 只能在真实页面已进入商品基础信息页时生效
- 若真实页面仍是 `category_page`，必须自动回补 `select_category`

要做：
- 在 `resume-preflight` 后增加 phase gate
- `page_state=product_info_page` 才允许进入 `fill_product_info`
- `page_state=category_page` 时自动回退执行 `select_category`
- `page_state=unknown` 时先做滚动截图复核，再决定回退还是继续

完成标准：
- 不再出现“真实还在类目页，却直接进入 step 5”

### P0-0A 修 product_info_ready 到达判据

目标：
- 只有真正进入商品基础信息填写页，才允许把 phase 标成 `product_info_ready`

要做：
- 收紧 `select_category` 和 `navigate_to` 的 postcheck
- 不能只靠“类目路径存在”或“下一步按钮存在”就判 ready
- 必须看到商品基础信息页结构：
  - 商品标题/品牌/型号
  - 或商品信息页分区结构

完成标准：
- phase 标记与真实页面一致

### P0-1 保留滚动截图复核优先

说明：
- 上一轮修复方向仍然有效
- 一旦真实页面已经进入商品信息页，仍然要优先用滚动截图复核放行
- `precheck.status=ok` 继续只做兜底，不可覆盖 phase gate

## 下一步执行顺序

1. 修 `resume-preflight` 的真实页面 phase gate
2. 修 `select_category -> product_info_ready` 的到达判据
3. 重跑 acceptance，确认 step 5 前已经真正进入商品信息页
4. 再继续追 `fill_product_info` 内部字段填写稳定性
