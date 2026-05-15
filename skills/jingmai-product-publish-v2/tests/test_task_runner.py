from __future__ import annotations

from unittest.mock import MagicMock

from jingmai_publish.services.jingmai_workflow import WorkflowStepResult
from jingmai_publish.services.task_runner import TaskRunner


def _build_runner():
    workflow = MagicMock()
    workflow.window_manager.adapter = MagicMock()
    return TaskRunner(workflow), workflow


def test_task_runner_runs_both_as_minimal_loop():
    runner, workflow = _build_runner()
    workflow.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1",
        success=True,
        page_state="jingmai_home",
        window_handle="2002",
        screenshot_path="a.png",
        message="ok-1",
    )
    workflow.run_t2_enter_publish_entry.return_value = WorkflowStepResult(
        step_id="T2",
        success=True,
        page_state="publish_entry",
        window_handle="2002",
        screenshot_path="b.png",
        message="ok-2",
    )

    result = runner.run("both", debug=False)

    assert result["t1"]["step_id"] == "T1"
    assert result["t2"]["step_id"] == "T2"
    assert result["session"]["completed_steps"] == ["T1", "T2"]
    assert result["session"]["page_state"] == "publish_entry"
    assert result["session"]["halted"] is False


def test_task_runner_stops_when_t1_fails_and_keeps_session_state():
    runner, workflow = _build_runner()
    workflow.run_t1_attach_window.side_effect = ValueError("window missing")
    workflow.window_manager.adapter.build_window_debug_snapshot.return_value = {"matched_windows": []}

    result = runner.run("both", debug=True)

    assert result["t1"]["success"] is False
    assert "t2" not in result
    assert result["session"]["halted"] is True
    assert result["debug"]["window_snapshot"]["matched_windows"] == []


def test_task_runner_runs_transparent_image_step():
    runner, workflow = _build_runner()
    workflow.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1",
        success=True,
        page_state="jingmai_home",
        window_handle="2002",
        screenshot_path="a.png",
        message="ok-1",
    )
    workflow.run_t6_upload_transparent_image.return_value = WorkflowStepResult(
        step_id="T6-TRANSPARENT-IMAGE",
        success=True,
        page_state="transparent_image_uploaded",
        window_handle="2002",
        screenshot_path="b.png",
        message="ok-2",
    )

    result = runner.run("t6-transparent-image", transparent_image_path="demo.png")

    assert result["t6_transparent_image"]["success"] is True
    workflow.run_t6_upload_transparent_image.assert_called_once_with("2002", "demo.png")


def test_task_runner_runs_detail_editor_step():
    runner, workflow = _build_runner()
    workflow.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1",
        success=True,
        page_state="jingmai_home",
        window_handle="2002",
        screenshot_path="a.png",
        message="ok-1",
    )
    workflow.run_t6_fill_detail_editor.return_value = WorkflowStepResult(
        step_id="T6-DETAIL-EDITOR",
        success=True,
        page_state="detail_content_written",
        window_handle="2002",
        screenshot_path="b.png",
        message="ok-2",
    )

    result = runner.run("t6-detail-editor", detail_content="<p>详情</p>")

    assert result["t6_detail_editor"]["success"] is True
    workflow.run_t6_fill_detail_editor.assert_called_once_with("2002", detail_content="<p>详情</p>")


def test_task_runner_runs_publish_step():
    runner, workflow = _build_runner()
    workflow.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1",
        success=True,
        page_state="jingmai_home",
        window_handle="2002",
        screenshot_path="a.png",
        message="ok-1",
    )
    workflow.run_t8_publish_product.return_value = WorkflowStepResult(
        step_id="T8-PUBLISH-PRODUCT",
        success=True,
        page_state="publish_submitted",
        window_handle="2002",
        screenshot_path="b.png",
        message="ok-2",
    )

    result = runner.run("t8-publish-product")

    assert result["t8_publish_product"]["success"] is True
    workflow.run_t8_publish_product.assert_called_once_with("2002")


def test_task_runner_retries_until_step_verified():
    runner, workflow = _build_runner()
    workflow.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1",
        success=True,
        page_state="jingmai_home",
        window_handle="2002",
        screenshot_path="a.png",
        message="ok-1",
    )
    workflow.run_t2_enter_publish_entry.side_effect = [
        WorkflowStepResult(
            step_id="T2",
            success=False,
            page_state="jingmai_home",
            window_handle="2002",
            screenshot_path="b1.png",
            message="first-fail",
        ),
        WorkflowStepResult(
            step_id="T2",
            success=True,
            page_state="publish_entry",
            window_handle="2002",
            screenshot_path="b2.png",
            message="second-ok",
        ),
    ]

    result = runner.run("both", debug=False)

    assert workflow.run_t2_enter_publish_entry.call_count == 2
    assert result["t2"]["success"] is True
    assert result["session"]["max_retry_count"] == 3
    t2_trace = [item for item in result["session"]["trace"] if item["planned_step"] == "t2"]
    assert len(t2_trace) == 2
    assert t2_trace[0]["verified"] is False
    assert "first-fail" in t2_trace[0]["failure_signature"]
    assert t2_trace[1]["verified"] is True
