"""MySQL checkpoint 保存器。"""

from __future__ import annotations

from typing import Any

from jm_ufo_agent.storage.repositories.models import TaskRecord
from jm_ufo_agent.storage.repositories.tasks import TaskRepository
from jm_ufo_agent.workflow.state import GraphState


class AsyncMySQLSaver:
    """LangGraph 风格的异步状态保存器。"""

    def __init__(self, task_repository: TaskRepository):
        """初始化保存器。"""

        # 保存器只依赖 TaskRepository，不直接持有数据库连接细节。
        # 这让测试可以传 fake repository，也让后续替换 LangGraph saver 更容易。
        # 每次 aput 都保存完整 GraphState 快照。
        self.task_repository = task_repository

    async def aput(self, state: GraphState) -> None:
        """保存当前工作流状态。"""

        # GraphState.to_dict() 产出可 JSON 序列化快照。
        # task status 使用 state.status.value，便于数据库查询。
        # current_row 对应 row_index，用于行级恢复。
        await self.task_repository.upsert(
            TaskRecord(
                task_id=state.task_id,
                status=state.status.value,
                current_row=state.row_index,
                state=state.to_dict(),
            )
        )

    async def aget(self, task_id: str) -> dict[str, Any] | None:
        """读取已保存的状态快照。"""

        # Repository 返回 TaskRecord，state 字段是 JSON dict。
        # 找不到记录时返回 None，调用方决定从头开始还是 halt。
        # 不在这里重建 GraphState，避免 schema 演进时耦合过深。
        record = await self.task_repository.get(task_id)
        if record is None:
            return None
        return record.state
