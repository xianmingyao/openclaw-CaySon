from __future__ import annotations

from unittest.mock import MagicMock

import pytest

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


def test_task_runner_runs_detail_editor_step_from_detail_html():
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

    result = runner.run("t6-detail-editor", detail_html="<section>京东图文详情</section>")

    assert result["t6_detail_editor"]["success"] is True
    workflow.run_t6_fill_detail_editor.assert_called_once_with(
        "2002",
        detail_content="<section>京东图文详情</section>",
    )


def test_task_runner_runs_detail_editor_step_from_file(tmp_path):
    content_file = tmp_path / "detail.html"
    content_file.write_text("<section>文件详情</section>", encoding="utf-8")
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

    runner.run("t6-detail-editor", detail_content_file=str(content_file))

    workflow.run_t6_fill_detail_editor.assert_called_once_with("2002", detail_content="<section>文件详情</section>")


def test_task_runner_runs_detail_editor_step_from_jd_url(monkeypatch):
    class DummyFetchService:
        def __init__(self, upload_job_repo, snapshot_repo, runtime_log_repo) -> None:
            self.upload_job_repo = upload_job_repo
            self.snapshot_repo = snapshot_repo
            self.runtime_log_repo = runtime_log_repo

        def fetch_product_payload(self, jd_item_url: str) -> dict[str, object]:
            return {
                "title": "京东商品",
                "detail_html": '<section><img src="https://img14.360buyimg.com/n1/demo.jpg" /></section>',
                "detail_text": "京东详情文字",
                "images": [],
            }

        @staticmethod
        def build_detail_editor_content(payload: dict[str, object]) -> str | None:
            return payload["detail_html"]

    monkeypatch.setattr("jingmai_publish.services.task_runner.JDProductFetchService", DummyFetchService)
    monkeypatch.setattr("jingmai_publish.services.jd_fetch.JDProductFetchService", DummyFetchService)
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

    runner.run("t6-detail-editor", jd_item_url="https://item.jd.com/16793098028.html")

    workflow.run_t6_fill_detail_editor.assert_called_once_with(
        "2002",
        detail_content='<section><img src="https://img14.360buyimg.com/n1/demo.jpg" /></section>',
    )


def test_task_runner_rejects_bl0883_probe_detail_content():
    runner, workflow = _build_runner()
    workflow.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1",
        success=True,
        page_state="jingmai_home",
        window_handle="2002",
        screenshot_path="a.png",
        message="ok-1",
    )

    with pytest.raises(ValueError, match="probe text"):
        runner.run("t6-detail-editor", detail_content="BL-088-3 command final pass 2026-05-16")


def test_task_runner_publish_step_requires_confirmation():
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
        success=False,
        page_state="publish_guard_required",
        window_handle="2002",
        screenshot_path="b.png",
        message="guard",
    )

    result = runner.run("t8-publish-product")

    assert result["t8_publish_product"]["success"] is False
    workflow.run_t8_publish_product.assert_called_once_with("2002", confirm_publish=None)


def test_task_runner_runs_publish_step_with_confirmation():
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

    result = runner.run("t8-publish-product", confirm_publish=True)

    assert result["t8_publish_product"]["success"] is True
    workflow.run_t8_publish_product.assert_called_once_with("2002", confirm_publish=True)


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
