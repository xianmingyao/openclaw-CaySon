"""Excel 商品表解析。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jm_ufo_agent.storage.repositories.models import ProductRecord


class ExcelProductParser:
    """把 xlsx 行解析为商品记录。"""

    def __init__(self, product_id_columns: tuple[str, ...] = ("product_id", "商品ID", "京东商品ID", "sku", "上架序号")):
        """初始化解析器。"""

        # product_id_columns 是候选列名，兼容中英文表头。
        # 解析器不在构造时导入 openpyxl，避免依赖缺失导致包无法导入。
        # 表头规范化逻辑集中在 _normalize_header。
        self.product_id_columns = product_id_columns

    def parse(self, path: str | Path, sheet_name: str | None = None) -> list[ProductRecord]:
        """解析 xlsx 文件。"""

        # 真实文件读取是显式调用，不会在 CLI dry-run 中自动发生。
        # read_only=True 降低大表内存占用。
        # data_only=True 读取公式计算值，符合上架表使用习惯。
        try:
            from openpyxl import load_workbook
        except ImportError as exc:
            raise RuntimeError("缺少 openpyxl，无法解析 xlsx") from exc

        workbook = load_workbook(Path(path), read_only=True, data_only=True)
        sheet = workbook[sheet_name] if sheet_name else workbook.active
        rows = sheet.iter_rows(values_only=True)
        header_row_index, headers = self._find_header_row(rows)
        records: list[ProductRecord] = []
        for excel_row_index, row in enumerate(rows, start=header_row_index + 1):
            raw = self._row_to_dict(headers, row)
            if not any(value not in (None, "") for value in raw.values()):
                continue
            records.append(self._to_product_record(excel_row_index, raw))
        workbook.close()
        return records

    def _find_header_row(self, rows) -> tuple[int, list[str]]:
        """扫描并定位真实表头行。"""

        # 真实“湖南上架表格.xlsx”前两行是标题和说明，第三行才是字段表头。
        # 最多扫描前 20 行，兼容普通第一行表头，也避免大表全量读入内存。
        # 找不到明确表头时退回第一行，保持旧的简单表格行为兼容。
        first_row: tuple[Any, ...] | None = None
        for row_index, row in enumerate(rows, start=1):
            if first_row is None:
                first_row = row
            headers = self._read_headers(row)
            if self._looks_like_header(headers):
                return row_index, headers
            if row_index >= 20:
                break
        return 1, self._read_headers(first_row)

    def _looks_like_header(self, headers: list[str]) -> bool:
        """判断一行是否像商品上架表头。"""

        # 商品表头通常同时包含商品名称/品牌/型号/京东链接等业务列。
        # 只命中一个词可能是说明文字，所以至少需要两个关键信号。
        # 使用包含匹配，兼容“商品名称（对应京东开票内容）”这类长表头。
        joined = "|".join(headers)
        signals = ["商品ID", "商品名称", "商品标题", "品牌", "商品型号", "京东链接", "上架序号", "京东挂网价"]
        return sum(1 for signal in signals if signal in joined) >= 2

    def _read_headers(self, row: tuple[Any, ...] | None) -> list[str]:
        """读取并规范化表头。"""

        # 空工作表直接报错，避免悄悄返回空商品列表。
        # 空表头用 column_N 占位，保证每个单元格都有 key。
        # strip 用于清理 Excel 表头常见空白。
        if row is None:
            raise ValueError("xlsx 缺少表头")
        return [self._normalize_header(value, index) for index, value in enumerate(row, start=1)]

    def _normalize_header(self, value: Any, index: int) -> str:
        """规范化单个表头。"""

        # None 表头用 column_N，避免 dict key 为空。
        # 字符串表头只去掉首尾空白，不擅自翻译。
        # index 从 1 开始，对应 Excel 列序号。
        text = "" if value is None else str(value).strip()
        return text or f"column_{index}"

    def _row_to_dict(self, headers: list[str], row: tuple[Any, ...]) -> dict[str, Any]:
        """把 Excel 行转换为字典。"""

        # zip 只覆盖已有单元格，缺失尾列自动补 None。
        # 这样 raw_data 的 key 集合和表头一致，便于后续字段映射。
        # 不在这里做业务清洗，保留原始证据。
        values = list(row)
        if len(values) < len(headers):
            values.extend([None] * (len(headers) - len(values)))
        return dict(zip(headers, values, strict=False))

    def _to_product_record(self, row_index: int, raw: dict[str, Any]) -> ProductRecord:
        """转换为 ProductRecord。"""

        # product_id 优先从候选列读取。
        # 找不到商品 ID 时用 row_行号 作为稳定占位，后续校验可阻断。
        # title 兼容常见中文/英文字段名。
        product_id = self._first_present(raw, self.product_id_columns) or f"row_{row_index}"
        title = self._first_present(raw, ("title", "商品标题", "标题", "商品名称", "商品名称（对应京东开票内容）")) or ""
        return ProductRecord(product_id=str(product_id), row_index=row_index, title=str(title), raw_data=raw)

    def _first_present(self, raw: dict[str, Any], keys: tuple[str, ...]) -> Any:
        """按候选 key 读取第一个非空值。"""

        # Excel 表头可能中英文混用，所以按候选顺序查找。
        # None 和空字符串都视为缺失。
        # 返回原始值，不在这里转字符串，保留证据类型。
        for key in keys:
            value = raw.get(key)
            if value not in (None, ""):
                return value
        for raw_key, value in raw.items():
            if value in (None, ""):
                continue
            raw_key_text = str(raw_key)
            if any(key and key in raw_key_text for key in keys):
                return value
        return None
