"""SELECT_ROW 节点入口。"""

from __future__ import annotations

from jm_ufo_agent.workflow.nodes.dryrun import noop_node
from jm_ufo_agent.workflow.state import GraphState


async def select_row_node(state: GraphState) -> list[str]:
    """记录选行节点执行证据。"""

    # 当前 row82 种子规则由 DryRunWorkflow._select_row 执行。
    # 该入口用于满足节点文件拆分和后续 LangGraph 迁移。
    # 不在这里改 row_index，避免和现有恢复规则出现两套来源。
    return await noop_node(state, "SELECT_ROW", "select_row_node")


__all__ = ["select_row_node"]
