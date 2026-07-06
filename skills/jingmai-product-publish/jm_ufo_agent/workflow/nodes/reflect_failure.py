"""REFLECT_FAILURE 节点入口。"""

from __future__ import annotations

from jm_ufo_agent.workflow.nodes.dryrun import noop_node
from jm_ufo_agent.workflow.state import GraphState


async def reflect_failure_node(state: GraphState) -> list[str]:
    """记录失败反思节点证据。"""

    # 真实实现会把 failure reflections 写入 Milvus 或本地知识库。
    # 当前不访问向量库，只保留节点入口和证据键。
    # 这样后续接入检索时不会改变上游路由结构。
    return await noop_node(state, "REFLECT_FAILURE", "reflect_failure")


__all__ = ["reflect_failure_node"]
