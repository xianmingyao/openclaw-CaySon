"""任务 Repository。"""

from __future__ import annotations

from typing import Any

from jm_ufo_agent.storage.repositories.base import SQLRepository
from jm_ufo_agent.storage.repositories.models import TaskRecord


class TaskRepository(SQLRepository):
    """读写 `jm_tasks` 表。"""

    async def upsert(self, record: TaskRecord) -> None:
        """插入或更新任务状态。

        # task_id 是业务主键，重复写入时更新状态和当前行。
        # state_json 保存 LangGraph 状态快照，用于任务级恢复。
        # updated_at 由数据库刷新，避免多机器时间不一致。
        """

        await self.execute(
            """
            INSERT INTO jm_tasks (task_id, status, current_row, workflow_version, state_json)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                status = VALUES(status),
                current_row = VALUES(current_row),
                workflow_version = VALUES(workflow_version),
                state_json = VALUES(state_json),
                updated_at = CURRENT_TIMESTAMP
            """,
            (record.task_id, record.status, record.current_row, record.workflow_version, self.dumps_json(record.state)),
        )

    async def get(self, task_id: str) -> TaskRecord | None:
        """按任务 ID 查询任务。"""

        row = await self.fetchone(
            "SELECT task_id, status, current_row, workflow_version, state_json FROM jm_tasks WHERE task_id = %s",
            (task_id,),
        )
        if row is None:
            return None
        return self._row_to_record(row)

    def _row_to_record(self, row: Any) -> TaskRecord:
        """把数据库行转换为 `TaskRecord`。"""

        # fake connection 和部分驱动会返回 dict，优先按列名读取。
        # asyncmy 默认更常见的是 tuple，所以后面保留位置解包。
        # state_json 始终通过 loads_json 还原，避免调用方拿到字符串状态。
        if isinstance(row, dict):
            return TaskRecord(
                task_id=row["task_id"],
                status=row["status"],
                current_row=row.get("current_row"),
                workflow_version=row.get("workflow_version", "v2.0.0"),
                state=self.loads_json(row.get("state_json")),
            )
        task_id, status, current_row, workflow_version, state_json = row
        return TaskRecord(task_id=task_id, status=status, current_row=current_row, workflow_version=workflow_version, state=self.loads_json(state_json))
