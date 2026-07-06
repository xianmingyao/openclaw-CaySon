"""ASSERT_PAGE_SIGNATURE 节点入口。"""

from __future__ import annotations

from jm_ufo_agent.workflow.nodes.dryrun import noop_node
from jm_ufo_agent.workflow.state import GraphState


async def assert_page_signature_node(state: GraphState) -> list[str]:
    """记录页面签名校验节点证据。"""

    # 真实实现需要比较页面 signature、窗口标题和局部截图相似度。
    # 当前先保留节点边界，避免后续把校验散落在多个策略里。
    # 失败 halt 的现场证据会统一进入 GraphState.halt_evidence。
    return await noop_node(state, "ASSERT_PAGE_SIGNATURE", "page_signature")


__all__ = ["assert_page_signature_node"]
