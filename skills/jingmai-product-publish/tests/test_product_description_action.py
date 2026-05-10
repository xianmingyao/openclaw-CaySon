import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_build_description_html_uses_product_fields():
    import actions.form as form_module

    html = form_module._build_description_html(
        {
            "title": "test socket",
            "brand": "BULL",
            "model": "B5440",
            "length_mm": 250,
            "width_mm": 76,
            "height_mm": 29,
            "weight_kg": 0.5,
            "unit": "piece",
            "notes": "contains manual and warranty card",
        }
    )

    assert "test socket" in html
    assert "B5440" in html
    assert "250 x 76 x 29 mm" in html
    assert "contains manual and warranty card" in html


def test_fill_product_description_returns_from_advanced_editor(monkeypatch):
    import actions.form as form_module

    calls = []
    monkeypatch.setattr(form_module, "_return_from_advanced_detail_editor", lambda **kwargs: calls.append("return") or True)
    monkeypatch.setattr(form_module, "_scroll_to_description_section", lambda **kwargs: calls.append("scroll"))
    monkeypatch.setattr(form_module, "_is_advanced_detail_editor", lambda **kwargs: False)
    monkeypatch.setattr(form_module, "_extract_description_images", lambda product: [])
    monkeypatch.setattr(
        form_module,
        "_fill_description_code_editor",
        lambda html, **kwargs: {"success": True, "field": "detail_content", "expected": html},
    )
    monkeypatch.setattr(form_module.time, "sleep", lambda *_args, **_kwargs: None)

    result = form_module.fill_product_description({"detail_content": "<p>test product</p>"}, locator=object())

    assert result["success"] is True
    assert calls[:2] == ["return", "scroll"]


def test_fill_product_description_prefers_backend_image_upload(monkeypatch):
    import actions.form as form_module

    calls = []
    monkeypatch.setattr(form_module, "_return_from_advanced_detail_editor", lambda **kwargs: False)
    monkeypatch.setattr(form_module, "_scroll_to_description_section", lambda **kwargs: calls.append("scroll"))
    monkeypatch.setattr(form_module, "_is_advanced_detail_editor", lambda **kwargs: False)
    monkeypatch.setattr(form_module, "_extract_description_images", lambda product: ["E:/tmp/detail1.png"])
    monkeypatch.setattr(
        form_module,
        "_upload_description_image",
        lambda image_path, **kwargs: calls.append(("upload", image_path)) or {"success": True, "field": "detail_image"},
    )
    monkeypatch.setattr(
        form_module,
        "_fill_description_code_editor",
        lambda html, **kwargs: calls.append(("code", html)) or {"success": True, "field": "detail_content"},
    )

    result = form_module.fill_product_description({"description_images": ["E:/tmp/detail1.png"]}, locator=object())

    assert result["success"] is True
    assert ("upload", "E:/tmp/detail1.png") in calls
    assert not any(call[0] == "code" for call in calls if isinstance(call, tuple))


def test_fill_product_description_falls_back_to_explicit_detail_content(monkeypatch):
    import actions.form as form_module

    calls = []
    monkeypatch.setattr(form_module, "_return_from_advanced_detail_editor", lambda **kwargs: False)
    monkeypatch.setattr(form_module, "_scroll_to_description_section", lambda **kwargs: None)
    monkeypatch.setattr(form_module, "_is_advanced_detail_editor", lambda **kwargs: False)
    monkeypatch.setattr(form_module, "_extract_description_images", lambda product: [])
    monkeypatch.setattr(
        form_module,
        "_fill_description_code_editor",
        lambda html, **kwargs: calls.append(html) or {"success": True, "field": "detail_content", "expected": html},
    )

    result = form_module.fill_product_description({"detail_content": "<p>explicit detail</p>"}, locator=object())

    assert result["success"] is True
    assert calls == ["<p>explicit detail</p>"]


def test_fill_product_description_fails_without_text_or_images(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(form_module, "_return_from_advanced_detail_editor", lambda **kwargs: False)
    monkeypatch.setattr(form_module, "_scroll_to_description_section", lambda **kwargs: None)
    monkeypatch.setattr(form_module, "_is_advanced_detail_editor", lambda **kwargs: False)
    monkeypatch.setattr(form_module, "_extract_description_images", lambda product: [])

    result = form_module.fill_product_description({"title": "test product"}, locator=object())

    assert result["success"] is False
    assert "no description_images available" in result["message"]
