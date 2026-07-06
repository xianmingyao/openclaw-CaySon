"""COMMIT_ROW 节点入口。"""

from __future__ import annotations

from jm_ufo_agent.workflow.nodes.dryrun import noop_node
from jm_ufo_agent.workflow.state import GraphState, WorkflowStatus


async def commit_row_node(state: GraphState) -> list[str]:
    """记录当前 row 已完成。"""

    # commit_row 只能在草稿验证通过后执行。
    # dry-run 主流程已经写 row_progress，这里只提供独立节点入口。
    # 状态设为 COMMITTED，便于单独测试该节点的输出。
    state.status = WorkflowStatus.COMMITTED
    return await noop_node(state, "COMMIT_ROW", "commit_row")


__all__ = ["commit_row_node"]
