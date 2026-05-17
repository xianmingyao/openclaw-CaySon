from __future__ import annotations

from pathlib import Path

import pytest

from jingmai_publish.services.draft_e2e import DraftE2EOptions, DraftE2EOrchestrator


class FakeImportPipeline:
    def __init__(self, prepared_product: dict[str, object]) -> None:
        self.prepared_product = prepared_product
        self.calls: list[dict[str, object]] = []

    def run_from_local_excel_path(self, excel_path, *, mode, store_id):
        self.calls.append({"excel_path": excel_path, "mode": mode, "store_id": store_id})
        return {
            "job_id": "job-1",
            "session_id": "session-1",
            "task_ids": ["task-1"],
            "prepared_products": [self.prepared_product],
        }


class FakeDesktopService:
    def __init__(self, fail_step: str | None = None) -> None:
        self.fail_step = fail_step
        self.calls: list[dict[str, object]] = []

    def run(self, *, step, debug=False, **kwargs):
        self.calls.append({"step": step, "debug": debug, "kwargs": kwargs})
        return {step.replace("-", "_"): {"success": step != self.fail_step}}


def _prepared_product(**overrides) -> dict[str, object]:
    product = {
        "product_name": "公牛插座 GN-605",
        "model": "GN-605",
        "brand": "公牛",
        "market_price": "82.35",
        "purchase_price": "66.50",
        "jd_sale_price": "70.00",
        "unit_name": "件",
        "product_summary": "测试摘要",
        "detail_html": "<p>测试详情</p>",
        "weight_kg": "0.85",
        "length_mm": "250.00",
        "width_mm": "76.00",
        "height_mm": "42.00",
        "images": [],
    }
    product.update(overrides)
    return product


def _image_file(tmp_path: Path, name: str) -> str:
    path = tmp_path / name
    path.write_bytes(b"fake image")
    return str(path)


def _orchestrator(prepared: dict[str, object], desktop: FakeDesktopService) -> DraftE2EOrchestrator:
    orchestrator = DraftE2EOrchestrator.__new__(DraftE2EOrchestrator)
    orchestrator.import_pipeline = FakeImportPipeline(prepared)
    orchestrator.desktop_service = desktop
    return orchestrator


def test_draft_e2e_runs_import_and_saves_draft(tmp_path):
    desktop = FakeDesktopService()
    orchestrator = _orchestrator(_prepared_product(), desktop)

    result = orchestrator.run(
        DraftE2EOptions(
            excel_path="demo.xlsx",
            store_id="store-a",
            required_attr="五孔",
            current="10A",
            factory_inventory="10",
            main_image_path=_image_file(tmp_path, "main.png"),
            transparent_image_path=_image_file(tmp_path, "transparent.png"),
            rated_voltage="220V",
            cable_length="1.8m",
            debug=True,
        )
    )

    assert result["success"] is True
    assert result["mode"] == "draft"
    assert [call["step"] for call in desktop.calls] == [
        "t4",
        "t5-required-fields",
        "t6-main-image",
        "t6-transparent-image",
        "t6-detail-editor",
        "t7",
        "t8-save-draft",
    ]
    assert all(call["step"] != "t8-publish-product" for call in desktop.calls)
    assert desktop.calls[0]["debug"] is True
    assert desktop.calls[0]["kwargs"]["required_attribute"] == "五孔"


def test_draft_e2e_stops_on_first_failed_desktop_step(tmp_path):
    desktop = FakeDesktopService(fail_step="t6-main-image")
    orchestrator = _orchestrator(_prepared_product(), desktop)

    result = orchestrator.run(
        DraftE2EOptions(
            excel_path="demo.xlsx",
            main_image_path=_image_file(tmp_path, "main.png"),
            transparent_image_path=_image_file(tmp_path, "transparent.png"),
        )
    )

    assert result["success"] is False
    assert [call["step"] for call in desktop.calls][-1] == "t6-main-image"
    assert "t8-save-draft" not in [call["step"] for call in desktop.calls]


def test_draft_e2e_keeps_saving_when_transparent_image_fails(tmp_path):
    desktop = FakeDesktopService(fail_step="t6-transparent-image")
    orchestrator = _orchestrator(_prepared_product(), desktop)

    result = orchestrator.run(
        DraftE2EOptions(
            excel_path="demo.xlsx",
            main_image_path=_image_file(tmp_path, "main.png"),
            transparent_image_path=_image_file(tmp_path, "transparent.png"),
        )
    )

    assert result["success"] is True
    assert [call["step"] for call in desktop.calls][-1] == "t8-save-draft"


def test_draft_e2e_keeps_saving_when_t5_required_fields_fail(tmp_path):
    desktop = FakeDesktopService(fail_step="t5-required-fields")
    orchestrator = _orchestrator(_prepared_product(), desktop)

    result = orchestrator.run(
        DraftE2EOptions(
            excel_path="demo.xlsx",
            current="10A",
            main_image_path=_image_file(tmp_path, "main.png"),
            transparent_image_path=_image_file(tmp_path, "transparent.png"),
        )
    )

    assert result["success"] is True
    assert [call["step"] for call in desktop.calls][-1] == "t8-save-draft"


def test_draft_e2e_keeps_saving_when_t4_partial_fill_fails(tmp_path):
    desktop = FakeDesktopService(fail_step="t4")
    orchestrator = _orchestrator(_prepared_product(), desktop)

    result = orchestrator.run(
        DraftE2EOptions(
            excel_path="demo.xlsx",
            main_image_path=_image_file(tmp_path, "main.png"),
            transparent_image_path=_image_file(tmp_path, "transparent.png"),
        )
    )

    assert result["success"] is True
    assert desktop.calls[0]["step"] == "t4"
    assert [call["step"] for call in desktop.calls][-1] == "t8-save-draft"


def test_draft_e2e_omits_incomplete_dimensions_from_required_fields(tmp_path):
    desktop = FakeDesktopService()
    prepared = _prepared_product(length_mm=None, width_mm=None, height_mm=None)
    orchestrator = _orchestrator(prepared, desktop)

    result = orchestrator.run(
        DraftE2EOptions(
            excel_path="demo.xlsx",
            current="10A",
            main_image_path=_image_file(tmp_path, "main.png"),
            transparent_image_path=_image_file(tmp_path, "transparent.png"),
        )
    )

    steps = [call["step"] for call in desktop.calls]
    t5_call = next(call for call in desktop.calls if call["step"] == "t5-required-fields")
    assert result["success"] is True
    assert "t5-required-fields" in steps
    assert "length_mm" not in t5_call["kwargs"]
    assert "width_mm" not in t5_call["kwargs"]
    assert "height_mm" not in t5_call["kwargs"]


def test_draft_e2e_requires_local_image_path():
    desktop = FakeDesktopService()
    orchestrator = _orchestrator(_prepared_product(), desktop)

    with pytest.raises(ValueError, match="main"):
        orchestrator.run(DraftE2EOptions(excel_path="demo.xlsx"))
