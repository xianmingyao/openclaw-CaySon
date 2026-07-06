# 行动手册 v2：row8 公牛 GN-806DN 50米带漏保+3*2.5
# 触发：D1=是 且 D2=已前台 且 D3=路径或"无图版" 且 D4=电线长度 且 D5=库存
# 中止：你说"停" / 前台不再是京麦 / 任一动作坐标落到发布按钮禁区 [1260,1370]x[1320,1405]

## 工具栈
- PowerShell 7 + .NET Win32 P/Invoke（前台检查、坐标、剪贴板、GetWindowRect）
- System.Drawing（截图）
- jm-ufo-agent CLI（dashboard / inspect-jingmai-window / capture-halt-evidence）

## 截图命名
artifacts/2026-06-11-row8/evidence/E01_baseline.png  ← 草稿箱状态
artifacts/2026-06-11-row8/evidence/E02_after_publish_click.png  ← +发布商品 后
artifacts/2026-06-11-row8/evidence/E03_category_page.png  ← /categorySelect
artifacts/2026-06-11-row8/evidence/E04_search_input.png  ← 输入"插座"
artifacts/2026-06-11-row8/evidence/E05_selected.png  ← 已选类目出现
artifacts/2026-06-11-row8/evidence/E06_form_basic_filled.png  ← 基础信息完
artifacts/2026-06-11-row8/evidence/E07_detail_filled.png  ← 图文详情完
artifacts/2026-06-11-row8/evidence/E08_logistics_filled.png  ← 物流售后完
artifacts/2026-06-11-row8/evidence/E09_sku_filled.png  ← SKU 完
artifacts/2026-06-11-row8/evidence/E10_after_save_draft.png  ← 点保存草稿后
artifacts/2026-06-11-row8/evidence/E11_draft_box_verify.png  ← 草稿箱核对

## 步骤（每步前都先前台检查）
E1  前台检查：HWND 标题含 jd_465d1abd3ee76。截图 E01。
E2  草稿箱核对：基线状态截图，确认 row5/6/7 在草稿箱第一/二/三条。
E3  点击 +发布商品  → 坐标 (2160, 174)
E4  类目搜索框  → 坐标 (1280, 230)
E5  输入"插座"  → 剪贴板粘贴
E6  点搜索结果  → 坐标 (744, 270)
    验证：页面出现"已选类目：工业品 > 中低压配电 > 插座"
E7  下一步  → 坐标 (1280, 1314)
    验证：URL 进入 vcProductPublish
E8  填基础信息
    标题：剪贴板粘贴完整标题
    品牌：搜"公牛（BULL）"，点候选项
    型号：粘贴"GN-806DN"
    市场价：1449.41
    京东价：1232
    采购价：1170.4
    孔型配置：16A
    额定电压：250V
    电线长度：D4 选项
    极数：2P+E
E9  切图文编辑 → 添加文本 → 文本编辑框粘贴详情
    验证：已添加 1/50张 + 右侧预览有文字
E10 物流售后
    保质期 365
    销售单位 搜"个"，点候选项
    包装规格 1
    包装规格单位 个
    商品包装 普通商品
    危险品 不勾
    质保期 1年质保
    发货时效 普通品
    包装清单 粘贴"电缆盘*1"
E11 SKU 行
    商品名：粘贴
    SKU 属性 → 弹窗配置（孔型/电压/线长）
    厂直库存 D5
    短标题：粘贴"公牛GN-806DN电缆盘50米"
    货号：GN-806DN-50M-3X2.5
    横向滚动到尺寸/重量
    长 100 宽 100 高 100 重 12.3
    图片设置（仅当 D3 提供路径时）
E12 保存草稿  → 坐标 (1424, 1361)
    **绝不点击 (1315, 1361) 左侧发布商品**
    **绝不进入发布按钮禁区 [1260,1370] x [1320,1405]**
E13 草稿箱核对  → 第一行标题匹配 + 编码出现 + 编辑时间为本次
E14 更新 live state
    data/live_runs/jingmai_autonomous_state.json 添加 "8": {"status": "draft_saved", ...}

## 中止
你说"停"  → 立即停止
HWND 标题不再是 jd_465d1abd3ee76  → 立即停止
主图缺位 + SKU 红字阻断  → 截图 + 报告 + 等你授权
库存 = 0 阻断保存  → 截图 + 报告 + 等你授权
