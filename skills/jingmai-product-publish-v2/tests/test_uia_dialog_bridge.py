from jingmai_publish.desktop.uia_adapter import RealWindowsUIAAdapter


def test_upload_file_from_active_dialog_returns_not_found_when_no_dialog(monkeypatch):
    """当前没有激活文件对话框时，应返回结构化失败结果。"""

    adapter = RealWindowsUIAAdapter(screenshot_dir="logs/screenshots")

    class FakeDesktop:
        def __init__(self, backend):
            self.backend = backend

        def windows(self):
            return []

    monkeypatch.setattr(adapter, "_import_pywinauto", lambda: (FakeDesktop, None))
    result = adapter.upload_file_from_active_dialog("demo.png")

    assert result["success"] is False
    assert result["error"] == "active_file_dialog_not_found"


def test_pick_dialog_filename_edit_prefers_bottom_filename_box():
    top_edit = object()
    bottom_edit = object()
    picked = RealWindowsUIAAdapter._pick_dialog_filename_edit(
        [
            {"control": top_edit, "bounds": {"left": 210, "top": 44, "right": 980, "bottom": 72}},
            {"control": bottom_edit, "bounds": {"left": 330, "top": 612, "right": 1080, "bottom": 640}},
        ]
    )
    assert picked is bottom_edit


def test_pick_dialog_open_button_prefers_lower_right_button():
    left_button = object()
    right_button = object()
    picked = RealWindowsUIAAdapter._pick_dialog_open_button(
        [
            {"control": left_button, "bounds": {"left": 900, "top": 610, "right": 980, "bottom": 640}},
            {"control": right_button, "bounds": {"left": 1000, "top": 610, "right": 1080, "bottom": 640}},
        ]
    )
    assert picked is right_button


def test_try_navigate_dialog_via_shortcuts_navigates_directory_then_selects_filename(monkeypatch):
    adapter = RealWindowsUIAAdapter(screenshot_dir="logs/screenshots")
    calls: list[str] = []

    class FakeDialog:
        def set_focus(self):
            calls.append("focus")

    def fake_paste_text(value: str):
        calls.append(f"paste:{value}")

    def fake_select(dialog, file_name: str, resolved_path: str, dialog_handle=None):
        calls.append(f"select:{file_name}")
        return {"success": True, "file_path": resolved_path}

    class FakeKeyboard:
        @staticmethod
        def send_keys(value: str, pause: float = 0.0):
            calls.append(f"keys:{value}")

    import sys
    import types

    monkeypatch.setattr(adapter, "_paste_text", fake_paste_text)
    monkeypatch.setattr(adapter, "_try_select_file_after_navigation", fake_select)
    monkeypatch.setitem(sys.modules, "pywinauto.keyboard", types.SimpleNamespace(send_keys=FakeKeyboard.send_keys))

    result = adapter._try_navigate_dialog_via_shortcuts(FakeDialog(), r"E:\demo\folder\sample.png")

    assert result["success"] is True
    assert result["method"] == "alt_d_directory_then_select"
    assert "paste:E:\\demo\\folder" in calls
    assert "select:sample.png" in calls


def test_upload_dialog_candidate_prefers_address_bar_directory_navigation(monkeypatch):
    adapter = RealWindowsUIAAdapter(screenshot_dir="logs/screenshots")
    calls: list[str] = []

    class FakeDialog:
        def wait(self, state: str, timeout: int):
            calls.append(f"wait:{state}:{timeout}")

        def set_focus(self):
            calls.append("focus")

    class FakeDesktop:
        def __init__(self, backend: str):
            self.backend = backend

        def window(self, handle: int):
            calls.append(f"window:{self.backend}:{handle}")
            return FakeDialog()

    def fake_navigate(dialog, resolved_path: str, dialog_handle=None):
        calls.append(f"navigate:{resolved_path}:{dialog_handle}")
        return {"success": True, "file_path": resolved_path, "method": "alt_d_directory_then_select"}

    def fake_fill(dialog, resolved_path: str, dialog_handle=None):
        raise AssertionError("should prefer address-bar directory navigation before filename edit")

    monkeypatch.setattr(adapter, "_import_pywinauto", lambda: (FakeDesktop, None))
    monkeypatch.setattr(adapter, "_try_navigate_dialog_via_shortcuts", fake_navigate)
    monkeypatch.setattr(adapter, "_try_fill_dialog_filename", fake_fill)

    result = adapter._upload_file_via_dialog_candidate(
        {"handle": 123, "title": "打开", "class_name": "#32770"},
        r"E:\workspace\skills\jingmai-product-publish-v2\resources\probe-images\main-probe.png",
    )

    assert result["success"] is True
    assert result["method"] == "alt_d_directory_then_select"
    assert result["backend"] == "win32"
    assert "navigate:E:\\workspace\\skills\\jingmai-product-publish-v2\\resources\\probe-images\\main-probe.png:123" in calls


def test_try_fill_dialog_filename_falls_back_to_click_file_item_when_dialog_stays_open(monkeypatch):
    adapter = RealWindowsUIAAdapter(screenshot_dir="logs/screenshots")

    monkeypatch.setattr(adapter, "_fill_dialog_edit_and_submit", lambda edit, value, button: None)
    monkeypatch.setattr(adapter, "_is_dialog_still_open", lambda handle: True)
    monkeypatch.setattr(adapter, "_try_click_dialog_file_item_and_submit", lambda dialog, file_name, button, handle: True)

    class FakeEdit:
        def friendly_class_name(self):
            return "Edit"

        def window_text(self):
            return ""

        def rectangle(self):
            return type("Rect", (), {"left": 330, "top": 612, "right": 1080, "bottom": 640})()

    class FakeControl:
        def descendants(self):
            return [FakeEdit()]

    result = adapter._try_fill_dialog_filename(FakeControl(), r"E:\demo\folder\sample.png", 123)

    assert result["success"] is True
    assert result["method"] == "filename_edit_then_file_item_submit"


def test_try_select_file_after_navigation_returns_failure_when_dialog_stays_open(monkeypatch):
    adapter = RealWindowsUIAAdapter(screenshot_dir="logs/screenshots")

    monkeypatch.setattr(adapter, "_fill_dialog_edit_and_submit", lambda edit, value, button: None)
    monkeypatch.setattr(adapter, "_is_dialog_still_open", lambda handle: True)
    monkeypatch.setattr(adapter, "_try_click_dialog_file_item_and_submit", lambda dialog, file_name, button, handle: False)

    class FakeEdit:
        def friendly_class_name(self):
            return "Edit"

        def window_text(self):
            return ""

        def rectangle(self):
            return type("Rect", (), {"left": 330, "top": 612, "right": 1080, "bottom": 640})()

    class FakeDialog:
        def descendants(self):
            return [FakeEdit()]

    result = adapter._try_select_file_after_navigation(FakeDialog(), "sample.png", r"E:\demo\folder\sample.png", 123)

    assert result["success"] is False
    assert result["error"] == "dialog_still_open_after_filename_submit"


def test_try_click_dialog_file_item_matches_wrapped_icon_text(monkeypatch):
    adapter = RealWindowsUIAAdapter(screenshot_dir="logs/screenshots")
    clicked: list[str] = []

    monkeypatch.setattr(adapter, "_is_dialog_still_open", lambda handle: False)

    class FakeRect:
        left = 300
        top = 120

    class FakeFileItem:
        def window_text(self):
            return "transparent-pr\nobe.png"

        def friendly_class_name(self):
            return "ListItem"

        def rectangle(self):
            return FakeRect()

        def set_focus(self):
            clicked.append("focus")

        def click_input(self, double: bool = False):
            clicked.append(f"click:{double}")

    class FakeDialog:
        def descendants(self):
            return [FakeFileItem()]

    assert adapter._try_click_dialog_file_item_and_submit(FakeDialog(), "transparent-probe.png", None, 123) is True
    assert clicked == ["focus", "click:True"]
