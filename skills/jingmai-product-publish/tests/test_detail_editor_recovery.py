import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_detects_advanced_detail_editor(monkeypatch):
    import actions.form as form_module

    visible = {
        "杩斿洖鍟嗗鍚庡彴": True,
        "浜彴鏅哄簵": True,
        "璇︽儏": True,
        "楂樼骇缂栬緫": False,
    }
    monkeypatch.setattr(
        form_module,
        "_visible_text_contains",
        lambda text, **kwargs: visible.get(text, False),
    )

    assert form_module._is_advanced_detail_editor(locator=object()) is True


def test_ensure_basic_info_page_returns_from_advanced_detail_editor(monkeypatch):
    import actions.form as form_module

    states = {"title_visible": False}

    def fake_visible(text, **kwargs):
        if text == "鍟嗗搧鏍囬":
            return states["title_visible"]
        mapping = {
            "杩斿洖鍟嗗鍚庡彴": True,
            "浜彴鏅哄簵": True,
            "璇︽儏": True,
            "楂樼骇缂栬緫": False,
            "鍟嗗搧鍩烘湰淇℃伅": False,
            "绫荤洰閫夋嫨鍙戝搧": False,
            "涓嬩竴姝ワ紝瀹屽杽鍏朵粬鍟嗗搧淇℃伅": False,
        }
        return mapping.get(text, False)

    clicked = []

    class FakeLocator:
        def click(self, x, y, delay=0.0):
            clicked.append((x, y))
            if (x, y) == (70, 24):
                states["title_visible"] = True
            return True

    monkeypatch.setattr(form_module, "_visible_text_contains", fake_visible)
    monkeypatch.setattr(form_module, "_find_named_control", lambda *args, **kwargs: None)
    monkeypatch.setattr(form_module, "click_uia_element", lambda *args, **kwargs: False)
    monkeypatch.setattr(form_module.time, "sleep", lambda *_args, **_kwargs: None)

    assert form_module._ensure_basic_info_page(locator=FakeLocator()) is True
    assert (70, 24) in clicked
