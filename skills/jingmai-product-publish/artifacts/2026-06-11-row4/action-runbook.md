# 真实操作行动手册（row4 公牛 B5440）
# 触发条件：D1=是 且 D2=京麦已前台 且 D3=主图已提供 或 D3=无图版 且 D4=电线长度已选
# 中止条件：你随时说"停" / 前台不再是京麦 / 主图缺位（D3=无图版 但 SKU 红字阻断） / 编码与你期望不符

## 工具栈
- PowerShell 7 + .NET Win32 P/Invoke（前台检查、坐标、剪贴板、GetWindowRect）
- System.Drawing（截图）
- UFO action_execution.py（UIA click_text / set_edit_text / screenshot / clipboard）
- jm-ufo-agent CLI（dashboard / inspect-jingmai-window / capture-halt-evidence）

## 截图命名
artifacts/2026-06-11-row4/E01_baseline.png
artifacts/2026-06-11-row4/E02_after_publish_click.png
artifacts/2026-06-11-row4/E03_category_page.png
artifacts/2026-06-11-row4/E04_search_input.png
artifacts/2026-06-11-row4/E05_selected.png
artifacts/2026-06-11-row4/E06_form_basic_filled.png
artifacts/2026-06-11-row4/E07_detail_filled.png
artifacts/2026-06-11-row4/E08_logistics_filled.png
artifacts/2026-06-11-row4/E09_sku_filled.png
artifacts/2026-06-11-row4/E10_after_save_draft.png
artifacts/2026-06-11-row4/E11_draft_box_verify.png

## 步骤（每步前都先前台检查）
E1  前台检查：HWND 标题含 jd_465d1abd3ee76。截图 E01。
E2  点击 +发布商品  → /ware/categorySelect
    坐标 fallback（2560x1440）：(2160, 174)
    UIA 找 text=发布商品 失败时用坐标
E3  类目搜索框  → 坐标 (1280, 230)
    注：runbook L155 验证 (1280, 154) 实测太高
E4  输入"插座"  → 优先 Ctrl+V 粘贴
E5  点击搜索结果"插座"  → 坐标 (744, 270)
    验证：页面出现"已选类目：工业品 > 中低压配电 > 插座"
E6  点击下一步  → 坐标 (1280, 1314)
    验证：URL 进入 vcProductPublish
E7  填基础信息
    标题：剪贴板粘贴完整标题
    品牌：搜"公牛（BULL）"，点候选项
    型号：粘贴"无"
    市场价：82.35
    京东价：70
    采购价：66.5
    孔型配置：8位总控（下拉选）
    额定电压：250V（下拉选）
    电线长度：D4 选项
E8  切图文编辑 → 添加文本 → 文本编辑框粘贴详情
    验证：已添加 1/50张 + 右侧预览有文字
E9  物流售后
    保质期 365
    销售单位 搜"个"，点候选项
    包装规格 1
    包装规格单位 个
    商品包装 普通商品
    危险品 不勾
    质保期 1年质保
    发货时效 普通品
    包装清单 粘贴
E10 SKU 行
    商品名：粘贴
    SKU 属性 → 弹窗配置（孔型/电压/线长）
    厂直库存 2
    短标题：粘贴
    货号：B5440
    横向滚动到尺寸/重量
    长 250 宽 76 高 29 重 0.5
    图片设置（仅当 D3 提供路径时）
E11 保存草稿  → 坐标 (1424, 1448)（右侧草稿按钮）
    **绝不点击 (1315, 1448) 左侧发布商品**
E12 草稿箱核对  → 第一行标题匹配 + 编码出现 + 编辑时间为本次
    通过 10028205xxxx 编码或修改时间确证

## 中止
你说"停"  → 立即停止
HWND 标题不再是 jd_465d1abd3ee76  → 立即停止
主图缺位 + SKU 红字阻断  → 截图 + 报告 + 等你授权
