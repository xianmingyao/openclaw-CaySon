"""CALIBRATE_LOCATORS 节点入口。"""

from __future__ import annotations

from jm_ufo_agent.workflow.nodes.dryrun import noop_node
from jm_ufo_agent.workflow.state import GraphState


async def calibrate_locators_node(state: GraphState) -> list[str]:
    """记录 locator 校准节点证据。"""

    # 真实实现会写入 locator_cache，并结合 OCR/VLM 重新定位字段。
    # 当前只写入本地安全证据，不调用 VLM 或真实截图。
    # 后续接入时应保持输入输出仍然只通过 GraphState 传递。
    return await noop_node(state, "CALIBRATE_LOCATORS", "calibrate_locators")


__all__ = ["calibrate_locators_node"]
