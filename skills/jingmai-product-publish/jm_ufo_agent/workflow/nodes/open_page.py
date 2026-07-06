"""OPEN_PAGE 节点入口。"""

from __future__ import annotations

from jm_ufo_agent.workflow.nodes.dryrun import noop_node
from jm_ufo_agent.workflow.state import GraphState


async def open_page_node(state: GraphState) -> list[str]:
    """记录打开新增商品页节点证据。"""

    # 真实实现需要接入京麦窗口和 _expected_window_title 校验。
    # 本地安全实现不触碰桌面窗口，只写入明确的 noop 证据。
    # 这样测试能区分“节点存在”与“真实京麦动作已完成”。
    return await noop_node(state, "OPEN_PAGE", "open_page")


__all__ = ["open_page_node"]
