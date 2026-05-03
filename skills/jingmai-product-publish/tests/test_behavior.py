import json
import sys
from pathlib import Path
from types import SimpleNamespace

from click.testing import CliRunner
from openpyxl import Workbook

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.executor import ExecutorAgent
from agents.planner import PlannerAgent
from agents.thinker import ThinkerAgent
from cli import _build_product_model, _extract_plan_payload, _load_batch_items, _read_json_file, cli
from db import DatabaseManager
from llm.manager import LLMManager
from memory.long_term import LongTermMemory
from models import Product, PublishTask, TaskStep
from actions.form import fill_text
from actions import ActionRegistry
from actions.navigation import publish_product, save_draft, select_category
from actions.window import navigate_to
from infrastructure.locator import JingmaiLocator
from llm.ollama import OllamaProvider


class _LLMReturning:
    def __init__(self, text: str):
        self.text = text
        self.called = False

    def invoke(self, prompt: str, **kwargs) -> str:
        self.called = True
        return self.text

    def invoke_multimodal(self, prompt: str, image_path: str, **kwargs) -> str:
        self.called = True
        return self.text

    def embed_text(self, text: str) -> list:
        self.called = True
        return [0.1, 0.2, 0.3]


def test_executor_think_is_rule_driven():
    agent = ExecutorAgent()
    fake_llm = _LLMReturning("should not be used")
    agent.set_llm(fake_llm)

    result = agent.think({"action": "find_window"})

    assert result["next_action"] == "find_window"
    assert result["reason"] == "rule-driven executor"
    assert fake_llm.called is False


def test_thinker_rejects_empty_response():
    agent = ThinkerAgent()
    agent.set_llm(_LLMReturning(""))

    result = agent.run(question="当前页面怎么办")

    assert result["success"] is False
    assert "为空" in result["error"]


def test_planner_accepts_task_description():
    agent = PlannerAgent()

    result = agent.run(task_desc="发布一个手机商品，价格 99 元，类目 手机，SKU SKU001")

    assert result["success"] is True
    assert result["product_data"]["price"] == 99.0
    assert result["product_data"]["category"] == "手机"
    assert result["product_data"]["sku"] == "SKU001"
    assert any(step["action"] == "select_category" for step in result["plan"])


def test_planner_normalizes_llm_step_params():
    agent = PlannerAgent()
    product = {
        "title": "测试商品",
        "price": 99.0,
        "category": "手机",
        "sku": "SKU001",
    }
    raw_steps = [
        {"action": "find_window", "params": {"window_id": "x"}},
        {"action": "activate_window", "params": {"window_name": "x"}},
        {"action": "select_category", "params": {"category": "electronics"}},
        {"action": "navigate_to", "params": {"page": "product_creation"}},
        {"action": "fill_text", "params": {"field": "title"}},
        {"action": "fill_text", "params": {"field": "sku", "text": "SKU001"}},
        {"action": "fill_product_info", "params": {"sku": "bad"}},
        {"action": "verify_result", "params": {"expected": {"ok": True}}},
    ]

    normalized = agent._normalize_llm_steps(raw_steps, product)
    action_names = [step["action"] for step in normalized]

    assert normalized[0]["params"] == {}
    assert action_names.index("navigate_to") < action_names.index("select_category")
    assert next(step for step in normalized if step["action"] == "select_category")["params"]["search_text"] == "electronics"
    assert next(step for step in normalized if step["action"] == "navigate_to")["params"]["page"] == "publish"
    assert normalized[4]["params"]["text"] == "测试商品"
    assert normalized[5]["params"]["product"]["sku"] == "SKU001"
    assert normalized[6]["params"] == {"check_errors": True}


def test_load_batch_items_supports_xlsx(tmp_path: Path):
    path = tmp_path / "products.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["商品标题", "价格", "类目", "SKU"])
    sheet.append(["测试商品A", 88.5, "手机", "SKU-A"])
    sheet.append(["测试商品B", 66, "家电", "SKU-B"])
    workbook.save(path)

    items = _load_batch_items(path)

    assert len(items) == 2
    assert items[0]["title"] == "测试商品A"
    assert items[0]["price"] == 88.5
    assert items[1]["sku"] == "SKU-B"


def test_read_json_file_supports_utf8_bom(tmp_path: Path):
    path = tmp_path / "product.json"
    path.write_text('{"product":{"title":"测试商品","price":99}}', encoding="utf-8-sig")

    payload = _read_json_file(path)

    assert payload["product"]["title"] == "测试商品"


def test_build_product_model_maps_new_fields():
    payload = {
        "product": {
            "sku": "SKU001",
            "title": "测试商品",
            "category": "手机",
            "category_path": "数码>手机",
            "price": 199.9,
            "url": "https://item.jd.com/123.html",
            "attributes": {"颜色": "黑色"},
        },
        "images": ["a.jpg", "b.jpg"],
    }

    product = _build_product_model(payload, source="scrape")

    assert product.product_id == "SKU001"
    assert product.source_url == "https://item.jd.com/123.html"
    assert product.category_path == "数码>手机"
    assert product.images == ["a.jpg", "b.jpg"]
    assert product.attributes == {"颜色": "黑色"}


def test_db_tracks_task_and_step_results():
    db = DatabaseManager(sqlite_url="sqlite:///:memory:")
    db.create_tables()

    saved = db.save_product(Product(product_id="SKU001", title="测试商品"))
    assert saved.product_id == "SKU001"

    db.create_task(PublishTask(task_id="task-1", product_id="SKU001", status="planning"))
    db.save_step(TaskStep(task_id="task-1", step_index=0, action_name="find_window", params={}))

    db.update_task_status("task-1", "running")
    db.update_step_status("task-1", 0, "running")
    db.update_step_status("task-1", 0, "success", result={"success": True})
    db.update_task_status("task-1", "success", result={"ok": True})

    task = db.get_task("task-1")
    steps = db.list_steps("task-1")

    assert task["status"] == "success"
    assert task["started_at"] is not None
    assert task["finished_at"] is not None
    assert task["result"] == {"ok": True}
    assert steps[0]["status"] == "success"
    assert steps[0]["result"] == {"success": True}


def test_scrape_command_saves_product(monkeypatch, tmp_path: Path):
    runner = CliRunner()
    output = tmp_path / "product.json"

    def fake_scrape(self, url):
        return {
            "success": True,
            "product_id": "12345",
            "title": "抓取商品",
            "price": "88.8",
            "category": "手机",
            "url": url,
        }

    monkeypatch.setattr("scraper.JDScraper.scrape", fake_scrape)

    result = runner.invoke(cli, ["scrape", "--url", "https://item.jd.com/12345.html", "--output", str(output)])

    assert result.exit_code == 0
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["product_id"] == "12345"


def test_scrape_command_accepts_positional_url(monkeypatch, tmp_path: Path):
    runner = CliRunner()
    output = tmp_path / "product.json"

    def fake_scrape(self, url):
        return {
            "success": True,
            "product_id": "67890",
            "title": "位置参数商品",
            "price": "18.8",
            "category": "配件",
            "url": url,
        }

    monkeypatch.setattr("scraper.JDScraper.scrape", fake_scrape)

    result = runner.invoke(cli, ["scrape", "https://item.jd.com/67890.html", "--output", str(output), "--no-save"])

    assert result.exit_code == 0
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["product_id"] == "67890"


def test_llm_manager_falls_back_on_empty_primary():
    class FakeProvider:
        def __init__(self, name, text):
            self.name = name
            self.text = text

        def invoke(self, prompt: str, **kwargs):
            return self.text

        def invoke_multimodal(self, prompt: str, image_path: str, **kwargs):
            return self.text

        def embed_text(self, text: str):
            return [] if not self.text else [0.1]

        def health_check(self):
            return True

    manager = LLMManager()
    primary = FakeProvider("primary", "")
    fallback = FakeProvider("fallback", '{"ok": true}')
    manager.router.providers = [primary, fallback]

    assert manager.invoke("test") == '{"ok": true}'


def test_long_term_memory_degrades_without_embedder():
    memory = LongTermMemory(collection_name="jingmai_publish_memory_test")
    vector = memory._get_embedding("test")

    assert isinstance(vector, list)
    assert len(vector) == memory.dim


def test_extract_plan_payload_supports_full_plan_and_steps_only():
    full_payload = _extract_plan_payload({
        "task_id": "task-1",
        "plan": [{"action": "find_window", "params": {}}],
        "total_steps": 1,
    })
    legacy_payload = _extract_plan_payload([{"action": "find_window", "params": {}}])

    assert full_payload["task_id"] == "task-1"
    assert full_payload["steps"][0]["action"] == "find_window"
    assert legacy_payload["task_id"] == ""
    assert legacy_payload["total_steps"] == 1


def test_locator_filters_invalid_minimized_window():
    assert JingmaiLocator._is_usable_rect((-32000, -32000, -31840, -31972)) is False
    assert JingmaiLocator._is_usable_rect((100, 100, 1400, 900)) is True


def test_locator_refreshes_live_window_rect_before_scaling(monkeypatch):
    import infrastructure.locator as locator_module

    monkeypatch.setattr(locator_module, "WIN32_AVAILABLE", True)

    class FakeWin32Gui:
        @staticmethod
        def GetWindowRect(hwnd):
            return (0, 0, 2560, 1392)

    monkeypatch.setattr(locator_module, "win32gui", FakeWin32Gui)

    locator = JingmaiLocator()
    locator.hwnd = 123
    locator.window_rect = (100, 100, 1380, 900)

    x, y = locator.adapt_coords(1277, 1307)

    assert (x, y) == (1277, 1307)
    assert locator.window_rect == (0, 0, 2560, 1392)


def test_locator_click_fallback_uses_precomputed_screen_coords(monkeypatch):
    import infrastructure.locator as locator_module

    monkeypatch.setattr(locator_module, "WIN32_AVAILABLE", True)

    class FakeWin32Gui:
        @staticmethod
        def SetForegroundWindow(_hwnd):
            raise RuntimeError("boom")

    clicks = []

    class FakePyAutoGUI:
        @staticmethod
        def click(x, y):
            clicks.append((x, y))

    monkeypatch.setattr(locator_module, "win32gui", FakeWin32Gui)
    monkeypatch.setitem(sys.modules, "pyautogui", FakePyAutoGUI)
    monkeypatch.setattr(locator_module.time, "sleep", lambda *_args, **_kwargs: None)

    locator = JingmaiLocator()
    locator.hwnd = 123
    locator.window_rect = (10, 20, 2570, 1412)

    assert locator.click(100, 200) is True
    assert clicks == [(110, 220)]


def test_activate_window_does_not_shrink_large_window(monkeypatch):
    import infrastructure.locator as locator_module

    monkeypatch.setattr(locator_module, "WIN32_AVAILABLE", True)

    calls = {"set_window_pos": 0}

    class FakeWin32Gui:
        @staticmethod
        def ShowWindow(hwnd, flag):
            return None

        @staticmethod
        def GetWindowRect(hwnd):
            return (0, 0, 2560, 1392)

        @staticmethod
        def SetWindowPos(hwnd, insert_after, x, y, width, height, flags):
            calls["set_window_pos"] += 1

        @staticmethod
        def SetForegroundWindow(hwnd):
            return None

    monkeypatch.setattr(locator_module, "win32gui", FakeWin32Gui)
    monkeypatch.setattr(locator_module.time, "sleep", lambda *_args, **_kwargs: None)

    locator = JingmaiLocator()
    locator.hwnd = 123

    assert locator.activate_window() is True
    assert calls["set_window_pos"] == 0
    assert locator.window_rect == (0, 0, 2560, 1392)


def test_fill_text_fails_when_focus_click_fails():
    class FailingLocator:
        def click(self, *args, **kwargs):
            return False

    result = fill_text("test", x=10, y=10, locator=FailingLocator())

    assert result["success"] is False
    assert "激活输入框失败" in result["message"]


def test_navigate_to_fails_on_click_error():
    class FailingLocator:
        def click(self, *args, **kwargs):
            return False

    result = navigate_to("publish", locator=FailingLocator())

    assert result["success"] is False
    assert "导航失败" in result["message"]


def test_select_category_fails_on_click_error():
    class FailingLocator:
        def click(self, *args, **kwargs):
            return False

        def press_enter(self):
            return True

    result = select_category(search_text="手机", locator=FailingLocator())

    assert result["success"] is False


def test_select_category_fails_when_search_result_not_found(monkeypatch):
    import actions.navigation as navigation_module
    import actions.form as form_module

    class Locator:
        def __init__(self):
            self.clicks = []

        def click(self, x, y, delay=0):
            self.clicks.append((x, y))
            return True

        def press_enter(self):
            return True

    monkeypatch.setattr(form_module, "fill_text", lambda *args, **kwargs: {"success": True})
    monkeypatch.setattr(navigation_module, "_select_search_result", lambda *args, **kwargs: False)
    monkeypatch.setitem(sys.modules, "pyautogui", type("FakePyAutoGUI", (), {"press": staticmethod(lambda *_: None)}))

    locator = Locator()
    result = navigation_module.select_category(search_text="插座", locator=locator)

    assert result["success"] is False
    assert "未找到类目搜索结果" in result["message"]
    assert result["steps"] == ["search"]


def test_save_draft_and_publish_propagate_click_failures(monkeypatch):
    class FailingLocator:
        def click(self, *args, **kwargs):
            return False

    save_result = save_draft(locator=FailingLocator())
    publish_result = publish_product(locator=FailingLocator())

    assert save_result["success"] is False
    assert publish_result["success"] is False


def test_action_registry_execute_allows_action_param_named_name():
    class DummyLocator:
        pass

    result = ActionRegistry.execute("click_element", name="缂栬緫", locator=DummyLocator())

    assert isinstance(result, dict)
    assert result["success"] is False


def test_fill_product_info_fails_when_any_field_write_fails(monkeypatch):
    import actions.form as form_module

    def fake_fill_text(text, x=None, y=None, locator=None, log=None, clear=True, name="", index=0):
        return {"success": text != "bad-price"}

    monkeypatch.setattr(form_module, "fill_text", fake_fill_text)
    monkeypatch.setattr(
        form_module,
        "_verify_text_field",
        lambda locator, field, x, y, expected, prefer_uia=True: {
            "success": True,
            "actual": str(expected),
            "expected": str(expected),
            "method": "test",
            "compare_mode": "text",
        },
    )
    monkeypatch.setattr(form_module, "_select_dropdown_option", lambda *args, **kwargs: {"success": True})
    monkeypatch.setattr(
        "config.jingmai_coords.PRODUCT_INFO_PAGE",
        {
            "title_input": (1, 1),
            "model_input": (2, 2),
            "sku_input": (3, 3),
            "market_price": (4, 4),
            "jd_price": (5, 5),
            "purchase_price": (6, 6),
            "brand_select": (7, 7),
        },
    )

    result = form_module.fill_product_info(
        {
            "title": "ok",
            "purchase_price": "bad-price",
            "brand": "brand-a",
        },
        locator=SimpleNamespace(),
    )

    assert result["success"] is False
    assert result["filled"] == 2
    assert "purchase_price" in result["failed_fields"]


def test_fill_product_info_fails_when_readback_mismatches(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(
        form_module,
        "fill_text",
        lambda text, **kwargs: {"success": True, "text": text},
    )
    monkeypatch.setattr(
        form_module,
        "_verify_text_field",
        lambda locator, field, x, y, expected, prefer_uia=True: {
            "success": False,
            "actual": "wrong",
            "message": "readback mismatch",
            "failures": [{"method": "test", "reason": "value mismatch"}],
        },
    )
    monkeypatch.setattr(
        "config.jingmai_coords.PRODUCT_INFO_PAGE",
        {
            "title_input": (1, 1),
            "model_input": (2, 2),
            "sku_input": (3, 3),
            "market_price": (4, 4),
            "jd_price": (5, 5),
            "purchase_price": (6, 6),
            "brand_select": (7, 7),
        },
    )

    result = form_module.fill_product_info({"title": "ok"}, locator=SimpleNamespace())

    assert result["success"] is False
    assert result["failed_fields"] == ["title"]
    assert result["details"][0]["verify_error"] == "readback mismatch"
    assert result["details"][0]["write_success"] is True
    assert result["details"][0]["verify_success"] is False


def test_verify_text_field_prefers_uia_and_normalizes_price(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(
        form_module,
        "_read_uia_value_for_field",
        lambda locator, field, x, y: {"success": True, "actual": "70.00", "method": "uia-get-value"},
    )
    monkeypatch.setattr(
        form_module,
        "_read_clipboard_value_for_field",
        lambda locator, x, y: {"success": True, "actual": "wrong", "method": "clipboard-readback"},
    )

    result = form_module._verify_text_field(SimpleNamespace(), "jd_price", 1, 2, "70")

    assert result["success"] is True
    assert result["method"] == "uia-get-value"
    assert result["compare_mode"] == "numeric"
    assert result["actual"] == "70"


def test_verify_text_field_returns_structured_failures(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(
        form_module,
        "_read_uia_value_for_field",
        lambda locator, field, x, y: {"success": False, "message": "uia unavailable", "method": "uia-get-value"},
    )
    monkeypatch.setattr(
        form_module,
        "_read_clipboard_value_for_field",
        lambda locator, x, y: {"success": True, "actual": "71", "method": "clipboard-readback"},
    )

    result = form_module._verify_text_field(SimpleNamespace(), "purchase_price", 1, 2, "70")

    assert result["success"] is False
    assert result["failures"][0]["method"] == "uia-get-value"
    assert result["failures"][1]["method"] == "clipboard-readback"
    assert result["failures"][1]["compare_mode"] == "numeric"


def test_verify_text_field_marks_uia_timeout(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(
        form_module,
        "_read_uia_value_for_field",
        lambda locator, field, x, y: {"success": False, "message": "uia read timeout (1.5s)", "method": "uia-timeout"},
    )
    monkeypatch.setattr(
        form_module,
        "_read_clipboard_value_for_field",
        lambda locator, x, y: {"success": False, "message": "clipboard empty", "method": "clipboard-readback"},
    )

    result = form_module._verify_text_field(SimpleNamespace(), "jd_price", 1, 2, "70")

    assert result["success"] is False
    assert result["uia_timeout"] is True


def test_read_uia_value_prefers_local_candidates(monkeypatch):
    import actions.form as form_module

    class FakeRect:
        def __init__(self, left, top, right, bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    class FakeEdit:
        def __init__(self, rect, value):
            self._rect = rect
            self._value = value

        def rectangle(self):
            return self._rect

        def get_value(self):
            return self._value

    monkeypatch.setattr("actions._uia_helpers.find_jingmai_uia_window", lambda locator=None, log=None: object())
    monkeypatch.setattr(
        "infrastructure.uia_inspector.UIAControlInspector.find_descendants",
        lambda window, control_type_list, is_visible, is_enabled, limit: [
            FakeEdit(FakeRect(900, 450, 980, 500), "999"),
            FakeEdit(FakeRect(1450, 470, 1540, 520), "70.00"),
        ],
    )

    locator = SimpleNamespace(
        adapt_coords=lambda x, y: (x, y),
        window_to_screen=lambda x, y: (x, y),
    )

    result = form_module._read_uia_value_for_field(locator, "jd_price", 1590, 493)

    assert result["success"] is True
    assert result["method"] == "uia-local-edit"
    assert result["actual"] == "70.00"


def test_executor_does_not_turn_action_failure_into_success(tmp_path: Path):
    agent = ExecutorAgent()
    agent.set_llm(_LLMReturning('{"status":"ok","reason":"looks good"}'))
    agent._resume_step_index = 0
    agent._check_safety = lambda _action: True
    agent._ensure_locator = lambda: None
    agent._capture_window_summary = lambda: {}
    agent._diff_window_summary = lambda before, after: {}
    agent._log_window_diff_risk = lambda *args, **kwargs: None
    screenshot = tmp_path / "shot.png"
    screenshot.write_bytes(b"fake")
    agent._take_screenshot = lambda _action: str(screenshot)
    agent.act = lambda _action, _params: {"success": False, "error": "boom"}

    result = agent.run_react_loop([{"action": "click_element", "params": {"name": "缂栬緫"}}])

    assert result["success"] is False
    assert result["failed_step"] == 1
    assert result["results"][0]["success"] is False
    assert result["results"][0]["result"]["error"] == "boom"


def test_executor_records_memory_metadata_for_failed_step(tmp_path: Path):
    class FakeMemory:
        def __init__(self):
            self.entries = []

        def remember_short_term(self, content, importance, **meta):
            self.entries.append((content, importance, meta))

    agent = ExecutorAgent()
    fake_memory = FakeMemory()
    agent.set_memory(fake_memory)
    agent._resume_step_index = 0
    agent._check_safety = lambda _action: True
    agent._ensure_locator = lambda: None
    agent._capture_window_summary = lambda: {}
    agent._diff_window_summary = lambda before, after: {}
    agent._log_window_diff_risk = lambda *args, **kwargs: None
    screenshot = tmp_path / "shot.png"
    screenshot.write_bytes(b"fake")
    agent._take_screenshot = lambda _action: str(screenshot)
    agent.act = lambda _action, _params: {"success": False, "error": "boom"}

    result = agent.run_react_loop([{"action": "click_element", "params": {"name": "缂栬緫"}}])

    assert result["success"] is False
    assert len(fake_memory.entries) == 1
    _, _, meta = fake_memory.entries[0]
    assert meta["action_result_success"] is False
    assert meta["vision_status"] == "error"
    assert meta["retry_count"] == 3
    assert meta["error"] == "boom"
    assert meta["screenshot"] == str(screenshot)


def test_finalize_plan_file_resets_later_steps_to_pending_after_failure(tmp_path: Path):
    agent = ExecutorAgent()
    agent._task_id = "task-reset"
    agent._plan_file = str(tmp_path / "plan.json")

    plan = [
        {"action": "step-1", "status": "failed"},
        {"action": "step-2", "status": "success"},
        {"action": "step-3", "status": "success"},
    ]

    agent._finalize_plan_file(plan, success=False, failed_step=1, error="boom")

    payload = json.loads(Path(agent._plan_file).read_text(encoding="utf-8"))
    statuses = [step["status"] for step in payload["plan"]]

    assert payload["status"] == "failed"
    assert statuses == ["failed", "pending", "pending"]


def test_locator_take_screenshot_writes_real_png(monkeypatch, tmp_path: Path):
    import infrastructure.locator as locator_module

    monkeypatch.setattr(locator_module, "WIN32_AVAILABLE", True)

    class FakeBitmap:
        def CreateCompatibleBitmap(self, *_args, **_kwargs):
            return None

        def GetInfo(self):
            return {"bmWidth": 40, "bmHeight": 20}

        def GetBitmapBits(self, _signed):
            return b"\x00\x00\x00\x00" * (40 * 20)

        def GetHandle(self):
            return 1

    class FakeSaveDC:
        def SelectObject(self, *_args, **_kwargs):
            return None

        def BitBlt(self, *_args, **_kwargs):
            return None

        def DeleteDC(self):
            return None

    class FakeMfcDC:
        def CreateCompatibleDC(self):
            return FakeSaveDC()

        def DeleteDC(self):
            return None

    class FakeWin32UI:
        @staticmethod
        def CreateDCFromHandle(_handle):
            return FakeMfcDC()

        @staticmethod
        def CreateBitmap():
            return FakeBitmap()

    class FakeWin32Gui:
        @staticmethod
        def GetWindowRect(_hwnd):
            return (0, 0, 40, 20)

        @staticmethod
        def GetWindowDC(_hwnd):
            return 1

        @staticmethod
        def DeleteObject(_handle):
            return None

        @staticmethod
        def ReleaseDC(_hwnd, _dc):
            return None

    monkeypatch.setitem(sys.modules, "win32ui", FakeWin32UI)
    monkeypatch.setattr(locator_module, "win32gui", FakeWin32Gui)
    monkeypatch.setattr(locator_module, "win32con", SimpleNamespace(SRCCOPY=0))

    locator = JingmaiLocator()
    locator.hwnd = 1
    locator.window_rect = (0, 0, 40, 20)

    path = tmp_path / "vision.png"
    saved = locator.take_screenshot(str(path), for_vision=True)

    assert saved == str(path)
    assert path.exists()
    assert path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_plan_command_outputs_full_payload_by_default(monkeypatch):
    runner = CliRunner()

    class FakePlanner:
        def run(self, **kwargs):
            return {
                "success": True,
                "task_id": "task-123",
                "product_data": {"title": "测试商品"},
                "plan": [{"action": "find_window", "params": {}}],
                "total_steps": 1,
            }

    class FakeFactory:
        def create_planner(self):
            return FakePlanner()

    monkeypatch.setattr("agents.factory.AgentFactory", lambda: FakeFactory())
    result = runner.invoke(cli, ["plan", "发布测试商品"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["task_id"] == "task-123"
    assert payload["plan"][0]["action"] == "find_window"


def test_execute_command_reuses_task_id_from_plan_file(monkeypatch, tmp_path: Path):
    runner = CliRunner()
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps({
        "task_id": "task-xyz",
        "plan": [{"action": "find_window", "params": {}}],
    }, ensure_ascii=False), encoding="utf-8")

    class FakeExecutor:
        def __init__(self):
            self.last_task_id = ""

        def run(self, plan, task_id=""):
            self.last_task_id = task_id
            return {"success": True}

    fake_executor = FakeExecutor()

    class FakeFactory:
        def create_executor(self):
            return fake_executor

    monkeypatch.setattr("agents.factory.AgentFactory", lambda: FakeFactory())
    result = runner.invoke(cli, ["execute", "--config", str(plan_path)])

    assert result.exit_code == 0
    assert fake_executor.last_task_id == "task-xyz"
    assert "task_id=task-xyz" in result.output


def test_batch_plan_out_creates_one_plan_file_per_task(monkeypatch, tmp_path: Path):
    runner = CliRunner()
    batch_path = tmp_path / "products.json"
    plan_dir = tmp_path / "plans"
    batch_path.write_text(
        json.dumps(
            [
                {"title": "商品A", "price": 10},
                {"title": "商品B", "price": 20},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    class FakePlanner:
        def __init__(self):
            self.counter = 0

        def run(self, **kwargs):
            self.counter += 1
            return {
                "success": True,
                "task_id": f"task-{self.counter}",
                "product_data": kwargs["product_data"],
                "plan": [{"action": "find_window", "params": {}}],
                "total_steps": 1,
            }

    class FakeExecutor:
        def run(self, plan, task_id="", **kwargs):
            return {
                "success": True,
                "risk_stats": {"high_risk_window_shift_count": 0},
                "recovery_error": "",
            }

    fake_planner = FakePlanner()

    class FakeFactory:
        def create_planner(self):
            return fake_planner

        def create_executor(self):
            return FakeExecutor()

    monkeypatch.setattr("agents.factory.AgentFactory", lambda: FakeFactory())
    result = runner.invoke(cli, ["batch", "--file", str(batch_path), "--plan-out", str(plan_dir)])

    assert result.exit_code == 0
    assert (plan_dir / "task-1.json").exists()
    assert (plan_dir / "task-2.json").exists()


def test_ollama_provider_resolves_model_alias():
    provider = OllamaProvider(model="qwen3-vl")
    provider._list_models = lambda: ["qwen3-vl:8b", "llama3.1:8b"]

    assert provider._resolve_model_name(force_refresh=True) == "qwen3-vl:8b"


def test_ollama_provider_uses_thinking_when_response_empty():
    payload = {
        "response": "",
        "thinking": '{"steps":[{"action":"find_window","params":{}}]}',
    }

    assert OllamaProvider._extract_generate_text(payload) == payload["thinking"]
