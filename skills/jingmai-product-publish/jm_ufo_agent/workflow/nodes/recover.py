"""RECOVER 节点入口。"""

from __future__ import annotations

from jm_ufo_agent.workflow.nodes.dryrun import noop_node
from jm_ufo_agent.workflow.state import GraphState


async def recover_node(state: GraphState) -> list[str]:
    """记录恢复节点执行证据。"""

    # 字段级恢复当前由 DryRunWorkflow._recover_verified_fields 执行。
    # 独立节点文件先保留稳定入口，后续迁入真实 LangGraph 时可直接替换实现。
    # 这里不修改 verified_fields，避免和 repository 恢复逻辑重复。
    return await noop_node(state, "RECOVER", "recover")


__all__ = ["recover_node"]
