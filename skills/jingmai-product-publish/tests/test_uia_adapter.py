import sys
import types

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


def test_list_windows_skips_backend_enumeration_errors(monkeypatch):
    adapter = RealWindowsUIAAdapter(screenshot_dir="logs/screenshots")

    class BrokenDesktop:
        def windows(self):
            raise RuntimeError("invalid transient handle")

    monkeypatch.setattr(adapter, "_iter_desktops", lambda: [BrokenDesktop()])

    assert adapter.list_windows() == []


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
        649,
        343,
        1888,
        453,
    ) is True
    assert RealWindowsUIAAdapter._is_image_upload_slot_candidate(
        "Button",
        "请上传主图",
        650,
        660,
        780,
        780,
    ) is True
    assert RealWindowsUIAAdapter._is_image_upload_slot_candidate(
        "DataItem",
        "请上传透图",
        1887,
        660,
        2020,
        780,
    ) is True
    assert RealWindowsUIAAdapter._is_image_upload_slot_candidate(
        "ListItem",
        "",
        665,
        356,
        730,
        421,
    ) is True
    assert RealWindowsUIAAdapter._is_image_upload_slot_candidate(
        "DataItem",
        "请上传图片",
        1887,
        343,
        2278,
        453,
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


def test_normalize_image_upload_slot_snapshot_preserves_product_image_slot_text():
    snapshot = {
        "class_name": "Button",
        "text": "请上传主图",
        "bounds": {"left": 1000, "top": 666, "right": 1128, "bottom": 786},
    }
    normalized = RealWindowsUIAAdapter._normalize_image_upload_slot_snapshot(snapshot)
    assert normalized == {
        "class_name": "DataItem",
        "text": "请上传主图",
        "status": "empty",
        "bounds": {"left": 1000, "top": 666, "right": 1128, "bottom": 786},
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


def test_merge_image_upload_slot_snapshot_promotes_large_uploaded_image():
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
        "bounds": {"left": 1004, "top": 230, "right": 1122, "bottom": 334},
    }
    RealWindowsUIAAdapter._merge_image_upload_slot_snapshot(snapshots, candidate)
    assert snapshots == [
        {
            "class_name": "Image",
            "text": "",
            "status": "filled",
            "bounds": {"left": 1004, "top": 230, "right": 1122, "bottom": 334},
        }
    ]


def test_is_picker_image_candidate_accepts_thumbnail_without_text():
    assert RealWindowsUIAAdapter._is_picker_image_candidate("Image", "", 500, 260, 620, 380) is True
    assert RealWindowsUIAAdapter._is_picker_image_candidate("ListItem", "", 500, 260, 620, 380) is True
    assert RealWindowsUIAAdapter._is_picker_image_candidate("DataItem", "请上传图片", 500, 260, 620, 380) is False


def test_click_picker_file_card_by_name_clicks_thumbnail_above_label(monkeypatch):
    adapter = RealWindowsUIAAdapter(screenshot_dir="logs/screenshots")
    clicked: list[tuple[int, int]] = []
    selected = {"count": 0}

    class Rect:
        def __init__(self, left: int, top: int, right: int, bottom: int) -> None:
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    class FakeControl:
        def window_text(self) -> str:
            return "main-probe.png"

        def rectangle(self) -> Rect:
            return Rect(486, 480, 620, 505)

    class FakeWindow:
        def descendants(self):
            return [FakeControl()]

    def fake_click(coords):
        clicked.append(coords)
        selected["count"] = 1

    fake_pywinauto = types.ModuleType("pywinauto")
    fake_pywinauto.mouse = types.SimpleNamespace(click=fake_click)
    monkeypatch.setitem(sys.modules, "pywinauto", fake_pywinauto)
    monkeypatch.setattr(adapter, "_get_window", lambda handle: FakeWindow())
    monkeypatch.setattr(adapter, "read_document_text", lambda handle: f"已选{selected['count']}个，可选10个")

    assert adapter._click_picker_file_card_by_name("1187102", "main-probe.png", "main-probe") is True
    assert clicked == [(553, 400)]


def test_picker_selected_count_reads_zero_and_positive(monkeypatch):
    adapter = RealWindowsUIAAdapter(screenshot_dir="logs/screenshots")
    monkeypatch.setattr(adapter, "read_document_text", lambda handle: "共10000条 已选0个，可选10个 确定")
    assert adapter._picker_selected_count("1187102") == 0

    monkeypatch.setattr(adapter, "read_document_text", lambda handle: "已选 3 个，可选10个")
    assert adapter._picker_selected_count("1187102") == 3


def test_image_upload_slot_sort_key_keeps_main_image_before_transparent_image():
    slots = [
        {"class_name": "DataItem", "bounds": {"left": 1887, "top": 343, "right": 2278, "bottom": 453}},
        {"class_name": "DataItem", "bounds": {"left": 665, "top": 356, "right": 730, "bottom": 421}},
    ]
    slots.sort(key=RealWindowsUIAAdapter._image_upload_slot_sort_key)
    assert slots[0]["bounds"]["left"] == 665
    assert slots[1]["bounds"]["left"] == 1887


def test_hover_text_by_index_moves_to_indexed_text(monkeypatch):
    adapter = RealWindowsUIAAdapter(screenshot_dir="logs/screenshots")
    moved: list[tuple[int, int]] = []

    class Rect:
        def __init__(self, left: int, top: int, right: int, bottom: int) -> None:
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    class FakeControl:
        def __init__(self, text: str, rect: Rect) -> None:
            self._text = text
            self._rect = rect

        def window_text(self) -> str:
            return self._text

        def rectangle(self) -> Rect:
            return self._rect

    class FakeWindow:
        def descendants(self):
            return [
                FakeControl("请上传图片", Rect(100, 100, 140, 140)),
                FakeControl("请上传图片", Rect(300, 200, 360, 260)),
            ]

    class FakeDesktop:
        def __init__(self, backend: str) -> None:
            self.backend = backend

        def window(self, handle: int):
            return FakeWindow()

    fake_pywinauto = types.ModuleType("pywinauto")
    fake_pywinauto.mouse = types.SimpleNamespace(move=lambda coords: moved.append(coords))
    monkeypatch.setitem(sys.modules, "pywinauto", fake_pywinauto)
    monkeypatch.setattr(adapter, "_import_pywinauto", lambda: (FakeDesktop, None))

    assert adapter.hover_text_by_index("1187102", "请上传图片", 1) is True
    assert moved == [(330, 230)]


def test_click_local_upload_entry_supports_oxygen_vision_panel(monkeypatch):
    adapter = RealWindowsUIAAdapter(screenshot_dir="logs/screenshots")
    calls: list[tuple[float, float, float, float]] = []

    def fake_click_text_in_region(handle, text, *, min_x_ratio, max_x_ratio, min_y_ratio, max_y_ratio):
        calls.append((min_x_ratio, max_x_ratio, min_y_ratio, max_y_ratio))
        return min_y_ratio == 0.60 and max_y_ratio == 0.82

    monkeypatch.setattr(adapter, "click_text_in_region", fake_click_text_in_region)
    monkeypatch.setattr(adapter, "inspect_image_upload_slots", lambda handle: [])
    monkeypatch.setattr(adapter, "click_text", lambda handle, text: False)

    assert adapter.click_local_upload_entry("1187102", 0) is True
    assert (0.75, 0.95, 0.60, 0.82) in calls
