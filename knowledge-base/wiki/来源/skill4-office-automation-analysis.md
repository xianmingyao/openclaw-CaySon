# 技能4：Office-Automation 办公自动化深度分析

> 来源：`E:\workspace\skills\office\SKILL.md` 官方文档

---

## 🎯 这是什么（核心概念）

**Office-Automation = 办公软件自动化技能**

覆盖 Microsoft 365 / Google Workspace 全套办公软件，让 AI 能够：
- Excel/Sheets：公式、数据分析、自动化
- Word/Docs：文档处理、格式化、邮件合并
- PowerPoint/Slides：演示文稿自动化
- 办公室管理：采购、库存、供应商

```
┌─────────────────────────────────────────────────────────────┐
│                      AI Agent (大脑)                          │
├─────────────────────────────────────────────────────────────┤
│                  Office Automation                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │  Excel   │ │  Word    │ │ PPT/Key  │ │  Admin   │      │
│  │  表格    │ │  文档    │ │  演示    │ │  管理    │      │
│  │          │ │          │ │          │ │          │      │
│  │ VLOOKUP  │ │ Styles   │ │ Slide    │ │ 库存     │      │
│  │ 透视表   │ │ Mail     │ │ Master   │ │ 供应商   │      │
│  │ 宏       │ │ Merge    │ │ Animates │ │ 空间规划 │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 关键功能点

### 1. Excel / Google Sheets

#### 核心公式

| 公式 | 用途 | 示例 |
|------|------|------|
| `VLOOKUP` | 查找表中的值 | `=VLOOKUP(A1, 数据!A:B, 2, FALSE)` |
| `XLOOKUP` | 更灵活的查找 | `=XLOOKUP(A1, 数据!A:A, 数据!B:B)` |
| `SUMIF` | 条件求和 | `=SUMIF(A:A, "北京", B:B)` |
| `COUNTIF` | 条件计数 | `=COUNTIF(A:A, ">100")` |
| `INDEX/MATCH` | 灵活查找 | `=INDEX(B:B, MATCH(A1, C:C, 0))` |
| `IF` + `AND/OR` | 条件逻辑 | `=IF(AND(A1>60, B1>60), "及格", "不及格")` |

#### 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| VLOOKUP 返回 #N/A | 空格、数据类型不匹配 | 清除空格，检查数据类型 |
| 公式复制后失效 | 缺少 `$` 绝对引用 | 使用 `$A$1` |
| 日期排序错误 | 文本格式的日期 | 转换为日期格式 |
| 透视表不更新 | 数据源未刷新 | 右键 → 刷新 |

### 2. Word / Google Docs

#### 格式化核心

| 功能 | 操作 | 快捷 |
|------|------|------|
| 样式 | Home → Styles → 选择 | Ctrl+Alt+1/2/3 |
| 页码从第3页开始 | 插入分隔符 → 不同首页 → 编页码 | - |
| 不同节不同页眉 | 分节符 → 取消链接到前节 | - |

#### 邮件合并

```
准备数据源（Excel）→ Word → 邮件 → 开始邮件合并 → 信件
    ↓
插入合并域 → <<姓名>> <<地址>>
    ↓
预览结果 → 完成合并
```

### 3. PowerPoint / Google Slides

#### 专业基础

| 原则 | 说明 |
|------|------|
| 6x6 规则 | 最多 6 个要点，每点最多 6 词 |
| 一页一主题 | 一个想法一页 |
| Slide Master | 统一样式（视图 → 幻灯片母版） |

#### 动画技巧

| 类型 | 用途 | 建议 |
|------|------|------|
| Appear | 要点逐条出现 | 配合"单击" |
| Fade | 柔和过渡 | 适合图片 |
| Fly In | 强调 | 慎用，避免花哨 |

**快捷键：**
- `F5` - 从头开始放映
- `Shift+F5` - 从当前页放映

### 4. 办公室管理

| 领域 | 核心任务 | 工具 |
|------|---------|------|
| 采购库存 | 追踪物品、数量、 reorder point | 简单表格 |
| 供应商管理 | 合同、SLAs、联系方式 | 共享文档 |
| 空间规划 | 预订系统、15分钟缓冲 | 共享日历 |

---

## ⚡ 怎么使用

### Excel 自动化示例

```python
# Python + openpyxl 自动化 Excel
import openpyxl
from openpyxl.utils import get_column_letter

# 打开工作簿
wb = openpyxl.load_workbook('data.xlsx')
ws = wb.active

# 写入数据
ws['A1'] = '产品'
ws['B1'] = '销量'
ws['C1'] = '=SUMIF(A:A,A2,B:B)'  # SUMIF 公式

# 格式化
ws.column_dimensions['A'].width = 20
ws['A1'].font = openpyxl.styles.Font(bold=True)

# 保存
wb.save('output.xlsx')
```

### Word 文档自动化

```python
# Python + python-docx 自动化 Word
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

doc = Document()
# 添加标题
doc.add_heading('报告标题', 0)

# 添加段落
para = doc.add_paragraph('这是正文内容')
para.runs[0].font.size = Pt(12)

# 添加样式
doc.add_heading('第一部分', level=1)
doc.add_paragraph('第一部分内容...')

# 保存
doc.save('output.docx')
```

### PowerPoint 自动化

```python
# Python + python-pptx 自动化 PPT
from pptx import Presentation
from pptx.util import Inches

prs = Presentation()
# 添加幻灯片
slide = prs.slides.add_slide(prs.slide_layouts[1])

# 添加标题
title = slide.shapes.title
title.text = "演示标题"

# 添加内容
content = slide.placeholders[1]
content.text = "要点1\n要点2\n要点3"

# 保存
prs.save('output.pptx')
```

---

## ✅ 优点

1. **全面覆盖** - Excel/Word/PPT/管理全覆盖
2. **实战导向** - 解决真实办公问题
3. **公式详解** - 常用公式全部覆盖
4. **避坑指南** - 常见错误和解决方案
5. **Python 集成** - 可用代码自动化

---

## ❌ 缺点

1. **文档偏基础** - 高级 VBA/宏没有详细讲解
2. **无 GUI 自动化** - 不涉及 UI 操作
3. **依赖 Office 软件** - 需要安装对应软件
4. **跨平台问题** - Windows/Mac 功能差异

---

## 🎬 使用场景

| 场景 | 工具 | 说明 |
|------|------|------|
| **数据分析** | Excel | VLOOKUP、透视表、数据清洗 |
| **报告生成** | Word | 模板填充、邮件合并 |
| **演示制作** | PowerPoint | 自动化生成幻灯片 |
| **批量处理** | Python + 库 | 批量操作多个文件 |
| **库存管理** | Excel/Sheets | 简单的库存追踪系统 |

---

## 🔧 运行依赖

| 依赖 | 说明 |
|------|------|
| Microsoft 365 | Word/Excel/PowerPoint |
| Python | 代码自动化 |
| openpyxl | Excel 操作 |
| python-docx | Word 操作 |
| python-pptx | PPT 操作 |

### Python 库安装

```bash
pip install openpyxl python-docx python-pptx
```

---

## 🕳️ 避坑指南

| 坑 | 问题 | 解决 |
|-----|------|------|
| VLOOKUP #N/A | 空格/类型不匹配 | TRIM() 清除空格 |
| 公式复制失效 | 缺少 $ | 使用 $A$1 绝对引用 |
| 日期排序错 | 文本日期 | 转换为日期格式 |
| 透视表不更新 | 缓存 | 右键刷新 |
| 页码不从1开始 | 分节符 | 插入分节符设置 |

---

## 📊 总结

**学习价值：⭐⭐⭐⭐（4星）**

| 维度 | 评分 | 说明 |
|------|------|------|
| 办公覆盖 | ⭐⭐⭐⭐⭐ | Excel/Word/PPT 全覆盖 |
| 实用性 | ⭐⭐⭐⭐⭐ | 解决真实办公痛点 |
| 深度 | ⭐⭐⭐ | 偏基础，深度不足 |
| 自动化 | ⭐⭐⭐⭐ | Python 代码示例 |
| 避坑指南 | ⭐⭐⭐⭐⭐ | 常见问题全覆盖 |

**推荐指数：⭐⭐⭐⭐（4星，必装）**

**核心启示：**
> **"AI 不仅是助手，还能成为办公室自动化的核心引擎"**

---

## 📋 对应热门 GitHub 项目

| 项目 | 方向 | 对应功能 |
|------|------|---------|
| **office** | 官方 Skill | ✅ 刚学习 |

---

## 🔗 与其他技能的关系

```
┌─────────────────────────────────────────────────────┐
│                    AI Agent                          │
├─────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────┐   │
│  │              Office Automation              │   │
│  │  Excel ── Word ── PPT ── Admin             │   │
│  └─────────────────────────────────────────────┘   │
│                      │                              │
│         ┌─────────────┼─────────────┐               │
│         │             │             │               │
│    ┌────▼────┐  ┌────▼────┐  ┌────▼────┐        │
│    │Browser  │  │Windows  │  │ Memory   │        │
│    │Control  │  │Control  │  │System    │        │
│    └─────────┘  └─────────┘  └─────────┘        │
└─────────────────────────────────────────────────────┘
```

**4 大技能协同：**
- **Browser-Automation** → 网页数据采集
- **Windows-Control** → 桌面软件控制
- **Memory + AI-Enhanced** → 学习用户偏好
- **Office-Automation** → 办公自动化

