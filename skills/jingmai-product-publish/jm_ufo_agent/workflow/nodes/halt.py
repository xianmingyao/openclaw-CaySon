"""HALT 节点入口。"""

from __future__ import annotations

from jm_ufo_agent.workflow.state import GraphState


async def halt_node(state: GraphState) -> list[str]:
    """记录工作流已经进入中止终态。"""

    # HALT 是终态节点，不再尝试保存草稿或提交 row。
    # 如果此前已经有 blockers，这里不重复添加阻断原因。
    # 如果没有 blockers，则补一个通用原因，避免人工接管时缺少说明。
    state.current_node = "HALT"
    if not state.blockers:
        state.halt("工作流进入 HALT 但缺少上游阻断原因")
    else:
        state.add_evidence("halt", {"blockers": list(state.blockers)})
    return ["HALT"]


__all__ = ["halt_node"]
