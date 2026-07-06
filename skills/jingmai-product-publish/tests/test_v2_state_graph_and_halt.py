from pathlib import Path

from jm_ufo_agent.agents.image_transform import ImageTransformAgent
from jm_ufo_agent.workflow.graph import DryRunWorkflow, build_state_graph
from jm_ufo_agent.workflow.state import GraphState, WorkflowStatus


def _complete_product():
    return {
        "title": "测试商品",
        "category": "工业品",
        "brand": "测试品牌",
        "sku": "sku-1",
        "jd_price": "100.00",
        "purchase_price": "95.00",
        "market_price": "117.65",
        "main_image": "main.png",
        "sub_images": ["sub-1.png"],
        "description": "测试描述",
        "weight": "1kg",
        "stock": "10",
    }


def test_build_state_graph_declares_eighteen_nodes():
    spec = build_state_graph()

    assert len(spec.node_order) == 18
    assert spec.node_order[0] == "BOOTSTRAP"
    assert spec.node_order[-1] == "HALT"
    assert spec.has_node("PREPARE_ASSETS")
    assert ("SAVE_DRAFT", "VERIFY_DRAFT") in spec.edges


def test_workflow_node_files_match_state_graph_nodes():
    spec = build_state_graph()
    node_files = {path.stem for path in Path("jm_ufo_agent/workflow/nodes").glob("*.py") if path.stem != "__init__"}

    expected_files = {node_name.lower() for node_name in spec.node_order}
    assert expected_files.issubset(node_files)


def test_graph_state_halt_records_evidence():
    state = GraphState(task_id="task-1", row_index=82, product={})
    state.current_node = "ASSERT_PAGE_SIGNATURE"

    state.halt("页面签名不一致", {"screenshot_path": "artifacts/a.png", "page_signature": "sig-1"})

    assert state.status == WorkflowStatus.HALTED
    assert state.blockers == ["页面签名不一致"]
    assert state.evidence["halt_evidence"][0]["node"] == "ASSERT_PAGE_SIGNATURE"
    assert state.evidence["halt_evidence"][0]["details"]["page_signature"] == "sig-1"


async def test_vlm_three_failures_halt_current_row():
    async def failing_handler(context):
        raise RuntimeError("vlm unavailable")

    workflow = DryRunWorkflow(image_transform=ImageTransformAgent(handler=failing_handler))
    state = GraphState(task_id="task-1", row_index=82, product=_complete_product())

    result = await workflow.run(state)

    assert result.status == WorkflowStatus.HALTED
    assert result.current_node == "PREPARE_ASSETS"
    assert result.evidence["prepare_assets"]["halt_reason"] == "vlm_transform_failed"
    assert len(result.evidence["prepare_assets"]["attempts"]) == 3
    assert result.evidence["halt_evidence"][0]["node"] == "PREPARE_ASSETS"
