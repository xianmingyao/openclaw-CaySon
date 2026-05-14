import pytest

from jingmai_publish.desktop.uia_adapter import RealWindowsUIAAdapter, UIATuningConfig


def test_normalize_handle_supports_string_and_int():
    assert RealWindowsUIAAdapter._normalize_handle("1234") == 1234
    assert RealWindowsUIAAdapter._normalize_handle(5678) == 5678


def test_import_pywinauto_error_message(monkeypatch, tmp_path):
    adapter = RealWindowsUIAAdapter(screenshot_dir=tmp_path)

    real_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("pywinauto"):
            raise ImportError("missing")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)
    with pytest.raises(RuntimeError, match="pywinauto"):
        adapter._import_pywinauto()


def test_score_candidate_prefers_exact_button_match():
    adapter = RealWindowsUIAAdapter(tuning=UIATuningConfig(), screenshot_dir="logs/screenshots")
    score_button, reasons_button = adapter._score_candidate("发布商品", "发布商品", "Button")
    score_text, reasons_text = adapter._score_candidate("发布商品", "发布商品设置", "Text")
    assert score_button > score_text
    assert "exact_text:发布商品" in reasons_button
    assert "preferred_class" in reasons_button


def test_score_candidate_supports_alias_match():
    adapter = RealWindowsUIAAdapter(
        tuning=UIATuningConfig(click_text_aliases={"发布商品": ["发布"]}),
        screenshot_dir="logs/screenshots",
    )
    score, reasons = adapter._score_candidate("发布商品", "发布", "MenuItem")
    assert score > 0
    assert "exact_text:发布" in reasons


def test_expand_target_texts_merges_aliases_without_duplicates():
    adapter = RealWindowsUIAAdapter(
        tuning=UIATuningConfig(click_text_aliases={"发布商品": ["发布", "发布"]}),
        screenshot_dir="logs/screenshots",
    )
    assert adapter._expand_target_texts("发布商品") == ["发布商品", "发布"]
