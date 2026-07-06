from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

def add_title_slide(prs, title, subtitle="", date=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    txBox = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11.333), Inches(1.5))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(54)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER
    if subtitle:
        txBox2 = slide.shapes.add_textbox(Inches(1), Inches(4), Inches(11.333), Inches(1))
        tf2 = txBox2.text_frame
        p2 = tf2.paragraphs[0]
        p2.text = subtitle
        p2.font.size = Pt(28)
        p2.alignment = PP_ALIGN.CENTER
    if date:
        txBox3 = slide.shapes.add_textbox(Inches(1), Inches(5.5), Inches(11.333), Inches(0.5))
        tf3 = txBox3.text_frame
        p3 = tf3.paragraphs[0]
        p3.text = date
        p3.font.size = Pt(18)
        p3.alignment = PP_ALIGN.CENTER
    return slide

def add_content_slide(prs, title, bullets):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.333), Inches(0.8))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.bold = True
    txBox2 = slide.shapes.add_textbox(Inches(0.7), Inches(1.3), Inches(12), Inches(5.5))
    tf2 = txBox2.text_frame
    tf2.word_wrap = True
    for i, bullet in enumerate(bullets):
        if i == 0:
            p = tf2.paragraphs[0]
        else:
            p = tf2.add_paragraph()
        p.text = bullet
        p.font.size = Pt(22)
        p.space_after = Pt(10)
    return slide

def add_two_column_slide(prs, title, left_title, left_items, right_title, right_items):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.333), Inches(0.8))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.bold = True
    # Left
    left_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(6), Inches(5.8))
    lf = left_box.text_frame
    lf.word_wrap = True
    lp = lf.paragraphs[0]
    lp.text = left_title
    lp.font.size = Pt(24)
    lp.font.bold = True
    for item in left_items:
        pp = lf.add_paragraph()
        pp.text = "• " + item
        pp.font.size = Pt(20)
        pp.space_after = Pt(8)
    # Right
    right_box = slide.shapes.add_textbox(Inches(6.8), Inches(1.2), Inches(6), Inches(5.8))
    rf = right_box.text_frame
    rf.word_wrap = True
    rp = rf.paragraphs[0]
    rp.text = right_title
    rp.font.size = Pt(24)
    rp.font.bold = True
    for item in right_items:
        pp = rf.add_paragraph()
        pp.text = "• " + item
        pp.font.size = Pt(20)
        pp.space_after = Pt(8)
    return slide

def add_table_slide(prs, title, headers, rows):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.333), Inches(0.8))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.bold = True
    num_rows = len(rows) + 1
    num_cols = len(headers)
    table = slide.shapes.add_table(num_rows, num_cols, Inches(0.5), Inches(1.3), Inches(12.333), Inches(5)).table
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        cell.text_frame.paragraphs[0].font.size = Pt(20)
        cell.text_frame.paragraphs[0].font.bold = True
    for row_idx, row in enumerate(rows):
        for col_idx, cell_text in enumerate(row):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = cell_text
            cell.text_frame.paragraphs[0].font.size = Pt(18)
    return slide

# ===== SLIDE 1: Title =====
add_title_slide(prs, "华人清洗分销系统", "技术团队 & 成功案例展示", "2026年5月27日 · 客户会议专用")

# ===== SLIDE 2: TOC =====
add_content_slide(prs, "目录", [
    "一、项目体验 — 多商户分销系统在线演示",
    "二、技术团队介绍 — 农场认养小鸡商城项目经验",
    "三、系统架构 — 分销角色体系、商品规则、关系绑定",
    "四、奖励体系 — 直推奖、对碰奖、代数奖、滑落奖、职级分红",
    "五、API对接 — 对接系统、数据交互方式",
    "六、核心卖点总结"
])

# ===== SLIDE 3: Project Demo =====
add_content_slide(prs, "项目体验 — 多商户分销系统", [
    "【后台管理系统】http://0626tbcs.ohlegend.com/admin/dashboard",
    "  账号：admin  密码：admin888",
    "【商户端】http://0626tbcs.ohlegend.com/merchant/login",
    "  商户：13000000000  密码：123456",
    "【前端页面】http://0626tbcs.ohlegend.com/",
    "  功能：商户入驻 / 品牌好店 / 积分商城 / 推广中心"
])

# ===== SLIDE 4: Team Introduction =====
add_two_column_slide(prs, "技术团队介绍",
    "核心项目经验", [
        "农场认养小鸡商城（2011-2022）",
        "项目周期：超11年持续迭代",
        "担任职位：PHP技术组长",
        "项目规模：分销电商上链平台",
        "用户激活：沉淀用户拓展互动情节"
    ],
    "技术架构能力", [
        "Hyperf 协程框架",
        "MySQL8 + Redis + MongoDB",
        "RabbitMQ 消息队列",
        "ElasticSearch 搜索引擎",
        "Docker 微服务架构"
    ]
)

# ===== SLIDE 5: Case Study =====
add_content_slide(prs, "成功案例：农场认养小鸡商城", [
    "【项目背景】类似支付宝芭芭农场的游戏化电商平台",
    "【核心玩法】用户认养小鸡，每天产蛋获取收益",
    "【商业模式】三级分销体系，实现用户裂变",
    "【技术亮点】区块链上链 + 多Java项目数据打通",
    "【项目成果】超11年持续运营，沉淀用户激活"
])

# ===== SLIDE 6: Distribution Roles =====
add_two_column_slide(prs, "分销角色体系",
    "对内角色", [
        "SU 销售经理 — 内部管理人员",
        "BU 合伙人 — 初级合伙人，可发展N级"
    ],
    "对外角色", [
        "BU 合伙人（外部）— 外部合作伙伴",
        "N级分销商 — 无限裂变层级"
    ]
)

# ===== SLIDE 7: Products =====
add_content_slide(prs, "分销商品规则", [
    "分销商品由后台统一录入业绩订单",
    "系统根据订单及分销规则自动分配业绩",
    "确保公平透明，避免人工分配争议"
])

# ===== SLIDE 8: Binding Rules =====
add_content_slide(prs, "关系绑定规则（核心机制）", [
    "邀请绑定：分享链接/二维码邀请，自动绑定上下级",
    "主线限制：每个用户下方仅允许2条主线（左线+右线）",
    "自动滑落：第3个及以上被推荐人自动滑落至最深空位",
    "双重绑定：拉新用户自动绑定推荐人和安置上线"
])

# ===== SLIDE 9: Direct Push Award =====
add_two_column_slide(prs, "奖励体系 — 直推奖",
    "首年利润", ["裂变1个BU，获得首年利润5%"],
    "次年收益", ["首年后持续获得2%收益"]
)

# ===== SLIDE 10: Matching Award =====
add_content_slide(prs, "奖励体系 — 对碰奖", [
    "左右平衡时触发对碰奖",
    "左右两区业绩对碰，获得小区业绩2%",
    "由直推人获取该奖励利润"
])

# ===== SLIDE 11: Generation Award Table =====
add_table_slide(prs, "奖励体系 — 代数奖（级差奖）",
    ["代数范围", "奖励比例", "说明"],
    [
        ["1-10 代", "1%", "无限代分润起点"],
        ["11-20 代", "0.5%", "递减少法"],
        ["21代后", "0.2%", "始终留存40%"]
    ]
)

# ===== SLIDE 12: Guarantees =====
add_content_slide(prs, "代数奖保障机制", [
    "40% 留存机制 — 系统始终留存40%，保证分配",
    "最小分润值 1元 — 低于1元累积到下次，永远能分到钱"
])

# ===== SLIDE 13: Slip & Position =====
add_two_column_slide(prs, "滑落奖 & 职级分红",
    "滑落奖（被动收入）", [
        "上面掉人也赚钱",
        "识别推荐人是他人但安置在自己树下的节点",
        "计算其首年利润×1%"
    ],
    "职级分红（奖金池）", [
        "白金：奖金池10%",
        "钻石：奖金池20%",
        "总统钻石：奖金池30%"
    ]
)

# ===== SLIDE 14: API =====
add_two_column_slide(prs, "API对接说明",
    "对接系统", [
        "项目管理系统",
        "有成报销（付款管理）",
        "单据管理系统"
    ],
    "交互数据", [
        "客户信息",
        "项目名称",
        "项目编号"
    ]
)

# ===== SLIDE 15: Selling Points =====
add_content_slide(prs, "核心卖点（会议强调重点）", [
    "11年分销系统经验 — 团队成熟，项目可实地体验",
    "无限代裂变 — 真正的管道收入，团队越大收益越高",
    "两条主线+自动滑落 — 公平均衡的网络结构",
    "40%留存机制 — 永远不会被分不到钱",
    "API无缝对接 — 不影响现有系统"
])

# ===== SLIDE 16: Thank You =====
add_title_slide(prs, "谢谢观看", "华人清洗分销系统 · 技术团队 & 案例展示", "了解更多请联系项目负责人")

prs.save(r'E:\workspace\华人清洗分销系统-案例展示.pptx')
print("✅ PPT已生成: E:\\workspace\\华人清洗分销系统-案例展示.pptx")
