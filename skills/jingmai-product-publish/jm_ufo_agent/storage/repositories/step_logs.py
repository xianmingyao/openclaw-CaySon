"""节点执行日志 Repository。"""

from __future__ import annotations

from jm_ufo_agent.storage.repositories.base import SQLRepository
from jm_ufo_agent.storage.repositories.models import StepLogRecord


class StepLogRepository(SQLRepository):
    """写入 `jm_step_logs` 表。"""

    async def add(self, record: StepLogRecord) -> None:
        """追加一条节点执行日志。"""

        # step_logs 是只追加日志，不覆盖历史执行。
        # duration_ms 和 error 都允许为空，方便节点开始/结束两种场景复用。
        # metadata_json 保存截图路径、OCR 摘要、外部调用 ID 等补充信息。
        await self.execute(
            """
            INSERT INTO jm_step_logs (
                task_id, row_index, node_name, status, duration_ms, error, metadata_json
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                record.task_id,
                record.row_index,
                record.node_name,
                record.status,
                record.duration_ms,
                record.error,
                self.dumps_json(record.metadata),
            ),
        )
