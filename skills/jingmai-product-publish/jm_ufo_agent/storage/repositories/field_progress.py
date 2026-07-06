"""字段级进度 Repository。"""

from __future__ import annotations

from typing import Any

from jm_ufo_agent.storage.repositories.base import SQLRepository
from jm_ufo_agent.storage.repositories.models import FieldProgressRecord


class FieldProgressRepository(SQLRepository):
    """读写 `jm_field_progress` 表。"""

    async def mark(self, record: FieldProgressRecord) -> None:
        """记录字段填充或校验状态。

        # 字段级断点的唯一键是 task_id + row_index + field_name。
        # evidence 保存截图、OCR、读回值等证据摘要。
        # 恢复时只跳过 status=verified 的字段，避免未验证字段误判成功。
        """

        await self.execute(
            """
            INSERT INTO jm_field_progress (task_id, row_index, field_name, status, evidence_json)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                status = VALUES(status),
                evidence_json = VALUES(evidence_json),
                updated_at = CURRENT_TIMESTAMP
            """,
            (record.task_id, record.row_index, record.field_name, record.status, self.dumps_json(record.evidence)),
        )

    async def get(self, task_id: str, row_index: int, field_name: str) -> FieldProgressRecord | None:
        """查询单个字段进度。"""

        row = await self.fetchone(
            """
            SELECT task_id, row_index, field_name, status, evidence_json, updated_at
            FROM jm_field_progress
            WHERE task_id = %s AND row_index = %s AND field_name = %s
            """,
            (task_id, row_index, field_name),
        )
        if row is None:
            return None
        return self._row_to_record(row)

    async def list_verified_fields(self, task_id: str, row_index: int) -> set[str]:
        """查询某一行已验证字段集合。"""

        # 只返回 status=verified 的字段，其他状态不能作为恢复跳过依据。
        # set 天然去重，适合直接喂给 DeterministicPlanStrategy。
        # 该方法是字段级断点续传的核心查询。
        rows = await self.fetchall(
            """
            SELECT field_name
            FROM jm_field_progress
            WHERE task_id = %s AND row_index = %s AND status = 'verified'
            """,
            (task_id, row_index),
        )
        fields: set[str] = set()
        for row in rows:
            fields.add(row["field_name"] if isinstance(row, dict) else row[0])
        return fields

    def _row_to_record(self, row: Any) -> FieldProgressRecord:
        """把数据库行转换为 `FieldProgressRecord`。"""

        # 字段进度是恢复逻辑的关键证据，不能把 evidence 当作普通字符串透传。
        # dict row 和 tuple row 都支持，便于切换数据库游标实现。
        # updated_at 保留原始数据库类型，后续展示层再决定格式化方式。
        if isinstance(row, dict):
            return FieldProgressRecord(
                task_id=row["task_id"],
                row_index=row["row_index"],
                field_name=row["field_name"],
                status=row["status"],
                evidence=self.loads_json(row.get("evidence_json")),
                updated_at=row.get("updated_at"),
            )
        task_id, row_index, field_name, status, evidence_json, updated_at = row
        return FieldProgressRecord(
            task_id=task_id,
            row_index=row_index,
            field_name=field_name,
            status=status,
            evidence=self.loads_json(evidence_json),
            updated_at=updated_at,
        )
