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

准备数据源（Excel）→ Word → 邮件 → 开始邮件合并 → 信件

↓

插入合并域 → <<姓名>> <<地址>>

↓

预览结果 → 完成合并

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

### Word 文档自动化

# Python + python-docx 自动化 Word

from docx import Document

from docx.shared import Pt

from docx.enum.text import WD_PARAGRAPH_ALIGNMENT