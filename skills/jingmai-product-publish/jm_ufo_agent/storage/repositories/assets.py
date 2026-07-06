"""商品素材 Repository。"""

from __future__ import annotations

from jm_ufo_agent.storage.repositories.base import SQLRepository
from jm_ufo_agent.storage.repositories.models import ProductAssetRecord


class ProductAssetRepository(SQLRepository):
    """读写 `jm_product_assets` 表。"""

    async def upsert(self, record: ProductAssetRecord) -> None:
        """插入或更新商品素材记录。"""

        # product_id + asset_type + remote_url 可以稳定标识同一张外部图片。
        # transformed_path 和 transform_status 由图片转换链路逐步更新。
        # metadata_json 保存下载尺寸、hash、失败原因等轻量证据。
        await self.execute(
            """
            INSERT INTO jm_product_assets (
                product_id, task_id, row_index, asset_type, local_path, remote_url,
                transform_status, transformed_path, metadata_json
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                local_path = VALUES(local_path),
                transform_status = VALUES(transform_status),
                transformed_path = VALUES(transformed_path),
                metadata_json = VALUES(metadata_json),
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                record.product_id,
                record.task_id,
                record.row_index,
                record.asset_type,
                record.local_path,
                record.remote_url,
                record.transform_status,
                record.transformed_path,
                self.dumps_json(record.metadata),
            ),
        )

    async def list_by_product(self, product_id: str) -> list[ProductAssetRecord]:
        """读取某个商品的全部素材。"""

        # 返回值用于判断主图/副图是否全部下载和转换完成。
        # dict row 和 tuple row 都支持，方便 fake connection 与真实 cursor 共用。
        # 没有素材时返回空列表，不把“未下载”伪装成异常。
        rows = await self.fetchall(
            """
            SELECT product_id, task_id, row_index, asset_type, local_path, remote_url,
                   transform_status, transformed_path, metadata_json
            FROM jm_product_assets
            WHERE product_id = %s
            """,
            (product_id,),
        )
        return [self._row_to_record(row) for row in rows]

    def _row_to_record(self, row) -> ProductAssetRecord:
        """把数据库行转换为 ProductAssetRecord。"""

        # dict row 适配 DictCursor 和单元测试。
        # tuple row 的字段顺序必须和 SELECT 保持一致。
        # metadata_json 统一走 loads_json，避免调用方重复解析。
        if isinstance(row, dict):
            return ProductAssetRecord(
                product_id=row["product_id"],
                task_id=row.get("task_id"),
                row_index=row.get("row_index"),
                asset_type=row["asset_type"],
                local_path=row.get("local_path"),
                remote_url=row.get("remote_url"),
                transform_status=row.get("transform_status") or "pending",
                transformed_path=row.get("transformed_path"),
                metadata=self.loads_json(row.get("metadata_json")),
            )
        product_id, task_id, row_index, asset_type, local_path, remote_url, transform_status, transformed_path, metadata_json = row
        return ProductAssetRecord(
            product_id=product_id,
            task_id=task_id,
            row_index=row_index,
            asset_type=asset_type,
            local_path=local_path,
            remote_url=remote_url,
            transform_status=transform_status or "pending",
            transformed_path=transformed_path,
            metadata=self.loads_json(metadata_json),
        )
