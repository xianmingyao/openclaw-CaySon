#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Convert Markdown report to Word document preserving formatting."""

from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import re

# Markdown content
markdown_content = """# 2026年4月工作月报

**汇报人：先明瑶**
**汇报日期：2026年5月11日**

---

## 一、本月工作完成情况

### 1. 京麦智能体开发 [60% → 98.5%]
| 阶段 | 完成度 | 主要工作 |
|------|--------|----------|
| 4月上旬 | 60%→81% | Claude Code源码分析、GitHub数据采集脚本开发 |
| 4月中旬 | 82%→92% | 重构RAG知识库代码、Skill写作规范、封装技能测试 |
| 4月下旬 | 94%→98.5% | UFO架构重构、鼠标识别精准度优化、bug修复 |

**本月核心成果：**
- 完成WebMCP、MCP浏览器自动化深度研究报告
- 完成browser-use CLI 2.0深度研究报告
- 开发jingmai-cli、jingmai-putaway、jingmai-product-publish等核心技能
- 京麦商品上架流程截图录制（18张）验证自动化流程

### 2. OpenClaw多渠道AI助手系统配置 [40%→60%]
**本月新增安装技能（20+个）：**
- 自动化类：opencli-agent、desktop-control-cli、jingmai-putaway、jingmai-product-publish
- 内容类：content-hunter、auto-publisher、react-best-practices
- 效率类：prd-writer、web-access、nuwa-skill
- 特殊技能：nano-banana-pro、summarize、karpathy-skills、huguanjin-libtv-skill

**系统优化：**
- 完成SkillHub安全协议与每日安全扫描Cron配置
- AI-NATIVE工作流SOP标准流程制定
- Hermès风格Skill沉淀机制升级
- 知识库双向同步+持续ingest+统一检索机制

### 3. 日常运维与问题处理

| 人员 | 问题类型 | 处理结果 |
|------|----------|----------|
| 付总 | 小龙虾异常 | 已处理 |
| 小蒙 | 小龙虾异常 + 京麦上品调试 | 已处理 |
| 京采 | 京麦API权限开通沟通 | 进行中 |

---

## 二、技术成果统计

### Git提交统计
- **4月1日：** 11条commit（GitHub数据采集脚本、每日趋势数据更新）
- **4月8日：** 9条commit（文档更新与技能配置）
- **4月23日：** 6条commit（MAGMA v2.1，AI记忆系统对比分析）
- **4月29日：** 5条commit（jingmai-putaway UFO Agent修复优化）

### 代码开发统计
| 类别 | 数量 |
|------|------|
| 新增技能 | 20+个 |
| 新增脚本 | 20+个（uia系列） |
| 自动化截图 | 18+张 |
| 会话记录 | 138个 |

---

## 三、待解决问题

| 问题 | 状态 | 备注 |
|------|------|------|
| 京麦API权限开通 | 进行中 | 与京采持续沟通 |
| jingmai-cli MySQL连接bug | 排查中 | localhost vs 8.137.122.11配置问题 |

---

## 四、一句话总结

> 🎯 京麦智能体从60%推进到98.5%，进入收尾阶段；OpenClaw技能体系日趋完善；持续处理日常异常，保障业务稳定运行。"""

def add_horizontal_rule(doc):
    """添加水平分隔线"""
    p = doc.add_paragraph()
    p_fmt = p.paragraph_format
    p_fmt.space_before = Pt(6)
    p_fmt.space_after = Pt(6)
    # 使用下划线模拟分隔线
    run = p.add_run("─" * 50)
    run.font.color.rgb = RGBColor(200, 200, 200)

def parse_markdown_line(line):
    """解析Markdown行，返回(文本, 样式类型)"""
    # 移除Markdown标记
    text = line
    style = 'normal'
    
    # H1
    if line.startswith('# '):
        text = line[2:]
        style = 'heading1'
    # H2
    elif line.startswith('## '):
        text = line[3:]
        style = 'heading2'
    # H3
    elif line.startswith('### '):
        text = line[4:]
        style = 'heading3'
    # H4
    elif line.startswith('#### '):
        text = line[5:]
        style = 'heading4'
    # 粗体文本
    elif line.startswith('**') and line.endswith('**'):
        text = line[2:-2]
        style = 'bold'
    # 列表项
    elif line.startswith('- '):
        text = "• " + line[2:]
        style = 'list'
    # 引用
    elif line.startswith('> '):
        text = line[2:]
        style = 'quote'
    # 分隔线
    elif line.strip() == '---':
        style = 'hr'
        text = ''
    # 表格行 - 检测 | 列 | 格式
    elif '|' in line and line.strip().startswith('|'):
        style = 'table'
        text = line
    # 空行
    elif not line.strip():
        style = 'empty'
        text = ''
    
    return text, style

def create_table(doc, header_line, data_lines):
    """创建Word表格"""
    # 解析表头
    headers = [h.strip() for h in header_line.split('|') if h.strip()]
    
    # 解析数据行（跳过分隔行）
    rows = []
    for line in data_lines:
        if line.strip() and '|' in line and not line.strip().startswith('|---'):
            cols = [c.strip() for c in line.split('|') if c.strip()]
            if cols:
                rows.append(cols)
    
    if not headers or not rows:
        return
    
    # 创建表格
    num_cols = len(headers)
    table = doc.add_table(rows=1 + len(rows), cols=num_cols)
    table.style = 'Table Grid'
    
    # 设置表头
    header_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        header_cells[i].text = header
        # 表头加粗
        for paragraph in header_cells[i].paragraphs:
            for run in paragraph.runs:
                run.bold = True
    
    # 设置数据行
    for row_idx, row_data in enumerate(rows):
        row_cells = table.rows[row_idx + 1].cells
        for col_idx, cell_text in enumerate(row_data):
            if col_idx < num_cols:
                row_cells[col_idx].text = cell_text
    
    # 居中对齐
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

def convert_markdown_to_docx(markdown_text, output_path):
    """将Markdown转换为Word文档"""
    doc = Document()
    
    # 设置文档标题
    title = doc.add_heading('2026年4月工作月报', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 添加汇报人信息
    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = meta.add_run('汇报人：先明瑶    汇报日期：2026年5月11日')
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(100, 100, 100)
    
    doc.add_paragraph()
    
    # 按行处理Markdown内容
    lines = markdown_text.split('\n')
    i = 0
    current_table_header = None
    current_table_data = []
    in_table = False
    
    while i < len(lines):
        line = lines[i]
        
        # 检测表格开始
        if '|' in line and line.strip().startswith('|') and '---' not in line and not in_table:
            in_table = True
            current_table_header = line
            current_table_data = []
            i += 1
            continue
        
        # 检测表格分隔行
        if in_table and ('---' in line or (line.strip().startswith('|') and all(c.strip() in ['-', ':', '|', ' '] for c in line if c.strip() and c.strip() not in '|'))):
            i += 1
            continue
        
        # 检测表格结束并创建表格
        if in_table and (not line.strip() or ('|' not in line and line.strip()) or (line.strip() and not line.strip().startswith('|'))):
            if current_table_header:
                create_table(doc, current_table_header, current_table_data)
            in_table = False
            current_table_header = None
            current_table_data = []
            if not line.strip():
                i += 1
                continue
        
        # 如果在表格中，收集数据行
        if in_table:
            if '|' in line:
                current_table_data.append(line)
            i += 1
            continue
        
        # 处理分隔线
        if line.strip() == '---':
            add_horizontal_rule(doc)
            i += 1
            continue
        
        # 解析并添加文本
        text, style = parse_markdown_line(line)
        
        if style == 'empty':
            doc.add_paragraph()
        elif style == 'heading1':
            doc.add_heading(text, level=1)
        elif style == 'heading2':
            doc.add_heading(text, level=2)
        elif style == 'heading3':
            doc.add_heading(text, level=3)
        elif style == 'heading4':
            doc.add_heading(text, level=4)
        elif style == 'bold':
            p = doc.add_paragraph()
            run = p.add_run(text)
            run.bold = True
        elif style == 'list':
            p = doc.add_paragraph(text, style='List Bullet')
        elif style == 'quote':
            p = doc.add_paragraph()
            run = p.add_run(text)
            run.italic = True
            run.font.color.rgb = RGBColor(80, 80, 80)
        elif style == 'table':
            # 这行是表格的一部分，已在上面的逻辑中处理
            pass
        else:
            if text:
                doc.add_paragraph(text)
        
        i += 1
    
    # 处理最后一个表格
    if in_table and current_table_header:
        create_table(doc, current_table_header, current_table_data)
    
    # 添加引用段落（一句话总结）
    last_section = doc.add_paragraph()
    last_section.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = last_section.add_run('🎯 京麦智能体从60%推进到98.5%，进入收尾阶段；OpenClaw技能体系日趋完善；持续处理日常异常，保障业务稳定运行。')
    run.italic = True
    run.font.color.rgb = RGBColor(60, 60, 60)
    
    # 保存文档
    doc.save(output_path)
    print(f"Document saved to: {output_path}")

if __name__ == '__main__':
    output_file = r'E:\workspace\docs\月报\2026年4月工作月报_先明瑶.docx'
    convert_markdown_to_docx(markdown_content, output_file)
