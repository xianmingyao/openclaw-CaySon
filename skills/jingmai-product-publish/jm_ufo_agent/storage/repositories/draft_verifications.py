"""草稿验证 Repository。"""

from __future__ import annotations

from jm_ufo_agent.storage.repositories.base import SQLRepository
from jm_ufo_agent.storage.repositories.models import DraftVerificationRecord


class DraftVerificationRepository(SQLRepository):
    """读写 `jm_draft_verifications` 表。"""

    async def add(self, record: DraftVerificationRecord) -> None:
        """追加一条草稿验证结果。"""

        # 草稿验证是保存草稿后的关键证据，不能覆盖历史。
        # verification_result 明确保存 passed/failed/pending 等状态。
        # diff_json 用于记录列表页读回值和预期值的差异。
        await self.execute(
            """
            INSERT INTO jm_draft_verifications (
                product_id, task_id, row_index, draft_url, completion_score, verification_result, diff_json
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                record.product_id,
                record.task_id,
                record.row_index,
                record.draft_url,
                record.completion_score,
                record.verification_result,
                self.dumps_json(record.diff),
            ),
        )

    async def latest_for_row(self, task_id: str, row_index: int) -> DraftVerificationRecord | None:
        """读取某行最新一条草稿验证结果。"""

        # row82 恢复和人工复盘都需要快速看到最后一次验证结果。
        # 按 id 倒序读取一条，避免重复扫描全部历史记录。
        # 没有记录时返回 None，不把未验证当成失败。
        row = await self.fetchone(
            """
            SELECT product_id, task_id, row_index, draft_url, completion_score, verification_result, diff_json
            FROM jm_draft_verifications
            WHERE task_id = %s AND row_index = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (task_id, row_index),
        )
        if row is None:
            return None
        if isinstance(row, dict):
            return DraftVerificationRecord(
                product_id=row.get("product_id"),
                task_id=row["task_id"],
                row_index=int(row["row_index"]),
                draft_url=row.get("draft_url"),
                completion_score=float(row.get("completion_score") or 0.0),
                verification_result=row["verification_result"],
                diff=self.loads_json(row.get("diff_json")),
            )
        product_id, task_id, row_index, draft_url, completion_score, verification_result, diff_json = row
        return DraftVerificationRecord(
            task_id=task_id,
            row_index=int(row_index),
            verification_result=verification_result,
            product_id=product_id,
            draft_url=draft_url,
            completion_score=float(completion_score or 0.0),
            diff=self.loads_json(diff_json),
        )
