"""Excel 批量导入验收服务。"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from jm_ufo_agent.io.excel import ExcelProductParser
from jm_ufo_agent.storage.repositories.models import ProductRecord


class ProductWriter(Protocol):
    """商品写入仓储协议。"""

    async def upsert(self, record: ProductRecord) -> None:
        """写入或更新一条商品记录。"""


@dataclass(frozen=True)
class ExcelImportSummary:
    """Excel 导入验收摘要。"""

    source_path: str
    parsed_count: int
    written_count: int
    generated_id_rows: list[int] = field(default_factory=list)
    first_rows: list[dict[str, object]] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """转换为 CLI 可输出的 JSON 字典。"""

        # parsed_count 对应 Excel 真实非空数据行数量。
        # written_count 对应 repository 实际 upsert 次数。
        # generated_id_rows 标记缺失商品 ID 的行，后续真实上架前必须人工确认。
        return {
            "source_path": self.source_path,
            "parsed_count": self.parsed_count,
            "written_count": self.written_count,
            "generated_id_rows": list(self.generated_id_rows),
            "first_rows": list(self.first_rows),
        }


class ExcelProductImportService:
    """把 Excel 商品表解析并批量写入商品仓储。"""

    def __init__(self, parser: ExcelProductParser | None = None):
        """初始化导入服务。"""

        # parser 可注入，方便测试覆盖特殊表头和空行。
        # 服务本身不创建数据库连接，真实 MySQL 连接由调用方显式传入。
        # 这样 CLI dry-run 可以只解析文件，不接触生产数据库。
        self.parser = parser or ExcelProductParser()

    async def import_file(self, path: str | Path, repository: ProductWriter | None = None, sheet_name: str | None = None) -> ExcelImportSummary:
        """解析 Excel，并在提供 repository 时批量写入。"""

        # 先完整解析，拿到稳定的 ProductRecord 列表。
        # repository 为 None 时只做验收汇总，适合本地检查真实 xlsx 行数。
        # 写入逐行 await，保证失败时能定位到具体 row_index。
        records = self.parser.parse(path, sheet_name=sheet_name)
        written_count = 0
        for record in records:
            if repository is not None:
                await repository.upsert(record)
            written_count += 1 if repository is not None else 0
        generated_id_rows = [record.row_index for record in records if record.product_id == f"row_{record.row_index}"]
        return ExcelImportSummary(
            source_path=str(path),
            parsed_count=len(records),
            written_count=written_count,
            generated_id_rows=generated_id_rows,
            first_rows=[self._record_preview(record) for record in records[:5]],
        )

    def _record_preview(self, record: ProductRecord) -> dict[str, object]:
        """生成导入摘要里的轻量商品预览。"""

        # 预览只放 row/product_id/title，避免 CLI 输出过大的原始 Excel 行。
        # raw_data 仍保存在 ProductRecord 中，repository 写入时会完整落库。
        # 这个方法不做业务判断，只用于人工快速确认解析是否对齐。
        return {
            "row_index": record.row_index,
            "product_id": record.product_id,
            "title": record.title,
        }
