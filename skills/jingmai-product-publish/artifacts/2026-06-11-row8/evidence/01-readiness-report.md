# 2026-06-11 row8 上架准备度评估报告
# 数据源：5 个只读命令 + 截图视觉验证 + live state + 字段计算
# 用户指令：选项 5 = 纯只读证据采集（不触碰京麦任何按钮/输入/文件框）

============================================================
A. 执行了哪些只读命令（5 个，全部不触碰京麦）
============================================================
1. jm-ufo-agent inspect-ufo --ufo-root E:\PY\UFO\ufo          ✓
2. jm-ufo-agent inspect-jingmai-window                        ✓
3. jm-ufo-agent production-readiness --capabilities-json ...  ✓
4. jm-ufo-agent mysql-preflight --env-file .env              ✓ (缺 asyncmy)
5. jm-ufo-agent minimax-preflight --env-file .env            ✓ (MiniMax-M3 可用)
6. jm-ufo-agent capture-halt-evidence --use-tesseract        ✓ (截图存证)
7. jm-ufo-agent run --backend ufo-observe (干跑 row8)         ✗ PermissionError（需 --confirm-real-jingmai）

============================================================
B. 核心发现
============================================================
B1. UFO 源码就绪
    - E:\PY\UFO\ufo 7 个核心模块全在（action_execution, controller, inspector 等）
    - ready_for_observe: true
    - ready_for_write: true（理论可写，webview-act 白名单）

B2. 京麦窗口事实（与之前对比：5 pane → 3 pane）
    - main_class_name: Qt51511QWindowIcon
    - main_title: jd_465d1abd3ee76
    - html_button_count: 0 / html_edit_count: 0 / html_combobox_count: 0
      → WebView 内部 HTML 控件**不暴露 UIA**（runbook 验证的硬事实）
    - qt_child_count: 35（之前 42）
    - webview_pane_count: 3（之前 5）—— 页面状态变化

B3. 生产就绪度（8 项能力缺 7 项）
    - available: ["parse_excel"]
    - missing: [crawl_jd, download_images, transform_images, check_jingmai_login,
              open_add_product_page, fill_webview_form, save_draft, verify_draft_readback]
    - ready: false
    注：open_add_product_page 缺失但截图显示京麦**已在该页**——是用户手动开的，不是 agent 开的。
        fill_webview_form/save_draft 缺失意味着即便用 webview-act backend 也只能由 PyAutoGui
        真实模拟点击，agent 自身**没有**Verified Action Ladder 编排。

B4. MySQL 预检
    - ok: false
    - error: "缺少 asyncmy，无法连接 MySQL"
    影响：当前无法写 MySQL 持久化；MySQL 是 storage 可选依赖（pip install -e .[storage]）
    对 row8 影响：**只读采集**不需要 MySQL；**真实保存草稿**不需要 MySQL（草稿存在京麦服务端）

B5. MiniMax 预检
    - ok: true
    - model_available: MiniMax-M3
    - provider: minimax
    - base_url: https://api.minimaxi.com/anthropic
    影响：评审模型可用；如果走"webview-act 真实跑通"流程，MiniMax-M3 可做字段评审

============================================================
C. 截图视觉验证（最关键）
============================================================
C1. URL: https://wares-jdm.jd.com/vcProductPublish/?publishPageType=1&locType=0&categoryId=149578&uuid=83f98cef-12af-45de-a697-9772357e666a
C2. 页面状态：vcProductPublish（商品发布表单）
C3. 类目已选：工业品 > 中低压配电 > 插座（categoryId=149578）
C4. 当前 UUID：83f98cef-12af-45de-a697-9772357e666a
C5. 关键 UI：
    - 顶部：基本信息 / 图文详情 / 物流售后及其他 / 规格描述 四个 Tab
    - 必填红星：商品标题 *、品牌 *、型号 *、采购员 *、销售员 *、市场价(元) *、京东价(元) *、采购价(元) *
    - 采购员/销售员已预填：赵林(zhaolin125)
    - 商品属性：孔型配置 *、额定电压 *、电线长度 *、极数（无红星）
    - 图文详情：商品详情 / 图文编辑(推荐) / 代码编辑 / 高级编辑（已选"高级编辑"！）
      **注意**：截图显示**当前选的是"高级编辑"而非"图文编辑"——这与 runbook L196-208 强调的"切到图文编辑"冲突**
    - 物流售后：保质期(天) *、销售单位 *、包装规格 *、包装规格单位、商品包装 *、是否危险商品 *、质保期 *、特殊发货时效标记 *
    - 右下角：发布商品（蓝）+ 保存草稿（蓝带下拉箭头）两个按钮

C6. ⚠️ 重要警告：
    - 京麦当前打开的是**空表单**（所有输入框空）
    - 但 runbook L13 明确："多行 Excel 批量上架时，每一行商品都要从 +发布商品 新建流程开始"
    - **如果我直接填这个空表单** = 跳过 row8 的"类目搜索→选→下一步"流程，但**会填到 row4/5/6/7 留的会话里**（除非这是用户刚才为 row8 新开的）
    - 建议：先回草稿箱关闭这个会话，从草稿箱 +发布商品 新建（runbook 严令）

C7. OCR 失败（tesseract 未装）
    - TesseractNotFoundError
    - 影响：截图中**文字无法 OCR 提取**（runbook L170-183 字段填写需要 OCR 验证读回）
    - 缓解：可以用 VLM（如 MiniMax-M3 多模态）替代，或安装 tesseract（pip install pytesseract + 系统包 tesseract-ocr）

============================================================
D. row8 完整字段补全（再校核 + live state 状态）
============================================================
D1. 数据源：公牛上架.xlsx 第 8 行
    - 标题：GN-806DN线盘移动电缆盘电线卷线盘30米公牛带漏保工程地拖绕线盘拖线盘50米线轴卷盘排插接线插座 806DN带漏保+3*2.5 50米
    - 品牌：公牛
    - 型号：GN-806DN
    - 长宽高：100x100x100 mm
    - 重量：12.3 kg
    - 单位：个
    - 京东价：1232
    - 京东链接：item.jd.com/10220710592600.html
    - 备注：数量 0

D2. 价格公式（autonomous L181-183）
    - 市场价 = 1232 / 0.85 = 1449.41
    - 采购价 = 1232 * 0.95 = 1170.4

D3. 平台枚举（autonomous L161-170 + row5/6/7 实战）
    - 孔型配置：16A
    - 额定电压：250V
    - 电线长度：6米（row8 真实 50米，平台枚举无）— D4 待确认
    - 极数：2P+E
    - 销售单位：套（autonomous）但 row4 实战用"个"——搜平台枚举
    - 商品包装：普通商品
    - 质保期：1年质保
    - 发货时效：普通品
    - 危险品：不勾

D4. ⚠️ 库存
    - Excel 备注"数量 0"——保存草稿可能红字
    - 实际业务 row5/6/7 库存都是 1
    - row8 库存 = 0 是异常，需要你显式确认

D5. live state 状态
    - task_id: T001
    - row_index: 4（不是 8！state 还没更新到 row8）
    - status: blocked
    - halt_node: FILL_AND_VERIFY_FIELDS
    - blockers: ["title: 必填字段为空"]
    - backend: ufo-observe
    - observe_only: true
    - root_cause: "jm-ufo-agent 的 production.py 硬编码了 observe_only 强制门控..."

============================================================
E. 当前是否可启动真实 row8 操作？
============================================================
E1. 阻塞矩阵
    [ ] D1 用户字面确认"是"           ❌ 3 次"开始"≠"是"
    [ ] D2 京麦切前台 + 登录 + 权限    ❌ 前台仍 Claude Code
    [ ] D3 主图本地路径 或"无图版"   ❌ 未提供
    [ ] D4 电线长度平台枚举           ❌ 未选
    [ ] D5 库存 = 0 还是其他数        ❌ 未确认
    [ ] MySQL 可连接（asyncmy）       ❌ 缺依赖
    [ ] OCR 可用（tesseract）         ❌ 缺系统包
    [ ] webview-act 真实跑通验证      ❌ 进度文件明示"未执行真实外部动作"

E2. 真实行操作的"打开新会话"问题
    - 当前京麦已在 vcProductPublish 空表单（UUID 83f98cef-12af-45de-a697-9772357e666a）
    - runbook L13 严令：每行商品都要从 +发布商品 新建流程开始
    - **直接填当前表单**：跳过了 row8 的类目搜索+选择步骤，但**会污染 row4/5/6/7 留的会话**
    - **正确做法**：先关闭当前表单 → 回草稿箱 → +发布商品 → 类目搜索"插座" → 选中 → 下一步 → 填表 → 保存草稿
    - **当前表单选的是"高级编辑"而非"图文编辑"**——runbook L196-208 明确图文编辑才能"已添加 1/50张"

E3. 假设"全用默认" + 接受 webview-act 风险的可行性
    - 接受：webview-act backend 真实跑通风险（PyAutoGui 真实点击）
    - 接受：库存=0（按 Excel）
    - 接受：电线长度=6米（用户授权）
    - 接受：主图"无图版"（SKU 红字风险）
    - 接受：图省事**直接填当前空表单**（跳过"先关再开"步骤）
    - 在上述全部接受情况下，技术上**可启动**，但：
      ① 坐标 (2160,174)/(1280,230)/(744,270)/(1280,1314)/(1424,1361) 是 2560x1440 校准
      ② 截图显示当前页就是 vcProductPublish（已选类目），可直接进入 E7 填基础信息
      ③ 但**未点击**当前位置，PyAutoGui 仍需从 (2160,174) 点 +发布商品——会跳到草稿箱
      ④ 实际操作会比 runbook 描述更复杂

============================================================
F. 建议下一步（按风险递增）
============================================================
F1. 最低风险（你已选 5，本轮结束）
    - 归档本报告
    - 等你重新评估

F2. 中等风险：先回草稿箱 + 关当前会话
    - 你手动点京麦切前台
    - 我**仍不**点京麦任何按钮
    - 我**只**做：inspect-jingmai-window 重新采集（确认当前空表单是否已关闭）

F3. 高风险：启动 webview-act 真实跑通 row8
    - 你需字面确认 D1=是 + D2=已前台 + D3-D5
    - 我会跑：run --backend webview-act --no-observe-only --confirm-real-jingmai
    - 风险：webview-act 真实未跑通；PyAutoGui.click 失败需手动接管

F4. 最高风险：完全信任 webview-act 跑通
    - 接受失败可手动介入
    - 接受"高 capital"风险（误点发布商品可能商品立即上线）
    - 需要你**全程在京麦前监督** + 出错立即喊停

============================================================
G. 截图存证
============================================================
artifacts/2026-06-11-row8/evidence/T001/row8_READ_ONLY_PROBE_ocr.png  ← 实际截图
artifacts/2026-06-11-row8/evidence/T001/row8_READ_ONLY_PROBE_halt_20260610T193611Z.json  ← 采集元数据
