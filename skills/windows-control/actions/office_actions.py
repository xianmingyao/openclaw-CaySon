#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Office COM 自动化 Actions

提供 Word、Excel、PowerPoint 的 COM 自动化操作。
参考 UFO 的 WinCOMReceiver (basic.py, wordclient.py, excelclient.py, powerpointclient.py)。

依赖: pywin32 (pip install pywin32) — Windows COM 接口
"""
import asyncio
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from app.service.actions.ufo_base_action import UFOBaseAction
from app.service.skills.base_action import (
    ActionResult,
    ActionParameter,
    ParameterType,
)


# ==================== COM 工具函数 ====================

def _get_com_object(app_name: str):
    """通过应用名获取 COM 对象

    支持的应用名:
    - word / winword
    - excel / excel
    - powerpoint / powerpnt
    """
    import win32com.client  # type: ignore
    prog_ids = {
        "word": "Word.Application",
        "winword": "Word.Application",
        "excel": "Excel.Application",
        "powerpoint": "PowerPoint.Application",
        "powerpnt": "PowerPoint.Application",
    }
    prog_id = prog_ids.get(app_name.lower())
    if not prog_id:
        raise ValueError(f"不支持的应用: {app_name}，支持: {list(prog_ids.keys())}")
    return win32com.client.Dispatch(prog_id)


def _get_active_com_object(app_name: str):
    """获取已运行的 COM 对象（如果应用已在运行）"""
    import win32com.client  # type: ignore
    prog_ids = {
        "word": "Word.Application",
        "winword": "Word.Application",
        "excel": "Excel.Application",
        "powerpoint": "PowerPoint.Application",
        "powerpnt": "PowerPoint.Application",
    }
    prog_id = prog_ids.get(app_name.lower())
    if not prog_id:
        raise ValueError(f"不支持的应用: {app_name}")
    try:
        return win32com.client.GetActiveObject(prog_id)
    except Exception:
        return None


# ==================== 基类 ====================

class OfficeBaseAction(UFOBaseAction):
    """Office 操作基类，提供 COM 对象获取和错误处理"""

    # 子类必须定义
    app_name: str = ""

    def _get_app(self):
        """获取 Office COM 对象（优先使用已运行的实例）"""
        obj = _get_active_com_object(self.app_name)
        if obj is None:
            obj = _get_com_object(self.app_name)
        return obj

    def _ensure_visible(self, app):
        """确保应用窗口可见"""
        try:
            app.Visible = True
        except Exception:
            pass


# ==================== 通用 Office Actions ====================

class SaveAction(OfficeBaseAction):
    """保存当前活动文档"""
    name = "save"
    description = "保存当前 Office 活动文档"
    app_name = "word"
    parameters = []

    async def _execute(self) -> ActionResult:
        try:
            app = self._get_app()
            doc = app.ActiveDocument
            doc.Save()
            return ActionResult(success=True, data={"action": "saved"})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class SaveToXmlAction(OfficeBaseAction):
    """将当前文档保存为 XML 格式"""
    name = "save_to_xml"
    description = "将当前 Office 活动文档保存为 XML 格式"
    app_name = "word"
    parameters = [
        ActionParameter(name="path", type=ParameterType.STRING,
                         description="XML 文件保存路径", required=False, default=""),
    ]

    async def _execute(self, path: str = "") -> ActionResult:
        try:
            app = self._get_app()
            doc = app.ActiveDocument
            if path:
                doc.SaveAs(path, FileFormat=11)  # wdFormatXML = 11
            else:
                doc.SaveAs(FileName=doc.FullName + ".xml", FileFormat=11)
            return ActionResult(success=True, data={"action": "saved_to_xml"})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class CloseAction(OfficeBaseAction):
    """关闭当前活动文档"""
    name = "close"
    description = "关闭当前 Office 活动文档"
    app_name = "word"
    parameters = [
        ActionParameter(name="save_changes", type=ParameterType.BOOLEAN,
                         description="关闭前是否保存", required=False, default=True),
    ]

    async def _execute(self, save_changes: bool = True) -> ActionResult:
        try:
            app = self._get_app()
            doc = app.ActiveDocument
            doc.Close(SaveChanges=int(save_changes))
            return ActionResult(success=True, data={"action": "closed"})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


# ==================== Word Actions ====================

class WordInsertTableAction(OfficeBaseAction):
    """在 Word 文档中插入表格"""
    name = "insert_table"
    description = "在 Word 文档光标位置插入表格"
    app_name = "word"
    parameters = [
        ActionParameter(name="rows", type=ParameterType.INTEGER, description="行数"),
        ActionParameter(name="cols", type=ParameterType.INTEGER, description="列数"),
        ActionParameter(name="data", type=ParameterType.ARRAY,
                         description="表格数据 (二维数组)", required=False, default=None),
    ]

    async def _execute(self, rows: int = 3, cols: int = 3, data: list = None) -> ActionResult:
        try:
            app = self._get_app()
            self._ensure_visible(app)
            doc = app.ActiveDocument
            rng = doc.Application.Selection.Range
            table = doc.Tables.Add(rng, rows, cols)
            if data and isinstance(data, list):
                for r_idx, row in enumerate(data):
                    if r_idx >= rows:
                        break
                    for c_idx, cell_val in enumerate(row):
                        if c_idx >= cols:
                            break
                        try:
                            table.Cell(r_idx + 1, c_idx + 1).Range.Text = str(cell_val)
                        except Exception:
                            pass
            return ActionResult(success=True, data={"rows": rows, "cols": cols})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class WordSelectTextAction(OfficeBaseAction):
    """选中文本内容"""
    name = "select_text"
    description = "选中 Word 文档中的文本"
    app_name = "word"
    parameters = [
        ActionParameter(name="start", type=ParameterType.INTEGER,
                         description="起始位置（字符数）", required=False, default=0),
        ActionParameter(name="end", type=ParameterType.INTEGER,
                         description="结束位置（字符数）", required=False, default=0),
    ]

    async def _execute(self, start: int = 0, end: int = 0) -> ActionResult:
        try:
            app = self._get_app()
            self._ensure_visible(app)
            selection = app.Selection
            if end > start:
                rng = app.ActiveDocument.Range(start, end)
                rng.Select()
            elif start > 0:
                app.ActiveDocument.Range(start, start + 100).Select()
            return ActionResult(success=True, data={"start": start, "end": end})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class WordSelectTableAction(OfficeBaseAction):
    """选中表格"""
    name = "select_table"
    description = "选中 Word 文档中光标所在的表格"
    app_name = "word"
    parameters = []

    async def _execute(self) -> ActionResult:
        try:
            app = self._get_app()
            self._ensure_visible(app)
            table = app.Selection.Tables(1) if app.Selection.Tables.Count > 0 else None
            if table:
                table.Select()
                return ActionResult(success=True, data={"rows": table.Rows.Count, "cols": table.Columns.Count})
            return ActionResult(success=False, error="光标不在表格中")
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class WordSelectParagraphAction(OfficeBaseAction):
    """选中段落"""
    name = "select_paragraph"
    description = "选中 Word 文档中光标所在的段落"
    app_name = "word"
    parameters = []

    async def _execute(self) -> ActionResult:
        try:
            app = self._get_app()
            self._ensure_visible(app)
            para = app.Selection.Paragraphs(1)
            para.Range.Select()
            text = para.Range.Text.strip()
            return ActionResult(success=True, data={"text": text[:500]})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class WordSaveAsAction(OfficeBaseAction):
    """Word 文档另存为"""
    name = "word_save_as"
    description = "将 Word 文档另存为指定格式"
    app_name = "word"
    parameters = [
        ActionParameter(name="path", type=ParameterType.STRING, description="保存路径"),
        ActionParameter(name="format", type=ParameterType.STRING,
                         description="格式 (docx/pdf/txt/rtf/htm/xml)", required=False, default="docx"),
    ]

    async def _execute(self, path: str, format: str = "docx") -> ActionResult:
        try:
            app = self._get_app()
            doc = app.ActiveDocument
            format_map = {
                "docx": 16, "doc": 0, "pdf": 17, "txt": 2,
                "rtf": 6, "htm": 8, "html": 8, "xml": 11,
                "docm": 13, "dotx": 14, "dotm": 15, "xps": 18,
            }
            file_format = format_map.get(format.lower(), 16)
            doc.SaveAs(FileName=path, FileFormat=file_format)
            return ActionResult(success=True, data={"path": path, "format": format})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class WordSetFontAction(OfficeBaseAction):
    """设置字体样式"""
    name = "set_font"
    description = "设置选中文本的字体样式（名称、大小、加粗、斜体、颜色）"
    app_name = "word"
    parameters = [
        ActionParameter(name="font_name", type=ParameterType.STRING,
                         description="字体名称", required=False, default=""),
        ActionParameter(name="size", type=ParameterType.INTEGER,
                         description="字号", required=False, default=0),
        ActionParameter(name="bold", type=ParameterType.BOOLEAN,
                         description="是否加粗", required=False, default=None),
        ActionParameter(name="italic", type=ParameterType.BOOLEAN,
                         description="是否斜体", required=False, default=None),
        ActionParameter(name="color", type=ParameterType.STRING,
                         description="颜色 (十六进制，如 FF0000)", required=False, default=""),
    ]

    async def _execute(self, font_name: str = "", size: int = 0, bold: bool = None,
                       italic: bool = None, color: str = "") -> ActionResult:
        try:
            app = self._get_app()
            self._ensure_visible(app)
            font = app.Selection.Font
            if font_name:
                font.Name = font_name
            if size > 0:
                font.Size = size
            if bold is not None:
                font.Bold = bold
            if italic is not None:
                font.Italic = italic
            if color:
                # 将十六进制颜色转换为 RGB
                rgb = int(color, 16)
                font.Color = rgb
            return ActionResult(success=True, data={
                "font_name": font_name or font.Name,
                "size": size or font.Size,
            })
        except Exception as e:
            return ActionResult(success=False, error=str(e))


# ==================== Excel Actions ====================

class ExcelTable2MarkdownAction(OfficeBaseAction):
    """将 Excel 表格转换为 Markdown 格式"""
    name = "table2markdown"
    description = "将 Excel 选中区域转换为 Markdown 表格字符串"
    app_name = "excel"
    parameters = []

    async def _execute(self) -> ActionResult:
        try:
            app = self._get_app()
            self._ensure_visible(app)
            selection = app.Selection
            if not selection or not hasattr(selection, "Value2"):
                return ActionResult(success=False, error="无选中区域")
            try:
                values = selection.Value2
            except Exception:
                return ActionResult(success=False, error="无法读取选中区域")

            if not values:
                return ActionResult(success=True, data={"markdown": "", "rows": 0})

            if not isinstance(values[0], list):
                values = [values]

            lines = []
            for row in values:
                cells = [str(c) if c is not None else "" for c in row]
                lines.append("| " + " | ".join(cells) + " |")
            # 分隔行
            if lines:
                sep = "| " + " | ".join(["---"] * len(lines[0].split("|"))) + " |"
                lines.insert(1, sep)
            markdown = "\n".join(lines)
            return ActionResult(success=True, data={
                "markdown": markdown[:10000],
                "rows": len(values),
            })
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class ExcelInsertTableAction(OfficeBaseAction):
    """在 Excel 中插入表格数据"""
    name = "insert_excel_table"
    description = "在 Excel 活动单元格位置插入二维数组数据"
    app_name = "excel"
    parameters = [
        ActionParameter(name="data", type=ParameterType.ARRAY, description="表格数据 (二维数组)"),
        ActionParameter(name="start_cell", type=ParameterType.STRING,
                         description="起始单元格 (如 A1)", required=False, default="A1"),
    ]

    async def _execute(self, data: list, start_cell: str = "A1") -> ActionResult:
        try:
            app = self._get_app()
            self._ensure_visible(app)
            sheet = app.ActiveSheet
            # 解析起始单元格
            start_cell = start_cell.upper()
            col = 0
            row = 0
            for ch in start_cell:
                if ch.isalpha():
                    col = col * 26 + (ord(ch.upper()) - ord("A"))
                else:
                    row = int(ch) - 1
            for r_idx, row_data in enumerate(data):
                for c_idx, val in enumerate(row_data):
                    try:
                        sheet.Cells(row + r_idx + 1, col + c_idx + 1).Value = val
                    except Exception:
                        pass
            return ActionResult(success=True, data={
                "rows": len(data),
                "start_cell": start_cell,
            })
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class ExcelSelectTableRangeAction(OfficeBaseAction):
    """选中 Excel 单元格范围"""
    name = "select_table_range"
    description = "选中 Excel 中指定单元格范围"
    app_name = "excel"
    parameters = [
        ActionParameter(name="range", type=ParameterType.STRING, description="单元格范围 (如 A1:D10)"),
    ]

    async def _execute(self, range_str: str = "A1:D10") -> ActionResult:
        try:
            app = self._get_app()
            self._ensure_visible(app)
            rng = app.Range(range_str)
            rng.Select()
            return ActionResult(success=True, data={"range": range_str})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class ExcelGetRangeValuesAction(OfficeBaseAction):
    """获取 Excel 指定范围的值"""
    name = "get_range_values"
    description = "获取 Excel 中指定范围的单元格值"
    app_name = "excel"
    parameters = [
        ActionParameter(name="range", type=ParameterType.STRING, description="单元格范围 (如 A1:D10)"),
    ]

    async def _execute(self, range_str: str = "A1:D10") -> ActionResult:
        try:
            app = self._get_app()
            self._ensure_visible(app)
            rng = app.Range(range_str)
            values = rng.Value2
            # 转换为二维列表
            result = []
            if values:
                if isinstance(values[0], list):
                    result = [[str(c) if c is not None else "" for c in row] for row in values]
                else:
                    result = [[str(c) if c is not None else "" for c in values]]
            return ActionResult(success=True, data={
                "values": result,
                "rows": len(result),
                "cols": len(result[0]) if result else 0,
            })
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class ExcelReorderColumnsAction(OfficeBaseAction):
    """重排列的顺序"""
    name = "reorder_columns"
    description = "重排 Excel 表格中列的顺序"
    app_name = "excel"
    parameters = [
        ActionParameter(name="column_indices", type=ParameterType.ARRAY,
                         description="新的列顺序 (基于 0 的索引列表, 如 [2, 0, 1])"),
    ]

    async def _execute(self, column_indices: list = None) -> ActionResult:
        try:
            app = self._get_app()
            self._ensure_visible(app)
            selection = app.Selection
            if not column_indices:
                return ActionResult(success=False, error="column_indices 不能为空")

            values = selection.Value2
            if not values or not isinstance(values, list):
                return ActionResult(success=False, error="无选中数据")

            # 重排列
            if isinstance(values[0], list):
                reordered = [[row[i] if i < len(row) else "" for i in column_indices] for row in values]
            else:
                reordered = [[values[i] if i < len(values) else "" for i in column_indices]]
            selection.Value2 = reordered

            return ActionResult(success=True, data={"reordered_columns": column_indices})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class ExcelSaveAsAction(OfficeBaseAction):
    """Excel 工作簿另存为"""
    name = "excel_save_as"
    description = "将 Excel 工作簿另存为指定格式"
    app_name = "excel"
    parameters = [
        ActionParameter(name="path", type=ParameterType.STRING, description="保存路径"),
        ActionParameter(name="format", type=ParameterType.STRING,
                         description="格式 (xlsx/csv/pdf/txt/html/xml)", required=False, default="xlsx"),
    ]

    async def _execute(self, path: str, format: str = "xlsx") -> ActionResult:
        try:
            app = self._get_app()
            wb = app.ActiveWorkbook
            format_map = {
                "xlsx": 51, "csv": 6, "pdf": 0, "txt": -4158,
                "html": 44, "xml": 46, "xlsm": 52, "xlsb": 50, "xls": 56,
            }
            file_format = format_map.get(format.lower(), 51)
            wb.SaveAs(FileName=path, FileFormat=file_format)
            return ActionResult(success=True, data={"path": path, "format": format})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


# ==================== PowerPoint Actions ====================

class PPTSetBackgroundColorAction(OfficeBaseAction):
    """设置幻灯片背景颜色"""
    name = "set_background_color"
    description = "设置 PowerPoint 幻灯片的背景颜色"
    app_name = "powerpoint"
    parameters = [
        ActionParameter(name="color", type=ParameterType.STRING, description="颜色 (十六进制，如 0070C0)"),
        ActionParameter(name="slide_index", type=ParameterType.INTEGER,
                         description="幻灯片索引 (1-based)", required=False, default=1),
    ]

    async def _execute(self, color: str = "FFFFFF", slide_index: int = 1) -> ActionResult:
        try:
            app = self._get_app()
            self._ensure_visible(app)
            slides = app.ActivePresentation.Slides
            if slide_index < 1 or slide_index > slides.Count:
                return ActionResult(success=False, error=f"幻灯片索引超出范围 (1-{slides.Count})")
            slide = slides(slide_index)
            background = slide.Background
            fill = background.Fill
            fill.Solid()
            # 将十六进制转换为 RGB
            rgb = int(color, 16)
            fill.ForeColor.RGB = rgb
            return ActionResult(success=True, data={"color": color, "slide_index": slide_index})
        except Exception as e:
            return ActionResult(success=False, error=str(e))


class PPTSaveAsAction(OfficeBaseAction):
    """PowerPoint 演示文稿另存为"""
    name = "ppt_save_as"
    description = "将 PowerPoint 演示文稿另存为指定格式"
    app_name = "powerpoint"
    parameters = [
        ActionParameter(name="path", type=ParameterType.STRING, description="保存路径"),
        ActionParameter(name="format", type=ParameterType.STRING,
                         description="格式 (pptx/pdf/jpg/png/mp4)", required=False, default="pptx"),
    ]

    async def _execute(self, path: str, format: str = "pptx") -> ActionResult:
        try:
            app = self._get_app()
            pres = app.ActivePresentation
            format_map = {
                "pptx": 24, "pdf": 32, "jpg": 17, "png": 18,
                "gif": 26, "mp4": -1, "wmv": 37, "xps": 20,
            }
            if format == "pptx":
                pres.SaveAs(path)
            else:
                file_format = format_map.get(format.lower(), 24)
                pres.SaveAs(path, file_format)
            return ActionResult(success=True, data={"path": path, "format": format})
        except Exception as e:
            return ActionResult(success=False, error=str(e))
