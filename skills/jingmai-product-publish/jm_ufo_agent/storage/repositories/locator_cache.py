"""字段定位缓存 Repository。"""

from __future__ import annotations

from jm_ufo_agent.storage.repositories.base import SQLRepository
from jm_ufo_agent.storage.repositories.models import LocatorCacheRecord


class LocatorCacheRepository(SQLRepository):
    """读写 `jm_locator_cache` 表。"""

    async def upsert(self, record: LocatorCacheRecord) -> None:
        """写入或刷新字段定位缓存。"""

        # field_key + page_signature 是唯一键，代表某个页面版本下的字段位置。
        # hit_count 在命中时递增，用于后续淘汰低质量 locator。
        # confidence 保留小数，真实 OCR/VLM 接入后可直接写入置信度。
        await self.execute(
            """
            INSERT INTO jm_locator_cache (
                field_key, page_signature, selector_type, selector_value, confidence, hit_count
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                selector_type = VALUES(selector_type),
                selector_value = VALUES(selector_value),
                confidence = VALUES(confidence),
                hit_count = hit_count + 1,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                record.field_key,
                record.page_signature,
                record.selector_type,
                record.selector_value,
                record.confidence,
                record.hit_count,
            ),
        )

    async def get(self, field_key: str, page_signature: str) -> LocatorCacheRecord | None:
        """读取一个字段的定位缓存。"""

        # 找不到缓存时返回 None，让上层进入 CALIBRATE_LOCATORS。
        # 这里只按唯一键查询，不做模糊匹配，避免错用其它页面版本的坐标。
        # tuple/dict row 同时支持，降低测试和真实数据库游标差异。
        row = await self.fetchone(
            """
            SELECT field_key, page_signature, selector_type, selector_value, confidence, hit_count
            FROM jm_locator_cache
            WHERE field_key = %s AND page_signature = %s
            """,
            (field_key, page_signature),
        )
        if row is None:
            return None
        if isinstance(row, dict):
            return LocatorCacheRecord(
                field_key=row["field_key"],
                page_signature=row["page_signature"],
                selector_type=row["selector_type"],
                selector_value=row["selector_value"],
                confidence=float(row.get("confidence") or 0.0),
                hit_count=int(row.get("hit_count") or 0),
            )
        field_key, page_signature, selector_type, selector_value, confidence, hit_count = row
        return LocatorCacheRecord(field_key, page_signature, selector_type, selector_value, float(confidence or 0.0), int(hit_count or 0))
