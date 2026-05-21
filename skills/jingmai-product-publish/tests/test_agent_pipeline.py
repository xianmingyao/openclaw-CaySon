"""test_agent_pipeline.py — AgentPipeline 测试。
BL-091: 验证全管线集成、T1 失败停止、重试成功、结果结构兼容。
"""

from __future__ import annotations

from unittest.mock import MagicMock

from jingmai_publish.agent import REGISTRY, AgentExecutor, AgentPipeline, AgentReflection
from jingmai_publish.services.jingmai_workflow import WorkflowStepResult


class FakeSession:
    """最小 session 模拟类。"""

    def __init__(self) -> None:
        self.window_handle = None
        self.trace: list[dict] = []
        self.completed_steps: list[str] = []
        self.page_state = None
        self.halted = False
        self.last_message = None
        self.max_retry_count = 3


def _build_pipeline(service):
    executor = AgentExecutor(service)
    reflection = AgentReflection()
    return AgentPipeline(REGISTRY, executor, reflection)


def _full_publish_params():
    return {
        "title": "测试商品标题",
        "model": "XH-001",
        "required_attribute": "10A",
        "market_price": "100",
        "purchase_price": "80",
        "jd_price": "99",
        "current": "10A",
        "weight": "1.2",
        "length_mm": "100",
        "width_mm": "80",
        "height_mm": "60",
        "factory_inventory": "10",
        "image_path": "main.png",
        "transparent_image_path": "transparent.png",
        "detail_content": "<p>detail</p>",
        "sale_unit": "个",
        "package_type": "纸箱",
        "delivery_mark": "现货",
        "package_list": "主机*1",
        "warranty_period": "365",
    }


def _stub_full_publish_success(service):
    service.run_t3_confirm_category.return_value = WorkflowStepResult(
        step_id="T3", success=True, page_state="category_confirmed", window_handle="2002",
    )
    service.run_t4_fill_base_info.return_value = WorkflowStepResult(
        step_id="T4", success=True, page_state="base_info_completed", window_handle="2002",
    )
    service.run_t5_fill_required_fields.return_value = WorkflowStepResult(
        step_id="T5-REQUIRED-FIELDS", success=True, page_state="required_fields_completed", window_handle="2002",
    )
    service.run_t6_upload_main_image.return_value = WorkflowStepResult(
        step_id="T6-MAIN-IMAGE", success=True, page_state="main_image_uploaded", window_handle="2002",
    )
    service.run_t6_upload_transparent_image.return_value = WorkflowStepResult(
        step_id="T6-TRANSPARENT-IMAGE", success=True, page_state="transparent_image_uploaded", window_handle="2002",
    )
    service.run_t6_fill_detail_editor.return_value = WorkflowStepResult(
        step_id="T6-DETAIL-EDITOR", success=True, page_state="detail_editor_completed", window_handle="2002",
    )
    service.run_t7_fill_logistics_fields.return_value = WorkflowStepResult(
        step_id="T7", success=True, page_state="logistics_completed", window_handle="2002",
    )
    service.run_t8_save_draft.return_value = WorkflowStepResult(
        step_id="T8-SAVE-DRAFT", success=True, page_state="draft_saved", window_handle="2002",
    )


def test_pipeline_both_full_flow():
    """both 全管线：T1 + T2 均成功，结果结构兼容。"""
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1", success=True, page_state="jingmai_home", window_handle="2002",
    )
    service.run_t2_enter_publish_entry.return_value = WorkflowStepResult(
        step_id="T2", success=True, page_state="publish_entry", window_handle="2002",
    )
    _stub_full_publish_success(service)

    pipeline = _build_pipeline(service)
    session = FakeSession()
    results = pipeline.run("both", session, _full_publish_params())

    assert "t1" in results
    assert "t2" in results
    assert results["t1"]["success"] is True
    assert results["t2"]["success"] is True
    assert "t8_save_draft" in results
    assert session.completed_steps == [
        "T1",
        "T2",
        "T3",
        "T4",
        "T5-REQUIRED-FIELDS",
        "T6-MAIN-IMAGE",
        "T6-TRANSPARENT-IMAGE",
        "T6-DETAIL-EDITOR",
        "T7",
        "T8-SAVE-DRAFT",
    ]
    assert session.halted is False


def test_pipeline_t1_failure_stops_plan():
    """T1 失败应 halted=True，不执行后续步骤。"""
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.side_effect = ValueError("window missing")

    pipeline = _build_pipeline(service)
    session = FakeSession()
    results = pipeline.run("t2", session, {})

    assert results["t1"]["success"] is False
    assert "t2" not in results
    assert session.halted is True


def test_pipeline_retry_on_failure():
    """首次失败后重试，第二次成功。"""
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1", success=True, page_state="jingmai_home", window_handle="2002",
    )
    service.run_t2_enter_publish_entry.side_effect = [
        WorkflowStepResult(step_id="T2", success=False, page_state="error", message="fail-1"),
        WorkflowStepResult(step_id="T2", success=True, page_state="publish_entry", window_handle="2002"),
    ]

    pipeline = _build_pipeline(service)
    session = FakeSession()
    results = pipeline.run("t2", session, {})

    assert service.run_t2_enter_publish_entry.call_count == 2
    assert results["t2"]["success"] is True
    assert len(session.trace) >= 2  # at least 2 trace entries (T1 + T2)
    t2_trace = [t for t in session.trace if t["planned_step"] == "t2"]
    assert len(t2_trace) == 2
    assert t2_trace[0]["verified"] is False
    assert t2_trace[1]["verified"] is True


def test_pipeline_trace_entries_format():
    """trace 条目格式应与原 TaskRunner 兼容。"""
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1", success=True, page_state="home", window_handle="2002",
    )

    pipeline = _build_pipeline(service)
    session = FakeSession()
    pipeline.run("t1", session, {})

    assert len(session.trace) == 1
    entry = session.trace[0]
    assert entry["planned_step"] == "t1"
    assert entry["attempt_no"] == 1
    assert "before_state" in entry
    assert "after_state" in entry
    assert "verified" in entry


def test_pipeline_exception_wraps_as_workflow_result():
    """异常应被包装为 WorkflowStepResult(success=False)。"""
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.side_effect = RuntimeError("unexpected crash")

    pipeline = _build_pipeline(service)
    session = FakeSession()
    results = pipeline.run("t1", session, {})

    assert results["t1"]["success"] is False
    assert results["t1"]["page_state"] == "error"
    assert "unexpected crash" in results["t1"]["message"]


def test_pipeline_result_structure_matches_original():
    """结果结构应与原 TaskRunner.run() 兼容。"""
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1", success=True, page_state="jingmai_home", window_handle="2002",
    )
    service.run_t2_enter_publish_entry.return_value = WorkflowStepResult(
        step_id="T2", success=True, page_state="publish_entry", window_handle="2002",
    )
    _stub_full_publish_success(service)

    pipeline = _build_pipeline(service)
    session = FakeSession()
    results = pipeline.run("both", session, _full_publish_params())

    # 原 TaskRunner 返回结构中有 't1' 和 't2' 键
    assert "t1" in results
    assert "t2" in results
    assert "t8_save_draft" in results
    assert results["t1"]["step_id"] == "T1"
    assert results["t2"]["step_id"] == "T2"
    assert results["t1"]["success"] is True
    assert results["t2"]["success"] is True
