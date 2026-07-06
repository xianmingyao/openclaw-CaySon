"""商品 Repository。"""

from __future__ import annotations

from typing import Any

from jm_ufo_agent.storage.repositories.base import SQLRepository
from jm_ufo_agent.storage.repositories.models import ProductRecord


class ProductRepository(SQLRepository):
    """读写 `jm_products` 表。"""

    async def upsert(self, record: ProductRecord) -> None:
        """插入或更新商品数据。

        # raw_data 保存 Excel 原始行，便于追溯输入证据。
        # enriched_data 保存京东抓取和图片处理后的增强数据。
        # row_index 建唯一索引后可支持行级恢复不重复处理。
        """

        await self.execute(
            """
            INSERT INTO jm_products (product_id, row_index, title, raw_json, enriched_json)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                row_index = VALUES(row_index),
                title = VALUES(title),
                raw_json = VALUES(raw_json),
                enriched_json = VALUES(enriched_json),
                updated_at = CURRENT_TIMESTAMP
            """,
            (record.product_id, record.row_index, record.title, self.dumps_json(record.raw_data), self.dumps_json(record.enriched_data)),
        )

    async def get_by_row(self, row_index: int) -> ProductRecord | None:
        """按 Excel 行号查询商品。"""

        row = await self.fetchone(
            "SELECT product_id, row_index, title, raw_json, enriched_json FROM jm_products WHERE row_index = %s",
            (row_index,),
        )
        if row is None:
            return None
        return self._row_to_record(row)

    def _row_to_record(self, row: Any) -> ProductRecord:
        """把数据库行转换为 `ProductRecord`。"""

        # dict row 适合单元测试和 DictCursor。
        # tuple row 适合默认游标，字段顺序必须和 SELECT 保持一致。
        # raw/enriched 两个 JSON 字段都在这里反序列化，保持上层代码干净。
        if isinstance(row, dict):
            return ProductRecord(
                product_id=row["product_id"],
                row_index=row["row_index"],
                title=row["title"],
                raw_data=self.loads_json(row.get("raw_json")),
                enriched_data=self.loads_json(row.get("enriched_json")),
            )
        product_id, row_index, title, raw_json, enriched_json = row
        return ProductRecord(product_id=product_id, row_index=row_index, title=title, raw_data=self.loads_json(raw_json), enriched_data=self.loads_json(enriched_json))
