"""行级断点续传 Repository。"""

from __future__ import annotations

from typing import Any

from jm_ufo_agent.storage.repositories.base import SQLRepository
from jm_ufo_agent.storage.repositories.models import RowExecutionRecord


class RowExecutionRepository(SQLRepository):
    """读写 `jm_row_execution_states` 表。"""

    async def upsert(self, record: RowExecutionRecord) -> None:
        """插入或更新行级执行状态。"""

        # task_id + row_index 是行级恢复的唯一键。
        # draft_evidence 记录草稿保存/验证证据，用于 row82 特殊恢复判断。
        # completion/review 明细都写 JSON，便于人工复盘失败原因。
        await self.execute(
            """
            INSERT INTO jm_row_execution_states (
                task_id, row_index, status, current_field, retry_count, last_error,
                page_signature, completion_score, completion_passed, completion_details_json,
                evaluation_loop_count, review_score, review_decision, review_details_json,
                draft_evidence_json
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                status = VALUES(status),
                current_field = VALUES(current_field),
                retry_count = VALUES(retry_count),
                last_error = VALUES(last_error),
                page_signature = VALUES(page_signature),
                completion_score = VALUES(completion_score),
                completion_passed = VALUES(completion_passed),
                completion_details_json = VALUES(completion_details_json),
                evaluation_loop_count = VALUES(evaluation_loop_count),
                review_score = VALUES(review_score),
                review_decision = VALUES(review_decision),
                review_details_json = VALUES(review_details_json),
                draft_evidence_json = VALUES(draft_evidence_json),
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                record.task_id,
                record.row_index,
                record.status,
                record.current_field,
                record.retry_count,
                record.last_error,
                record.page_signature,
                record.completion_score,
                1 if record.completion_passed else 0,
                self.dumps_json(record.completion_details),
                record.evaluation_loop_count,
                record.review_score,
                record.review_decision,
                self.dumps_json(record.review_details),
                self.dumps_json(record.draft_evidence),
            ),
        )

    async def get(self, task_id: str, row_index: int) -> RowExecutionRecord | None:
        """读取单行执行状态。"""

        # SELECT 字段顺序必须和 _row_to_record 的 tuple 解包一致。
        # dict row 和 tuple row 都支持，便于测试和不同 MySQL cursor。
        # 不存在时返回 None，由 workflow 按新行处理。
        row = await self.fetchone(
            """
            SELECT task_id, row_index, status, current_field, retry_count, last_error,
                   page_signature, completion_score, completion_passed, completion_details_json,
                   evaluation_loop_count, review_score, review_decision, review_details_json,
                   draft_evidence_json, updated_at
            FROM jm_row_execution_states
            WHERE task_id = %s AND row_index = %s
            """,
            (task_id, row_index),
        )
        if row is None:
            return None
        return self._row_to_record(row)

    async def list_committed_rows(self, task_id: str) -> set[int]:
        """列出已经提交完成的行号。"""

        # 行级恢复只跳过 committed 行，draft_saved 仍需 VERIFY_DRAFT/COMMIT_ROW。
        # 返回 set 便于 SELECT_ROW 快速判断是否已处理。
        # 该方法也服务 row82 特殊规则的证据检查。
        rows = await self.fetchall(
            """
            SELECT row_index
            FROM jm_row_execution_states
            WHERE task_id = %s AND status = 'committed'
            """,
            (task_id,),
        )
        return {int(row["row_index"] if isinstance(row, dict) else row[0]) for row in rows}

    async def has_draft_evidence(self, task_id: str, row_index: int) -> bool:
        """判断某行是否已有草稿证据。"""

        # row82 恢复规则要求 row5-row7 草稿证据齐全。
        # 只看 status 不够，必须确认 draft_evidence_json 非空。
        # JSON 解析失败不吞掉，让坏证据尽早暴露。
        record = await self.get(task_id, row_index)
        return bool(record and record.draft_evidence)

    async def next_row_after_seed(self, task_id: str, requested_row: int, seed_rows: tuple[int, ...] = (5, 6, 7), target_row: int = 82) -> int:
        """根据 row5-row7 草稿证据推断 row82。"""

        # 该规则来自当前任务验收 F16，只在请求 seed 区间时触发。
        # 三行草稿证据齐全才跳到 row82，否则保持用户请求行不变。
        # 真实批量调度后续可替换成更通用的 SELECT_ROW 策略。
        if requested_row not in seed_rows:
            return requested_row
        ready = [await self.has_draft_evidence(task_id, row) for row in seed_rows]
        return target_row if all(ready) else requested_row

    def _row_to_record(self, row: Any) -> RowExecutionRecord:
        """把数据库行转换为 `RowExecutionRecord`。"""

        # dict row 适配测试 fake connection 和 DictCursor。
        # tuple row 适配默认 cursor，字段顺序由 SELECT 固定。
        # 布尔值从 MySQL 的 0/1 转成 Python bool。
        if isinstance(row, dict):
            return RowExecutionRecord(
                task_id=row["task_id"],
                row_index=int(row["row_index"]),
                status=row["status"],
                current_field=row.get("current_field"),
                retry_count=int(row.get("retry_count") or 0),
                last_error=row.get("last_error"),
                page_signature=row.get("page_signature"),
                completion_score=float(row.get("completion_score") or 0.0),
                completion_passed=bool(row.get("completion_passed")),
                completion_details=self.loads_json(row.get("completion_details_json")),
                evaluation_loop_count=int(row.get("evaluation_loop_count") or 0),
                review_score=float(row.get("review_score") or 0.0),
                review_decision=row.get("review_decision") or "",
                review_details=self.loads_json(row.get("review_details_json")),
                draft_evidence=self.loads_json(row.get("draft_evidence_json")),
                updated_at=row.get("updated_at"),
            )
        (
            task_id,
            row_index,
            status,
            current_field,
            retry_count,
            last_error,
            page_signature,
            completion_score,
            completion_passed,
            completion_details_json,
            evaluation_loop_count,
            review_score,
            review_decision,
            review_details_json,
            draft_evidence_json,
            updated_at,
        ) = row
        return RowExecutionRecord(
            task_id=task_id,
            row_index=int(row_index),
            status=status,
            current_field=current_field,
            retry_count=int(retry_count or 0),
            last_error=last_error,
            page_signature=page_signature,
            completion_score=float(completion_score or 0.0),
            completion_passed=bool(completion_passed),
            completion_details=self.loads_json(completion_details_json),
            evaluation_loop_count=int(evaluation_loop_count or 0),
            review_score=float(review_score or 0.0),
            review_decision=review_decision or "",
            review_details=self.loads_json(review_details_json),
            draft_evidence=self.loads_json(draft_evidence_json),
            updated_at=updated_at,
        )
