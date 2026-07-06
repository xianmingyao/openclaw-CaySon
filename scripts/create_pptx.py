from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

def add_title_slide(prs, title, subtitle="", date=""):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    # Title
    txBox = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11.333), Inches(1.5))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(54)
    p.font.bold = True
    p.alignment = PP_ALIGN.CENTER
    # Subtitle
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
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank
    # Title
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.333), Inches(0.8))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.bold = True
    # Content
    txBox2 = slide.shapes.add_textbox(Inches(0.7), Inches(1.3), Inches(12), Inches(5.5))
    tf2 = txBox2.text_frame
    tf2.word_wrap = True
    for i, bullet in enumerate(bullets):
        if i == 0:
            p = tf2.paragraphs[0]
        else:
            p = tf2.add_paragraph()
        p.text = "• " + bullet
        p.font.size = Pt(24)
        p.space_after = Pt(12)
    return slide

def add_two_column_slide(prs, title, left_title, left_items, right_title, right_items):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    # Title
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.333), Inches(0.8))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.bold = True
    # Left column
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
    # Right column
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
    # Title
    txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12.333), Inches(0.8))
    tf = txBox.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.bold = True
    # Table
    num_rows = len(rows) + 1
    num_cols = len(headers)
    table = slide.shapes.add_table(num_rows, num_cols, Inches(0.5), Inches(1.3), Inches(12.333), Inches(5)).table
    # Header
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        cell.text_frame.paragraphs[0].font.size = Pt(20)
        cell.text_frame.paragraphs[0].font.bold = True
    # Rows
    for row_idx, row in enumerate(rows):
        for col_idx, cell_text in enumerate(row):
            cell = table.cell(row_idx + 1, col_idx)
            cell.text = cell_text
            cell.text_frame.paragraphs[0].font.size = Pt(18)
    return slide

# Slide 1: Title
add_title_slide(prs, "华人清洗分销系统", "案例展示 & 需求分析", "2026年5月27日 · 客户会议专用")

# Slide 2: Table of Contents
add_content_slide(prs, "目录", [
    "一、系统架构 — 分销角色体系、分销商品规则、关系绑定流程",
    "二、奖励体系 — 直推奖、对碰奖、代数奖、滑落奖、职级分红",
    "三、API对接 — 对接系统范围、数据交互方式、接口文档",
    "四、会议目标 — 确认需求细节、解答客户疑问、达成合作共识"
])

# Slide 3: Distribution Roles
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

# Slide 4: Distribution Products
add_content_slide(prs, "分销商品规则", [
    "分销商品由后台统一录入业绩订单",
    "系统根据订单及分销规则自动分配业绩",
    "确保公平透明，避免人工分配争议"
])

# Slide 5: Relationship Binding
add_content_slide(prs, "关系绑定规则（核心机制）", [
    "邀请绑定：分享链接/二维码邀请，自动绑定上下级",
    "主线限制：每个用户下方仅允许2条主线（左线+右线）",
    "自动滑落：第3个及以上被推荐人自动滑落至最深空位",
    '双重绑定：拉新用户自动绑定推荐人和安置上线'
])

# Slide 6: Direct Push Award
add_two_column_slide(prs, "奖励体系 — 直推奖",
    "首年利润", ["裂变1个BU，获得首年利润5%"],
    "次年收益", ["首年后持续获得2%收益"]
)

# Slide 7: Matching Award
add_content_slide(prs, "奖励体系 — 对碰奖", [
    "左右平衡时触发对碰奖",
    "左右两区业绩对碰，获得小区业绩2%",
    "由直推人获取该奖励利润"
])

# Slide 8: Generation Award
add_table_slide(prs, "奖励体系 — 代数奖（级差奖）",
    ["代数范围", "奖励比例", "说明"],
    [
        ["1-10 代", "1%", "无限代分润起点"],
        ["11-20 代", "0.5%", "递减少法"],
        ["21代后", "0.2%", "始终留存40%"]
    ]
)

# Slide 9: Key Guarantees
add_content_slide(prs, "代数奖保障机制", [
    "40% 留存机制 — 系统始终留存40%，保证分配",
    "最小分润值 1元 — 低于1元累积到下次，永远能分到钱"
])

# Slide 10: Slip Award & Position Dividend
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

# Slide 11: API Integration
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

# Slide 12: Key Selling Points
add_content_slide(prs, "核心卖点（会议强调重点）", [
    "无限代裂变 — 真正的管道收入，团队越大收益越高",
    "两条主线+自动滑落 — 公平均衡的网络结构",
    "40%留存机制 — 永远不会被分不到钱",
    "被动收入 — 滑落奖实现真正躺赚",
    "API无缝对接 — 不影响现有系统"
])

# Slide 13: Thank You
add_title_slide(prs, "谢谢观看", "华人清洗分销系统 · 案例展示", "📞 了解更多请联系项目负责人")

prs.save(r'E:\workspace\华人清洗分销系统-案例展示.pptx')
print("✅ PPT文件已生成: E:\\workspace\\华人清洗分销系统-案例展示.pptx")
