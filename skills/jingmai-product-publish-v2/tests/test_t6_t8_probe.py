from unittest.mock import MagicMock

from jingmai_publish.services.desktop_verify import DesktopVerificationService
from jingmai_publish.services.jingmai_workflow import WorkflowStepResult
from jingmai_publish import cli


def test_desktop_verification_service_t6_probe():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_workflow.window_manager.adapter = fake_adapter
    fake_workflow.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1",
        success=True,
        page_state="jingmai_home",
        window_handle="2002",
        screenshot_path="a.png",
        message="ok",
    )
    fake_workflow.run_t6_probe.return_value = WorkflowStepResult(
        step_id="T6-PROBE",
        success=True,
        page_state="media_ready",
        window_handle="2002",
        screenshot_path="b.png",
        message="ok",
    )

    service = DesktopVerificationService.__new__(DesktopVerificationService)
    service.workflow_service = fake_workflow
    result = service.run("t6-probe", debug=False)
    assert result["t6_probe"]["step_id"] == "T6-PROBE"
    assert result["t6_probe"]["success"] is True


def test_desktop_verification_service_t8_probe():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_workflow.window_manager.adapter = fake_adapter
    fake_workflow.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1",
        success=True,
        page_state="jingmai_home",
        window_handle="2002",
        screenshot_path="a.png",
        message="ok",
    )
    fake_workflow.run_t8_probe.return_value = WorkflowStepResult(
        step_id="T8-PROBE",
        success=True,
        page_state="submit_ready",
        window_handle="2002",
        screenshot_path="b.png",
        message="ok",
    )

    service = DesktopVerificationService.__new__(DesktopVerificationService)
    service.workflow_service = fake_workflow
    result = service.run("t8-probe", debug=False)
    assert result["t8_probe"]["step_id"] == "T8-PROBE"
    assert result["t8_probe"]["success"] is True


def test_cli_parser_supports_t6_and_t8_probe_steps():
    parser = cli.build_parser()
    t6_args = parser.parse_args(["run-desktop-check", "--step", "t6-probe"])
    t8_args = parser.parse_args(["run-desktop-check", "--step", "t8-probe"])
    assert t6_args.step == "t6-probe"
    assert t8_args.step == "t8-probe"
