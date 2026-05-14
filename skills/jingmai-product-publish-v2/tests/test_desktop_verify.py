from unittest.mock import MagicMock

from jingmai_publish.services.desktop_verify import DesktopVerificationService
from jingmai_publish.services.jingmai_workflow import WorkflowStepResult
from jingmai_publish import cli


def test_desktop_verification_service_run_both():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_adapter.build_window_debug_snapshot.return_value = {"matched_windows": [{"title": "京麦工作台"}]}
    fake_adapter.list_candidate_controls.return_value = [{"text": "发布商品", "class_name": "Button"}]
    fake_adapter.build_click_diagnostics.return_value = {"attempts": [{"strategy": "preferred_class_then_alias"}]}
    fake_workflow.window_manager.adapter = fake_adapter
    fake_workflow.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1",
        success=True,
        page_state="jingmai_home",
        window_handle="2002",
        screenshot_path="a.png",
        message="ok",
    )
    fake_workflow.run_t2_enter_publish_entry.return_value = WorkflowStepResult(
        step_id="T2",
        success=True,
        page_state="publish_entry",
        window_handle="2002",
        screenshot_path="b.png",
        message="ok",
    )

    service = DesktopVerificationService.__new__(DesktopVerificationService)
    service.workflow_service = fake_workflow
    result = service.run("both", debug=True)
    assert result["t1"]["step_id"] == "T1"
    assert result["t2"]["step_id"] == "T2"
    assert result["debug"]["candidate_controls"][0]["text"] == "发布商品"
    assert result["debug"]["click_diagnostics"]["attempts"][0]["strategy"] == "preferred_class_then_alias"


def test_handle_run_desktop_check(monkeypatch):
    fake_settings = MagicMock()
    fake_settings.screenshot_dir = "logs/screenshots"
    fake_service = MagicMock()
    fake_service.run.return_value = {"t1": {"success": True}}

    monkeypatch.setattr(cli, "load_settings", lambda root: fake_settings)
    monkeypatch.setattr(cli, "DesktopVerificationService", lambda screenshot_dir, tuning=None: fake_service)

    result = cli.handle_run_desktop_check(
        "t1",
        ".",
        True,
        ["京麦"],
        ["Button"],
        {"发布商品": ["发布"]},
    )
    assert result == 0
    fake_service.run.assert_called_once_with(
        step="t1",
        debug=True,
        title=None,
        model=None,
        required_attribute=None,
        brand=None,
        sku_cell_id=None,
        sku_value=None,
        sku_submit=False,
    )


def test_desktop_verification_service_returns_debug_on_t1_failure():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_adapter.build_window_debug_snapshot.return_value = {"matched_windows": [{"title": "京东-京麦 (17)"}]}
    fake_workflow.window_manager.adapter = fake_adapter
    fake_workflow.run_t1_attach_window.side_effect = ValueError("未找到京麦桌面窗口")

    service = DesktopVerificationService.__new__(DesktopVerificationService)
    service.workflow_service = fake_workflow
    result = service.run("both", debug=True)

    assert result["t1"]["success"] is False
    assert result["debug"]["window_snapshot"]["matched_windows"][0]["title"] == "京东-京麦 (17)"


def test_desktop_verification_service_t4_requires_fields():
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
    fake_workflow.run_t3_confirm_category.return_value = WorkflowStepResult(
        step_id="T3",
        success=True,
        page_state="category_confirmed",
        window_handle="2002",
        screenshot_path="c.png",
        message="ok",
    )

    service = DesktopVerificationService.__new__(DesktopVerificationService)
    service.workflow_service = fake_workflow

    try:
        service.run("t4", debug=False, title="标题")
        assert False, "应当抛出 ValueError"
    except ValueError as exc:
        assert "required_attribute" in str(exc)


def test_desktop_verification_service_t5_probe():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_adapter.build_sku_probe.return_value = {"dynamic_controls": [{"automation_id": "jd-id-1-311"}]}
    fake_workflow.window_manager.adapter = fake_adapter
    fake_workflow.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1",
        success=True,
        page_state="jingmai_home",
        window_handle="2002",
        screenshot_path="a.png",
        message="ok",
    )

    service = DesktopVerificationService.__new__(DesktopVerificationService)
    service.workflow_service = fake_workflow
    result = service.run("t5-probe", debug=False)
    assert result["t5_probe"]["dynamic_controls"][0]["automation_id"] == "jd-id-1-311"


def test_desktop_verification_service_t5_input_probe():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_adapter.activate_cell_by_automation_id.return_value = {"success": True, "method": "control.click_input"}
    fake_adapter.type_into_focused_control.return_value = {"success": True, "after_contains": True}
    fake_workflow.window_manager.adapter = fake_adapter
    fake_workflow.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1",
        success=True,
        page_state="jingmai_home",
        window_handle="2002",
        screenshot_path="a.png",
        message="ok",
    )

    service = DesktopVerificationService.__new__(DesktopVerificationService)
    service.workflow_service = fake_workflow
    result = service.run(
        "t5-input-probe",
        debug=False,
        sku_cell_id="jd-id-1-311",
        sku_value="12.50",
        sku_submit=True,
    )
    assert result["t5_input_probe"]["activation"]["success"] is True
    assert result["t5_input_probe"]["typing"]["after_contains"] is True
