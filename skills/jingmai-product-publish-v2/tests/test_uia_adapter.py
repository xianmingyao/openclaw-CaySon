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


def test_is_image_upload_slot_candidate_matches_real_empty_slot_controls():
    assert RealWindowsUIAAdapter._is_image_upload_slot_candidate(
        "DataItem",
        "请上传图片",
        1011,
        226,
        1795,
        336,
    ) is True
    assert RealWindowsUIAAdapter._is_image_upload_slot_candidate(
        "Image",
        "",
        1051,
        263,
        1068,
        280,
    ) is True


def test_is_image_upload_slot_candidate_excludes_header_icon():
    assert RealWindowsUIAAdapter._is_image_upload_slot_candidate(
        "Image",
        "",
        1066,
        197,
        1081,
        211,
    ) is False


def test_normalize_image_upload_slot_snapshot_ignores_small_plus_icon():
    snapshot = {
        "class_name": "Image",
        "text": "",
        "bounds": {"left": 1051, "top": 263, "right": 1068, "bottom": 280},
    }
    assert RealWindowsUIAAdapter._normalize_image_upload_slot_snapshot(snapshot) is None


def test_normalize_image_upload_slot_snapshot_marks_empty_list_item_as_empty_slot():
    snapshot = {
        "class_name": "ListItem",
        "text": "",
        "bounds": {"left": 1000, "top": 226, "right": 1128, "bottom": 336},
    }
    normalized = RealWindowsUIAAdapter._normalize_image_upload_slot_snapshot(snapshot)
    assert normalized == {
        "class_name": "DataItem",
        "text": "请上传图片",
        "status": "empty",
        "bounds": {"left": 1000, "top": 226, "right": 1128, "bottom": 336},
    }


def test_merge_image_upload_slot_snapshot_prefers_empty_over_filled_for_same_slot():
    snapshots = [
        {
            "class_name": "DataItem",
            "text": "请上传图片",
            "status": "empty",
            "bounds": {"left": 1000, "top": 226, "right": 1128, "bottom": 336},
        }
    ]
    candidate = {
        "class_name": "Image",
        "text": "",
        "status": "filled",
        "bounds": {"left": 1048, "top": 262, "right": 1069, "bottom": 281},
    }
    RealWindowsUIAAdapter._merge_image_upload_slot_snapshot(snapshots, candidate)
    assert snapshots == [
        {
            "class_name": "DataItem",
            "text": "请上传图片",
            "status": "empty",
            "bounds": {"left": 1000, "top": 226, "right": 1128, "bottom": 336},
        }
    ]
