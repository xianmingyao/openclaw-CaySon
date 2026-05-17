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
    assert result["runtime"]["providers"]["memory"] is not None


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
        debug=True,
        window_keywords=["京麦"],
        preferred_classes=["Button"],
        click_aliases={"发布商品": ["发布"]},
    )
    assert result == 0
    fake_service.run.assert_called_once_with(step="t1", debug=True)


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
        assert "requires" in str(exc)


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


def test_desktop_verification_service_t4_option_probe():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_adapter.probe_select_options_by_label.side_effect = [
        {"success": True, "label": "品牌", "options": [{"text": "公牛"}]},
        {"success": True, "label": "额定电压", "options": [{"text": "250V"}]},
        {"success": True, "label": "电缆长度", "options": [{"text": "1.8m"}]},
    ]
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
        screenshot_path="b.png",
        message="ok",
    )

    service = DesktopVerificationService.__new__(DesktopVerificationService)
    service.workflow_service = fake_workflow
    result = service.run("t4-option-probe", debug=False)
    assert result["t4_option_probe"]["brand"]["options"][0]["text"] == "公牛"
    assert result["t4_option_probe"]["rated_voltage"]["options"][0]["text"] == "250V"


def test_desktop_verification_service_t5_input_probe():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_adapter.inspect_controls_by_automation_id.side_effect = [
        [{"automation_id": "jd-id-1-311", "text": "请输入"}],
        [{"automation_id": "jd-id-1-311", "text": "12.50"}],
    ]
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
    assert result["t5_input_probe"]["before_snapshot"][0]["text"] == "请输入"
    assert result["t5_input_probe"]["after_snapshot"][0]["text"] == "12.50"


def test_desktop_verification_service_t5_input_probe_resolves_dynamic_id():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_adapter.build_sku_probe.return_value = {
        "dynamic_controls": [
            {
                "automation_id": "jd-id-9983-328",
                "class_name": "Edit",
                "texts": ["电流"],
                "rects": [(713, 713, 918, 746)],
                "seen_count": 3,
            }
        ]
    }
    fake_adapter.inspect_controls_by_automation_id.side_effect = [
        [{"automation_id": "jd-id-9983-328", "text": "电流"}],
        [{"automation_id": "jd-id-9983-328", "text": "10A"}],
    ]
    fake_adapter.activate_cell_by_automation_id.return_value = {"success": True}
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
    result = service.run("t5-input-probe", debug=False, sku_cell_id="jd-id-8403-328", sku_value="10A")

    assert result["t5_input_probe"]["success"] is True
    assert result["t5_input_probe"]["resolved_automation_id"] == "jd-id-9983-328"
    fake_adapter.activate_cell_by_automation_id.assert_called_with("2002", "jd-id-9983-328")


def test_desktop_verification_service_t5_required_fields():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_adapter.build_sku_probe.return_value = {"dynamic_controls": []}
    fake_adapter.inspect_controls_by_automation_id.side_effect = [
        [{"automation_id": "jd-id-8403-328", "text": "电流"}],
        [{"automation_id": "jd-id-8403-328", "text": "10A"}],
        [{"automation_id": "jd-id-8403-319", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-319", "text": "0.5"}],
    ]
    fake_adapter.activate_cell_by_automation_id.return_value = {"success": True}
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
    fake_workflow.run_t5_fill_required_fields.return_value = WorkflowStepResult(
        step_id="T5-REQUIRED-FIELDS",
        success=True,
        page_state="required_fields_completed",
        window_handle="2002",
        screenshot_path="b.png",
        message="ok",
    )

    service = DesktopVerificationService.__new__(DesktopVerificationService)
    service.workflow_service = fake_workflow
    result = service.run("t5-required-fields", debug=False, current="10A", weight="0.5")

    assert result["t5_required_fields"]["success"] is True
    fake_workflow.run_t5_fill_required_fields.assert_called_once_with(
        "2002",
        market_price=None,
        purchase_price=None,
        jd_price=None,
        current="10A",
        weight="0.5",
        length_mm=None,
        width_mm=None,
        height_mm=None,
        factory_inventory=None,
    )


def test_desktop_verification_service_t5_row_probe():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_adapter.inspect_controls_by_automation_id.side_effect = [
        [{"automation_id": "jd-id-8403-311", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-311", "text": "商品A"}],
        [{"automation_id": "jd-id-8403-313", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-313", "text": "19.90"}],
    ]
    fake_adapter.activate_cell_by_automation_id.return_value = {"success": True}
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
        "t5-row-probe",
        debug=False,
        sku_name="商品A",
        market_price="19.90",
    )
    assert result["t5_row_probe"]["mapping"]["sku_name"] == "jd-id-8403-311"
    assert result["t5_row_probe"]["fields"]["market_price"]["after_snapshot"][0]["text"] == "19.90"


def test_desktop_verification_service_t5_market_probe():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_adapter.inspect_controls_by_automation_id.side_effect = [
        [{"automation_id": "jd-id-8403-312", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-312", "text": "19.90"}],
        [{"automation_id": "jd-id-8403-313", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-313", "text": "请输入"}],
    ]
    fake_adapter.activate_cell_by_automation_id.return_value = {"success": True}
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
        "t5-market-probe",
        debug=False,
        market_price="19.90",
    )
    assert result["t5_market_probe"]["candidates"] == ["jd-id-8403-312", "jd-id-8403-313"]
    assert result["t5_market_probe"]["results"]["jd-id-8403-312"]["after_snapshot"][0]["text"] == "19.90"


def test_desktop_verification_service_t5_first_row():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_adapter.inspect_controls_by_automation_id.side_effect = [
        [{"automation_id": "jd-id-8403-311", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-311", "text": "SKU-AUTO-01"}],
        [{"automation_id": "jd-id-8403-312", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-312", "text": "SKU-AUTO-01"}],
        [{"automation_id": "jd-id-8403-313", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-313", "text": "19.90"}],
        [{"automation_id": "jd-id-8403-314", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-314", "text": "17.00"}],
        [{"automation_id": "jd-id-8403-315", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-315", "text": "18.80"}],
    ]
    fake_adapter.activate_cell_by_automation_id.return_value = {"success": True}
    fake_adapter.type_into_focused_control.return_value = {"success": True, "after_contains": True}
    fake_adapter.read_document_text.return_value = "SKU-AUTO-01 19.90 17.00 18.80"
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
        "t5-first-row",
        debug=False,
        sku_name="SKU-AUTO-01",
        short_title="SKU-AUTO-01",
        market_price="19.90",
        purchase_price="17.00",
        jd_price="18.80",
    )
    assert result["t5_first_row"]["mapping"]["short_title"] == "jd-id-8403-312"
    assert result["t5_first_row"]["validation"]["jd_price"] is True
    assert result["t5_first_row"]["success"] is True


def test_desktop_verification_service_t5_dimension_probe():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_adapter.inspect_controls_by_automation_id.side_effect = [
        [{"automation_id": "jd-id-8403-319", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-319", "text": "1.25"}],
        [{"automation_id": "jd-id-8403-320", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-320", "text": "100"}],
        [{"automation_id": "jd-id-8403-321", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-321", "text": "50"}],
        [{"automation_id": "jd-id-8403-322", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-322", "text": "30"}],
    ]
    fake_adapter.activate_cell_by_automation_id.return_value = {"success": True}
    fake_adapter.type_into_focused_control.return_value = {"success": True, "after_contains": True}
    fake_adapter.read_document_text.return_value = "1.25 100 50 30"
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
        "t5-dimension-probe",
        debug=False,
        weight="1.25",
        length_mm="100",
        width_mm="50",
        height_mm="30",
    )
    assert result["t5_dimension_probe"]["mapping"]["weight"] == "jd-id-8403-319"
    assert result["t5_dimension_probe"]["validation"]["height_mm"] is True
    assert result["t5_dimension_probe"]["success"] is True


def test_desktop_verification_service_t5_weight_probe():
    fake_workflow = MagicMock()
    fake_adapter = MagicMock()
    fake_adapter.inspect_controls_by_automation_id.side_effect = [
        [{"automation_id": "jd-id-8403-319", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-319", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-319", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-319", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-319", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-319", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-319", "text": "请输入"}],
        [{"automation_id": "jd-id-8403-319", "text": "请输入"}],
    ]
    fake_adapter.activate_cell_by_automation_id.return_value = {"success": True}
    fake_adapter.type_into_focused_control.return_value = {"success": True, "after_contains": True}
    fake_adapter.read_document_text.side_effect = [
        "1.25",
        "125",
        "1,25",
        "1．25",
    ]
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
        "t5-weight-probe",
        debug=False,
        weight="1.25",
    )
    assert result["t5_weight_probe"]["automation_id"] == "jd-id-8403-319"
    assert result["t5_weight_probe"]["variants"] == ["1.25", "125", "1,25", "1．25"]
    assert result["t5_weight_probe"]["results"]["125"]["document_contains"] is True
