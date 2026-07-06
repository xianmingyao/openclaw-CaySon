import json

import pytest

from jm_ufo_agent.backends.ufo_adapter import Win32WindowInspectorBackend
from jm_ufo_agent.cli.command import main
from jm_ufo_agent.cli.interactive import render_live_dashboard
from jm_ufo_agent.core.settings import ReviewScorerSettings
from jm_ufo_agent.io.importer import ExcelProductImportService
from jm_ufo_agent.runtime.evidence import draft_verification_from_save_evidence, normalize_halt_evidence
from jm_ufo_agent.runtime.production import assess_production_readiness
from jm_ufo_agent.runtime.review import build_minimax_review_strategy
from jm_ufo_agent.workflow.state import GraphState


class FakeProductRepository:
    def __init__(self):
        self.records = []

    async def upsert(self, record):
        self.records.append(record)


class FakeWin32Api:
    def __init__(self):
        self.focused = []

    def enum_windows(self):
        return [1, 2]

    def enum_child_windows(self, handle):
        return [11, 12, 13] if handle == 1 else []

    def get_title(self, handle):
        return {1: "京麦 - 新增商品", 2: "Other", 11: "", 12: "", 13: ""}.get(handle, "")

    def get_class_name(self, handle):
        return {
            1: "Qt51511QWindowIcon",
            2: "Notepad",
            11: "Qt51511QWindowIcon",
            12: "Chrome_WidgetWin_0",
            13: "Chrome_RenderWidgetHostHWND",
        }.get(handle, "")

    def focus_window(self, handle):
        self.focused.append(handle)
        return True


class FlakyReviewTransport:
    def __init__(self):
        self.get_calls = 0
        self.post_calls = 0

    async def get_json(self, url, headers):
        self.get_calls += 1
        if self.get_calls == 1:
            raise TimeoutError("temporary")
        return {"data": [{"id": "MiniMax-M3", "type": "model"}]}

    async def post_json(self, url, headers, payload):
        self.post_calls += 1
        return {"content": [{"type": "text", "text": '{"overall_score": 96, "max_score": 100, "blocking_gaps": [], "recommendations": ["ok"]}'}]}


async def test_excel_import_service_parses_and_writes_real_xlsx(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    path = tmp_path / "products.xlsx"
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["商品ID", "商品标题"])
    sheet.append(["sku-1", "商品1"])
    sheet.append([None, "缺少ID"])
    workbook.save(path)
    repo = FakeProductRepository()

    summary = await ExcelProductImportService().import_file(path, repository=repo)

    assert summary.parsed_count == 2
    assert summary.written_count == 2
    assert summary.generated_id_rows == [3]
    assert [record.product_id for record in repo.records] == ["sku-1", "row_3"]


async def test_win32_window_backend_extracts_jingmai_facts_with_fake_api():
    api = FakeWin32Api()
    backend = Win32WindowInspectorBackend(api=api)

    facts = await backend.inspect_jingmai()
    focused = await backend.focus_window("京麦")

    assert facts.found is True
    assert facts.main_class_name == "Qt51511QWindowIcon"
    assert facts.qt_child_count == 1
    assert facts.webview_pane_count == 2
    assert focused is True
    assert api.focused == [1]


def test_halt_and_draft_evidence_are_normalized():
    state = GraphState(task_id="t1", row_index=82, product={})
    state.current_node = "VERIFY_FIELD"

    state.halt("ocr mismatch", {"screenshot_path": "a.png", "page_signature": "sig", "extra": 1})
    draft = draft_verification_from_save_evidence({"ok": True, "draft_id": "d1", "toast_text": "保存成功"})
    normalized = normalize_halt_evidence("SAVE_DRAFT", "failed", {"window_summary": {"found": True}})

    assert state.evidence["halt_evidence"][0]["screenshot_path"] == "a.png"
    assert state.evidence["halt_evidence"][0]["details"]["extra"] == 1
    assert state.evidence["halt_evidence"][0]["details"]["page_signature"] == "sig"
    assert draft.ok is True
    assert draft.draft_id == "d1"
    assert normalized["window_summary"] == {"found": True}


def test_live_dashboard_and_cli_jsonl_replay(capsys, tmp_path):
    states = [
        {"task_id": "t1", "row_index": 82, "current_node": "BOOTSTRAP", "status": "running"},
        {"task_id": "t1", "row_index": 82, "current_node": "SAVE_DRAFT", "status": "saved_draft"},
    ]
    jsonl = tmp_path / "states.jsonl"
    jsonl.write_text("\n".join(json.dumps(item, ensure_ascii=False) for item in states), encoding="utf-8")

    rendered = render_live_dashboard(states)
    code = main(["live-dashboard", "--states-jsonl", str(jsonl)])
    output = capsys.readouterr().out

    assert "frame: 1" in rendered
    assert "SAVE_DRAFT" in output
    assert code == 0


async def test_minimax_runtime_strategy_retries_preflight_and_scores():
    transport = FlakyReviewTransport()
    settings = ReviewScorerSettings(api_key="token", max_call_attempts=2, backoff_base_sec=0, backoff_max_sec=0)
    strategy = build_minimax_review_strategy(settings, transport=transport)

    result = await strategy.decide_async(1.0, blockers=[], loop_step=0, state_payload={"task_id": "t1"})

    assert result.decision == "save_draft"
    assert result.overall_score == 96
    assert transport.get_calls == 2
    assert transport.post_calls == 1


def test_production_readiness_blocks_missing_e2e_capabilities():
    report = assess_production_readiness({"parse_excel": True, "crawl_jd": True})
    ready_report = assess_production_readiness({key: True for key in ["parse_excel", "crawl_jd", "download_images", "transform_images", "check_jingmai_login", "open_add_product_page", "fill_webview_form", "save_draft", "verify_draft_readback"]})

    assert report.ready is False
    assert "save_draft" in report.missing
    assert ready_report.ready is True
