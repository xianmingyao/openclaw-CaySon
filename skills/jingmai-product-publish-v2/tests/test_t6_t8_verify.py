from __future__ import annotations

from unittest.mock import MagicMock

from jingmai_publish import cli
from jingmai_publish.services.desktop_verify import DesktopVerificationService
from jingmai_publish.services.jingmai_workflow import WorkflowStepResult


def _build_workflow_with_tuning():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_adapter.tuning.window_keywords = ["京麦"]
    fake_workflow.window_manager.adapter = fake_adapter
    fake_workflow.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1",
        success=True,
        page_state="jingmai_home",
        window_handle="2002",
        screenshot_path="a.png",
        message="ok",
    )
    return fake_workflow


def test_desktop_verification_service_t6_main_image():
    fake_workflow = _build_workflow_with_tuning()
    fake_workflow.run_t6_upload_main_image.return_value = WorkflowStepResult(
        step_id="T6-MAIN-IMAGE",
        success=True,
        page_state="main_image_uploaded",
        window_handle="2002",
        screenshot_path="b.png",
        message="ok",
    )

    service = DesktopVerificationService.__new__(DesktopVerificationService)
    service.workflow_service = fake_workflow
    result = service.run("t6-main-image", debug=False, image_path="demo.png")

    assert result["t6_main_image"]["step_id"] == "T6-MAIN-IMAGE"
    assert result["t6_main_image"]["success"] is True


def test_desktop_verification_service_t6_transparent_image():
    fake_workflow = _build_workflow_with_tuning()
    fake_workflow.run_t6_upload_transparent_image.return_value = WorkflowStepResult(
        step_id="T6-TRANSPARENT-IMAGE",
        success=True,
        page_state="transparent_image_uploaded",
        window_handle="2002",
        screenshot_path="b.png",
        message="ok",
    )

    service = DesktopVerificationService.__new__(DesktopVerificationService)
    service.workflow_service = fake_workflow
    result = service.run("t6-transparent-image", debug=False, transparent_image_path="transparent.png")

    assert result["t6_transparent_image"]["step_id"] == "T6-TRANSPARENT-IMAGE"
    assert result["t6_transparent_image"]["success"] is True


def test_desktop_verification_service_t6_detail_editor():
    fake_workflow = _build_workflow_with_tuning()
    fake_workflow.run_t6_fill_detail_editor.return_value = WorkflowStepResult(
        step_id="T6-DETAIL-EDITOR",
        success=True,
        page_state="detail_content_written",
        window_handle="2002",
        screenshot_path="b.png",
        message="ok",
    )

    service = DesktopVerificationService.__new__(DesktopVerificationService)
    service.workflow_service = fake_workflow
    result = service.run("t6-detail-editor", debug=False, detail_content="<p>详情</p>")

    assert result["t6_detail_editor"]["step_id"] == "T6-DETAIL-EDITOR"
    assert result["t6_detail_editor"]["success"] is True


def test_desktop_verification_service_t8_save_draft():
    fake_workflow = _build_workflow_with_tuning()
    fake_workflow.run_t8_save_draft.return_value = WorkflowStepResult(
        step_id="T8-SAVE-DRAFT",
        success=True,
        page_state="draft_saved",
        window_handle="2002",
        screenshot_path="b.png",
        message="ok",
    )

    service = DesktopVerificationService.__new__(DesktopVerificationService)
    service.workflow_service = fake_workflow
    result = service.run("t8-save-draft", debug=False)

    assert result["t8_save_draft"]["step_id"] == "T8-SAVE-DRAFT"
    assert result["t8_save_draft"]["success"] is True


def test_desktop_verification_service_t8_publish_product():
    fake_workflow = _build_workflow_with_tuning()
    fake_workflow.run_t8_publish_product.return_value = WorkflowStepResult(
        step_id="T8-PUBLISH-PRODUCT",
        success=True,
        page_state="publish_submitted",
        window_handle="2002",
        screenshot_path="b.png",
        message="ok",
    )

    service = DesktopVerificationService.__new__(DesktopVerificationService)
    service.workflow_service = fake_workflow
    result = service.run("t8-publish-product", debug=False)

    assert result["t8_publish_product"]["step_id"] == "T8-PUBLISH-PRODUCT"
    assert result["t8_publish_product"]["success"] is True


def test_cli_parser_supports_new_t6_t8_steps():
    parser = cli.build_parser()
    t6_args = parser.parse_args(["run-desktop-check", "--step", "t6-detail-editor", "--detail-content", "<p>1</p>"])
    t8_args = parser.parse_args(["run-desktop-check", "--step", "t8-save-draft"])
    publish_args = parser.parse_args(["run-desktop-check", "--step", "t8-publish-product"])

    assert t6_args.step == "t6-detail-editor"
    assert t6_args.detail_content == "<p>1</p>"
    assert t8_args.step == "t8-save-draft"
    assert publish_args.step == "t8-publish-product"
