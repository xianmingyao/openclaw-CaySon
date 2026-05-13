import sys
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def test_activate_publish_section_tab_searches_sidebar_ranges(monkeypatch):
    import actions.form as form_module

    calls = []

    def fake_find_named_control(keyword, control_types, locator=None, log=None, top_range=None, left_range=None):
        calls.append((keyword, top_range, left_range))
        if keyword == "商品物流" and top_range == (520, 1400):
            return (object(), keyword, SimpleNamespace(left=0, top=0, right=10, bottom=10))
        return None

    monkeypatch.setattr(form_module, "_find_named_control", fake_find_named_control)
    monkeypatch.setattr(form_module, "click_uia_element", lambda element, log=None: True)

    result = form_module._activate_publish_section_tab("商品物流", locator=SimpleNamespace())

    assert result is True
    assert any(top_range == (520, 1400) for _, top_range, _ in calls)


def test_fill_labeled_dropdown_field_accepts_validation_clear_for_short_value(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(form_module, "_find_labeled_dropdown_center", lambda *args, **kwargs: (1200, 900))
    monkeypatch.setattr(form_module, "_select_dropdown_option", lambda *args, **kwargs: {"success": True, "method": "keyboard"})
    monkeypatch.setattr(form_module, "_dropdown_selection_confirmed", lambda *args, **kwargs: False)
    monkeypatch.setattr(form_module, "_visible_text_contains", lambda *args, **kwargs: False)

    result = form_module._fill_labeled_dropdown_field(
        "sales_unit",
        ["销售单位"],
        "个",
        locator=SimpleNamespace(),
    )

    assert result["success"] is True
    assert result["verify_success"] is True


def test_fill_product_info_adds_sales_attributes_section(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(form_module, "_is_category_selection_page", lambda **kwargs: False)
    monkeypatch.setattr(form_module, "_ensure_basic_info_page", lambda **kwargs: True)
    monkeypatch.setattr(
        form_module,
        "_fill_title_field_v4",
        lambda *args, **kwargs: {"field": "title", "success": True, "write_success": True, "verify_success": True},
    )
    monkeypatch.setattr(
        form_module,
        "_fill_sku_pricing_fields_v3",
        lambda *args, **kwargs: [{"field": "purchase_price", "success": True, "write_success": True, "verify_success": True}],
    )
    monkeypatch.setattr(
        form_module,
        "_fill_brand_field_v2",
        lambda *args, **kwargs: {"field": "brand", "success": True, "write_success": True, "verify_success": True},
    )
    monkeypatch.setattr(
        form_module,
        "_fill_model_field_v2",
        lambda *args, **kwargs: {"field": "model", "success": True, "write_success": True, "verify_success": True},
    )
    monkeypatch.setattr(form_module, "_fill_supported_attributes", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        form_module,
        "_fill_required_sales_attributes_fields",
        lambda *args, **kwargs: [{"field": "current", "success": True, "write_success": True, "verify_success": True}],
    )
    monkeypatch.setattr(
        form_module,
        "_fill_required_logistics_fields",
        lambda *args, **kwargs: [{"field": "sales_unit", "success": True, "write_success": True, "verify_success": True}],
    )
    monkeypatch.setattr(
        form_module,
        "_fill_required_sku_image_fields",
        lambda *args, **kwargs: [{"field": "sku_square_image", "success": True, "write_success": True, "verify_success": True}],
    )

    result = form_module.fill_product_info(
        {"title": "公牛插座", "brand": "公牛", "model": "GN-B5440", "jd_price": 70, "attributes": {"current": "10A"}},
        locator=SimpleNamespace(),
        required_visual_fields={
            "sales_attributes": [{"field": "current", "label": "电流", "value": "10A"}],
            "logistics": [{"field": "sales_unit", "label": "销售单位", "value": "个"}],
        },
    )

    assert result["success"] is True
    assert result["sections"]["sales_attributes"]["success"] >= 1
    assert "sku_square_image" in result["successful_fields"]
    assert "current" in result["successful_fields"]


def test_fill_product_info_payload_preserves_component_schema(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(form_module, "_is_category_selection_page", lambda **kwargs: False)
    monkeypatch.setattr(form_module, "_ensure_basic_info_page", lambda **kwargs: True)
    monkeypatch.setattr(
        form_module,
        "_fill_title_field_v4",
        lambda *args, **kwargs: {"field": "title", "success": True, "write_success": True, "verify_success": True},
    )
    monkeypatch.setattr(form_module, "_fill_procurement_erp_field", lambda *args, **kwargs: None)
    monkeypatch.setattr(form_module, "_fill_model_field_v2", lambda *args, **kwargs: {"field": "model", "success": True, "write_success": True, "verify_success": True})
    monkeypatch.setattr(form_module, "_fill_sku_pricing_fields_v3", lambda *args, **kwargs: [])
    monkeypatch.setattr(form_module, "_fill_brand_field_v2", lambda *args, **kwargs: {"field": "brand", "success": True, "write_success": True, "verify_success": True})
    monkeypatch.setattr(form_module, "_fill_supported_attributes", lambda *args, **kwargs: [])
    monkeypatch.setattr(form_module, "_fill_required_sales_attributes_fields", lambda *args, **kwargs: [])
    monkeypatch.setattr(form_module, "_fill_required_sku_image_fields", lambda *args, **kwargs: [])
    monkeypatch.setattr(form_module, "_fill_required_logistics_fields", lambda *args, **kwargs: [])

    required_visual_fields = {
        "basic_info": [
            {
                "field": "title",
                "label": "商品名称",
                "value": "公牛插座",
                "component_type": "text_input",
                "interaction_strategy": {"action_type": "direct_input"},
            },
            {
                "field": "brand",
                "label": "品牌",
                "value": "公牛",
                "component_type": "dropdown_searchable",
                "interaction_strategy": {"action_type": "dropdown_select", "keyboard_sequence": ["ArrowDown", "Enter"]},
            },
        ],
        "sales_attributes": [
            {
                "field": "current",
                "label": "电流",
                "value": "10A",
                "component_type": "table_cell_input",
                "interaction_strategy": {"container_component": "scrollable_table"},
            }
        ],
    }

    result = form_module.fill_product_info(
        {"title": "公牛插座", "brand": "公牛", "model": "GN-B5440"},
        locator=SimpleNamespace(),
        required_visual_fields=required_visual_fields,
        field_groups=["basic_info", "sales_attributes"],
    )

    assert result["required_visual_fields"]["basic_info"][0]["component_type"] == "text_input"
    assert result["required_visual_fields"]["basic_info"][1]["interaction_strategy"]["action_type"] == "dropdown_select"
    assert result["required_visual_fields"]["sales_attributes"][0]["interaction_strategy"]["container_component"] == "scrollable_table"


def test_fill_required_sku_image_fields_uploads_square_and_transparent(monkeypatch):
    import actions.form as form_module

    class Rect:
        def __init__(self, left, top, right, bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    class FakeLocator(SimpleNamespace):
        def __init__(self):
            super().__init__(clicks=[])

        def click(self, x, y, delay=0.0):
            self.clicks.append((x, y, delay))
            return True

    upload_calls = []
    locator = FakeLocator()

    monkeypatch.setattr(form_module, "_activate_publish_section_tab", lambda *args, **kwargs: True)
    monkeypatch.setattr(form_module, "_focus_publish_scroll_anchor", lambda *args, **kwargs: True)
    monkeypatch.setattr(
        form_module,
        "_find_named_control",
        lambda keyword, *_args, **_kwargs: (object(), keyword, Rect(430 if keyword == "方图" else 1220, 140, 520 if keyword == "方图" else 1310, 170))
        if keyword in {"方图", "透图"}
        else None,
    )
    monkeypatch.setattr(
        form_module,
        "upload_image",
        lambda image_path, **kwargs: upload_calls.append(image_path) or {"success": True, "method": "file-dialog", "prepared_image": image_path},
    )

    result = form_module._fill_required_sku_image_fields(
        {
            "sku_square_image": r"E:\images\square.jpg",
            "sku_transparent_image": r"E:\images\transparent.png",
        },
        required_visual_fields={
            "sku_images": [
                {"field": "sku_square_image", "label": "方图", "value": r"E:\images\square.jpg"},
                {"field": "sku_transparent_image", "label": "透图", "value": r"E:\images\transparent.png"},
            ]
        },
        locator=locator,
    )

    assert [item["field"] for item in result] == ["sku_square_image", "sku_transparent_image"]
    assert all(item["success"] for item in result)
    assert upload_calls == [r"E:\images\square.jpg", r"E:\images\transparent.png"]
    assert len(locator.clicks) == 2


def test_fill_required_sku_image_fields_reuses_existing_sku_context(monkeypatch):
    import actions.form as form_module

    class Rect:
        def __init__(self, left, top, right, bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    class FakeLocator(SimpleNamespace):
        def __init__(self):
            super().__init__(clicks=[])

        def click(self, x, y, delay=0.0):
            self.clicks.append((x, y, delay))
            return True

    activate_calls = []
    focus_calls = []
    upload_calls = []
    locator = FakeLocator()

    monkeypatch.setattr(form_module, "_classify_fill_page_state", lambda **kwargs: "sku_table_page")
    monkeypatch.setattr(
        form_module,
        "_collect_price_area_template_state",
        lambda **kwargs: {"market_input_visible": True, "jd_input_visible": True, "sku_batch_visible": True},
    )
    monkeypatch.setattr(form_module, "_activate_publish_section_tab", lambda *args, **kwargs: activate_calls.append(args) or True)
    monkeypatch.setattr(form_module, "_focus_publish_scroll_anchor", lambda *args, **kwargs: focus_calls.append(args) or True)
    monkeypatch.setattr(
        form_module,
        "_find_named_control",
        lambda keyword, *_args, **_kwargs: (object(), keyword, Rect(430 if keyword == "方图" else 1220, 140, 520 if keyword == "方图" else 1310, 170))
        if keyword in {"方图", "透图"}
        else None,
    )
    monkeypatch.setattr(
        form_module,
        "upload_image",
        lambda image_path, **kwargs: upload_calls.append(image_path) or {"success": True, "method": "file-dialog", "prepared_image": image_path},
    )

    result = form_module._fill_required_sku_image_fields(
        {
            "sku_square_image": r"E:\images\square.jpg",
            "sku_transparent_image": r"E:\images\transparent.png",
        },
        required_visual_fields={
            "sku_images": [
                {"field": "sku_square_image", "label": "方图", "value": r"E:\images\square.jpg"},
                {"field": "sku_transparent_image", "label": "透图", "value": r"E:\images\transparent.png"},
            ]
        },
        locator=locator,
    )

    assert [item["field"] for item in result] == ["sku_square_image", "sku_transparent_image"]
    assert all(item["success"] for item in result)
    assert activate_calls != []
    assert focus_calls != []
    assert upload_calls == [r"E:\images\square.jpg", r"E:\images\transparent.png"]


def test_click_sku_image_upload_anchor_prefers_consensus_click(monkeypatch):
    import actions.form as form_module

    class Rect:
        def __init__(self, left, top, right, bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    class FakeLocator(SimpleNamespace):
        def __init__(self):
            super().__init__(clicks=[])

        def click(self, x, y, delay=0.0):
            self.clicks.append((x, y, delay))
            return True

    locator = FakeLocator()

    def fake_find_named_control(keyword, *_args, **_kwargs):
        if keyword == "鏂瑰浘":
            return (object(), keyword, Rect(430, 140, 520, 170))
        if keyword == "+":
            return (object(), keyword, Rect(468, 216, 492, 240))
        return None

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator)
    monkeypatch.setattr(form_module, "_find_named_control", fake_find_named_control)
    monkeypatch.setattr(form_module, "click_uia_element", lambda *args, **kwargs: False)

    result = form_module._click_sku_image_upload_anchor(
        "sku_square_image",
        ["鏂瑰浘"],
        locator=locator,
    )

    assert result["success"] is True
    assert result["method"] == "anchor-consensus-click"
    assert result["sources"] == ["label_relative", "uia_plus"] or result["sources"] == ["uia_plus", "label_relative"]
    assert len(locator.clicks) == 1


def test_click_sku_image_upload_anchor_falls_back_to_vision(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_find_named_control", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "actions.navigation.vision_click_text_center",
        lambda **kwargs: {"success": True, "x": 1200, "y": 860},
    )

    result = form_module._click_sku_image_upload_anchor(
        "sku_square_image",
        ["方图"],
        locator=SimpleNamespace(click=lambda *args, **kwargs: True),
    )

    assert result["success"] is True
    assert result["method"] == "vision-text-anchor"


def test_fill_brand_field_prefers_keyboard_first_option_when_dropdown_option_is_visible(monkeypatch):
    import actions.form as form_module

    keypresses = []

    class FakeLocator(SimpleNamespace):
        def click(self, *args, **kwargs):
            return True

    class FakePyAutoGui:
        @staticmethod
        def press(key):
            keypresses.append(key)

    monkeypatch.setitem(sys.modules, "pyautogui", FakePyAutoGui)
    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or FakeLocator())
    monkeypatch.setattr(form_module, "_scroll_publish_page_to_top", lambda **kwargs: None)
    monkeypatch.setattr(form_module, "_page_text_contains", lambda *args, **kwargs: False)
    monkeypatch.setattr(
        form_module,
        "_dropdown_selection_confirmed",
        lambda *args, **kwargs: keypresses == ["down", "enter"],
    )
    monkeypatch.setattr(form_module, "_visible_text_contains", lambda text, **kwargs: "公牛" in str(text))
    monkeypatch.setattr(form_module, "find_jingmai_uia_window", lambda **kwargs: object())
    monkeypatch.setattr(form_module, "_find_named_control", lambda *args, **kwargs: None)
    monkeypatch.setattr(form_module.time, "sleep", lambda *_args, **_kwargs: None)

    result = form_module._fill_brand_field_v2("公牛", locator=FakeLocator())

    assert result["success"] is True
    assert result["method"] == "keyboard-first-option"
    assert keypresses == ["down", "enter"]


def test_fill_sku_product_name_field_uses_current_section_without_rescroll(monkeypatch):
    import actions.form as form_module

    flags = []

    class FakeElement:
        def set_edit_text(self, value):
            self.value = value

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(
        form_module,
        "_find_sku_product_name_target",
        lambda **kwargs: flags.append(kwargs.get("ensure_section")) or (FakeElement(), SimpleNamespace(left=1600, top=640, right=1840, bottom=690)),
    )
    monkeypatch.setattr(
        form_module,
        "_verify_uia_edit_value",
        lambda *args, **kwargs: {"success": True, "actual": "测试SKU", "method": "uia-edit-value", "compare_mode": "contains"},
    )
    monkeypatch.setattr(form_module.time, "sleep", lambda *_args, **_kwargs: None)

    result = form_module._fill_sku_product_name_field("测试SKU", locator=SimpleNamespace(), log=None)

    assert result["success"] is True
    assert flags == [False]


def test_fill_sku_product_name_field_accepts_visible_existing_value(monkeypatch):
    import actions.form as form_module

    class FakeElement:
        def set_edit_text(self, value):
            self.value = value

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(
        form_module,
        "_find_sku_product_name_target",
        lambda **kwargs: (FakeElement(), SimpleNamespace(left=1500, top=640, right=1820, bottom=690)),
    )
    monkeypatch.setattr(form_module, "_verify_uia_edit_value", lambda *args, **kwargs: {"success": False, "actual": "", "message": "uia verify failed"})
    monkeypatch.setattr(form_module, "_visible_text_contains", lambda text, **kwargs: "测试SKU标题" in str(text))
    monkeypatch.setattr(form_module.time, "sleep", lambda *_args, **_kwargs: None)

    result = form_module._fill_sku_product_name_field("测试SKU标题-完整内容", locator=SimpleNamespace(), log=None)

    assert result["success"] is True
    assert result["method"] == "visible-text-existing"


def test_is_advanced_detail_editor_detects_blank_upload_canvas(monkeypatch):
    import actions.form as form_module

    def fake_visible(text, **kwargs):
        text = str(text)
        return text in {"返回商家后台", "商品介绍", "上传图片"}

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_visible_text_contains", fake_visible)

    assert form_module._is_advanced_detail_editor(locator=SimpleNamespace(), log=None) is True


def test_find_price_input_center_prefers_overlap_candidate(monkeypatch):
    import actions.form as form_module

    class Rect:
        def __init__(self, left, top, right, bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    monkeypatch.setattr(form_module, "_find_price_input_center_by_template", lambda *args, **kwargs: None)
    monkeypatch.setattr(form_module, "find_jingmai_uia_window", lambda locator=None, log=None: object())
    monkeypatch.setattr(
        form_module,
        "iter_named_descendants",
        lambda *args, **kwargs: [
            {"name": "京东价(元)", "control_type": "Text", "rect": Rect(1470, 825, 1535, 844), "element": object()}
        ],
    )
    monkeypatch.setattr(
        form_module,
        "_find_named_control",
        lambda *args, **kwargs: (object(), "京东价(元)", Rect(1470, 825, 1535, 844)),
    )
    monkeypatch.setattr(
        form_module,
        "_find_edit_elements",
        lambda *args, **kwargs: [
            (object(), "", Rect(1377, 929, 1460, 961)),
            (object(), "", Rect(1517, 929, 1722, 961)),
        ],
    )

    center = form_module._find_price_input_center("京东价", locator=SimpleNamespace())

    assert center == ((1517 + 1722) // 2, (929 + 961) // 2)


def test_fill_sku_pricing_fields_v3_prefers_uia_write(monkeypatch):
    import actions.form as form_module

    class Rect:
        def __init__(self, left, top, right, bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    class Element:
        def __init__(self):
            self.values = []

        def set_edit_text(self, value):
            self.values.append(value)

    jd_element = Element()
    market_element = Element()
    purchase_element = Element()

    monkeypatch.setattr(form_module, "_ensure_basic_info_page", lambda **kwargs: True)
    monkeypatch.setattr(form_module, "_scroll_to_sku_section", lambda **kwargs: None)
    monkeypatch.setattr(form_module, "_reset_sku_horizontal_scrollbar", lambda: None)
    monkeypatch.setattr(form_module, "_set_sku_horizontal_view", lambda *args, **kwargs: None)
    monkeypatch.setattr(form_module, "_fill_sku_product_name_field", lambda *args, **kwargs: {"field": "sku_product_name", "success": True, "write_success": True, "verify_success": True})
    monkeypatch.setattr(form_module, "_ensure_price_area_visible", lambda **kwargs: {"success": True, "state": {}})
    monkeypatch.setattr(
        form_module,
        "_find_price_input_target",
        lambda label, **kwargs: {
            "市场价": (market_element, Rect(1223, 929, 1406, 961)),
            "采购价": (purchase_element, Rect(1485, 929, 1568, 961)),
            "京东价": (jd_element, Rect(1613, 929, 1847, 983)),
        }.get(label),
    )
    monkeypatch.setattr(form_module, "_find_price_input_center", lambda *args, **kwargs: None)
    monkeypatch.setattr(form_module, "_hover_then_click", lambda *args, **kwargs: True)
    monkeypatch.setattr(form_module, "_write_active_text", lambda *args, **kwargs: {"success": False, "method": "active-write"})
    monkeypatch.setattr(
        form_module,
        "_verify_uia_edit_value",
        lambda field, value, element: {"success": True, "actual": str(value), "expected": str(value), "method": "uia-edit-value", "compare_mode": "numeric"},
    )
    monkeypatch.setattr(form_module, "_verify_text_field", lambda *args, **kwargs: {"success": False, "message": "should not use active verify"})

    result = form_module._fill_sku_pricing_fields_v3(
        {"title": "公牛插座", "market_price": 70, "jd_price": 70, "purchase_price": 66.5},
        locator=SimpleNamespace(),
    )

    assert {item["method"] for item in result if item["field"] in {"market_price", "purchase_price", "jd_price"}} == {"uia-set-edit-text"}
    assert jd_element.values == ["70"]


def test_fill_required_logistics_fields_uses_text_for_sales_unit(monkeypatch):
    import actions.form as form_module

    dropdown_fields = []
    text_fields = []

    monkeypatch.setattr(form_module, "_activate_publish_section_tab", lambda *args, **kwargs: True)
    monkeypatch.setattr(form_module, "_focus_publish_scroll_anchor", lambda *args, **kwargs: True)
    monkeypatch.setattr(
        form_module,
        "_fill_labeled_dropdown_field",
        lambda field, *args, **kwargs: dropdown_fields.append(field) or {"field": field, "success": True, "write_success": True, "verify_success": True},
    )
    monkeypatch.setattr(
        form_module,
        "_fill_labeled_text_field",
        lambda field, *args, **kwargs: text_fields.append(field) or {"field": field, "success": True, "write_success": True, "verify_success": True},
    )

    result = form_module._fill_required_logistics_fields(
        {"sales_unit": "个", "package_type": "盒装", "packing_list": "数量：2"},
        required_visual_fields={
            "logistics": [
                {"field": "sales_unit", "label": "销售单位", "value": "个"},
                {"field": "package_type", "label": "商品包装", "value": "盒装"},
                {"field": "packing_list", "label": "包装清单", "value": "数量：2"},
            ]
        },
        locator=SimpleNamespace(),
    )

    assert "sales_unit" in text_fields
    assert "sales_unit" not in dropdown_fields
    assert "package_type" in dropdown_fields
    assert {item["field"] for item in result} == {"sales_unit", "package_type", "packing_list"}


def test_fill_supported_attributes_skips_current_field(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(
        form_module,
        "_collect_attribute_values",
        lambda product: {
            "socket_config": "4位五孔+4位两孔",
            "rated_voltage": "250V",
            "cable_length": "5米",
            "current": "10A",
        },
    )
    monkeypatch.setattr(
        form_module,
        "_find_labeled_dropdown_center",
        lambda *args, **kwargs: (1200, 900),
    )
    monkeypatch.setattr(
        form_module,
        "_select_dropdown_option",
        lambda *args, **kwargs: {"success": True, "method": "keyboard"},
    )
    monkeypatch.setattr(form_module, "_dropdown_selection_confirmed", lambda *args, **kwargs: True)

    results = form_module._fill_supported_attributes({"attributes": {"current": "10A"}}, locator=SimpleNamespace())

    assert {item["field"] for item in results} == {"socket_config", "rated_voltage", "cable_length"}


def test_normalize_fill_result_preserves_existing_section():
    import actions.form as form_module

    result = form_module._normalize_fill_result(
        {"field": "sku_square_image", "section": "sku_images", "success": True},
        "sales_attributes",
    )

    assert result["section"] == "sku_images"


def test_infer_required_product_values_upgrades_weak_packing_list():
    import actions.form as form_module

    result = form_module._infer_required_product_values(
        {
            "title": "公牛插座 B5440",
            "notes": "数量：2",
        },
        required_visual_fields={"logistics": [{"field": "packing_list", "label": "包装清单", "value": ""}]},
    )

    assert result["product"]["packing_list"] == "公牛插座 B5440 x1"
    assert "packing_list" in result["inferred_values"]


def test_click_sku_image_upload_anchor_retries_after_scroll(monkeypatch):
    import actions.form as form_module

    class Rect:
        def __init__(self, left, top, right, bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    class FakeLocator(SimpleNamespace):
        def __init__(self):
            super().__init__(clicks=[])

        def click(self, x, y, delay=0.0):
            self.clicks.append((x, y, delay))
            return True

    locator = FakeLocator()
    call_state = {"header_calls": 0, "positions": []}

    def fake_find_named_control(keyword, *_args, **_kwargs):
        if keyword == "方图":
            call_state["header_calls"] += 1
            if call_state["header_calls"] == 1:
                return None
            return (object(), keyword, Rect(430, 640, 520, 670))
        if keyword == "+":
            return None
        return None

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator)
    monkeypatch.setattr(form_module, "_find_named_control", fake_find_named_control)
    monkeypatch.setattr(form_module, "_set_sku_horizontal_view", lambda position, log=None: call_state["positions"].append(position))
    monkeypatch.setattr(form_module.time, "sleep", lambda *_args, **_kwargs: None)

    result = form_module._click_sku_image_upload_anchor("sku_square_image", ["方图"], locator=locator)

    assert result["success"] is True
    assert call_state["positions"][:2] == ["left", "center"]
    assert len(locator.clicks) == 1


def test_fill_required_logistics_fields_treats_sales_unit_as_text(monkeypatch):
    import actions.form as form_module

    calls = []
    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_activate_publish_section_tab", lambda *args, **kwargs: True)
    monkeypatch.setattr(form_module, "_focus_publish_scroll_anchor", lambda *args, **kwargs: True)
    monkeypatch.setattr(
        form_module,
        "_fill_labeled_text_field",
        lambda field, labels, value, **kwargs: calls.append(("text", field, tuple(labels), value)) or {
            "field": field,
            "success": True,
            "write_success": True,
            "verify_success": True,
        },
    )
    monkeypatch.setattr(
        form_module,
        "_fill_labeled_dropdown_field",
        lambda field, labels, value, **kwargs: calls.append(("dropdown", field, tuple(labels), value)) or {
            "field": field,
            "success": True,
            "write_success": True,
            "verify_success": True,
        },
    )
    monkeypatch.setattr(form_module, "_visible_text_contains", lambda *args, **kwargs: False)

    results = form_module._fill_required_logistics_fields(
        {"sales_unit": "个", "package_type": "盒装", "packing_list": "数量：2"},
        required_visual_fields={
            "logistics": [
                {"field": "sales_unit", "label": "销售单位", "value": "个"},
                {"field": "package_type", "label": "商品包装", "value": "盒装"},
                {"field": "packing_list", "label": "包装清单", "value": "数量：2"},
            ]
        },
        locator=SimpleNamespace(),
    )

    assert ("text", "sales_unit", ("销售单位",), "个") in calls
    assert ("dropdown", "package_type", ("商品包装",), "盒装") in calls
    assert any(item["field"] == "sales_unit" for item in results)


def test_fill_required_logistics_fields_supports_extended_fields(monkeypatch):
    import actions.form as form_module

    calls = []
    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_activate_publish_section_tab", lambda *args, **kwargs: True)
    monkeypatch.setattr(form_module, "_focus_publish_scroll_anchor", lambda *args, **kwargs: True)
    monkeypatch.setattr(
        form_module,
        "_fill_labeled_text_field",
        lambda field, labels, value, **kwargs: calls.append(("text", field, tuple(labels), value)) or {
            "field": field,
            "success": True,
            "write_success": True,
            "verify_success": True,
        },
    )
    monkeypatch.setattr(
        form_module,
        "_fill_labeled_dropdown_field",
        lambda field, labels, value, **kwargs: calls.append(("dropdown", field, tuple(labels), value)) or {
            "field": field,
            "success": True,
            "write_success": True,
            "verify_success": True,
        },
    )
    monkeypatch.setattr(
        form_module,
        "_fill_hazardous_goods_field",
        lambda value, **kwargs: calls.append(("custom", "hazardous_goods", tuple(), value)) or {
            "field": "hazardous_goods",
            "success": True,
            "write_success": True,
            "verify_success": True,
        },
    )
    monkeypatch.setattr(form_module, "_visible_text_contains", lambda *args, **kwargs: False)

    results = form_module._fill_required_logistics_fields(
        {
            "shelf_life_days": "30",
            "sales_unit": "个",
            "package_spec": "10只/盒",
            "package_spec_unit": "盒",
            "package_type": "盒装",
            "special_delivery_mark": "普通商品",
            "hazardous_goods": "无",
            "packing_list": "数量：1",
            "warranty_period": "1年",
        },
        required_visual_fields={
            "logistics": [
                {"field": "shelf_life_days", "label": "保质期（天）", "value": "30"},
                {"field": "sales_unit", "label": "销售单位", "value": "个"},
                {"field": "package_spec", "label": "包装规格", "value": "10只/盒"},
                {"field": "package_spec_unit", "label": "包装规格单位", "value": "盒"},
                {"field": "package_type", "label": "商品包装", "value": "盒装"},
                {"field": "special_delivery_mark", "label": "特殊发货时效标记", "value": "普通商品"},
                {"field": "hazardous_goods", "label": "是否危险商品", "value": "无"},
                {"field": "packing_list", "label": "包装清单", "value": "数量：1"},
                {"field": "warranty_period", "label": "质保期", "value": "1年"},
            ]
        },
        locator=SimpleNamespace(),
    )

    assert ("text", "shelf_life_days", ("保质期（天）", "保质期(天)", "保质期"), "30") in calls
    assert ("text", "package_spec", ("包装规格",), "10只/盒") in calls
    assert ("dropdown", "package_spec_unit", ("包装规格单位",), "盒") in calls
    assert ("custom", "hazardous_goods", tuple(), "无") in calls
    assert {item["field"] for item in results} == {
        "shelf_life_days",
        "sales_unit",
        "package_spec",
        "package_spec_unit",
        "package_type",
        "special_delivery_mark",
        "hazardous_goods",
        "packing_list",
        "warranty_period",
    }


def test_fill_sku_pricing_fields_v3_prefers_uia_target(monkeypatch):
    import actions.form as form_module

    class Rect:
        def __init__(self, left, top, right, bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    class FakeEdit:
        def __init__(self):
            self.writes = []

        def set_edit_text(self, value):
            self.writes.append(value)

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_ensure_basic_info_page", lambda **kwargs: True)
    monkeypatch.setattr(form_module, "_scroll_to_sku_section", lambda **kwargs: None)
    monkeypatch.setattr(form_module, "_reset_sku_horizontal_scrollbar", lambda: None)
    monkeypatch.setattr(form_module, "_set_sku_horizontal_view", lambda *args, **kwargs: None)
    monkeypatch.setattr(form_module, "_fill_sku_product_name_field", lambda *args, **kwargs: {"field": "sku_product_name", "success": True, "write_success": True, "verify_success": True})
    monkeypatch.setattr(form_module, "_ensure_price_area_visible", lambda **kwargs: {"success": True, "state": {}})
    monkeypatch.setattr(form_module.time, "sleep", lambda *_args, **_kwargs: None)

    market_edit = FakeEdit()
    purchase_edit = FakeEdit()
    jd_edit = FakeEdit()
    monkeypatch.setattr(
        form_module,
        "_find_price_input_target",
        lambda label, **kwargs: (market_edit, Rect(1223, 929, 1406, 961))
        if "市场" in label
        else (purchase_edit, Rect(1350, 929, 1438, 961))
        if "采购" in label
        else (jd_edit, Rect(1485, 929, 1568, 961)),
    )
    monkeypatch.setattr(
        form_module,
        "_verify_uia_edit_value",
        lambda field, value, element: {"success": True, "actual": str(value), "expected": str(value), "method": "uia-edit-value", "compare_mode": "numeric"},
    )

    details = form_module._fill_sku_pricing_fields_v3(
        {"title": "", "market_price": 70, "jd_price": 70},
        locator=SimpleNamespace(),
    )

    assert market_edit.writes == ["70"]
    assert purchase_edit.writes == ["66.5"]
    assert jd_edit.writes == ["70"]
    assert {item["method"] for item in details} == {"uia-set-edit-text"}


def test_infer_required_product_values_uses_visual_defaults():
    import actions.form as form_module

    result = form_module._infer_required_product_values(
        {"title": "测试插座", "price": 70},
        required_visual_fields={
            "basic_info": [{"field": "protection_level", "label": "防护等级", "value": ""}],
            "sales_attributes": [
                {"field": "current", "label": "电流", "value": "10A"},
                {"field": "short_title", "label": "短标题", "value": ""},
                {"field": "gross_margin", "label": "毛利", "value": ""},
            ],
            "logistics": [
                {"field": "sales_unit", "label": "销售单位", "value": "pcs"},
                {"field": "package_type", "label": "商品包装", "value": "盒装"},
            ],
        },
    )

    product = result["product"]
    assert product["jd_price"] == 70
    assert product["market_price"] == 82.35
    assert product["purchase_price"] == 66.5
    assert product["sales_unit"] == "个"
    assert product["package_type"] == "盒装"
    assert product["short_title"] == "测试插座"
    assert product["gross_margin"] == 5.0
    assert product["protection_level"] == "IP20"
    assert product["attributes"]["current"] == "10A"
    report = {item["field"]: item for item in result["required_field_report"]}
    assert report["current"]["status"] == "inferred"
    assert report["short_title"]["status"] == "inferred"
    assert report["gross_margin"]["status"] == "inferred"
    assert report["protection_level"]["status"] == "inferred"


def test_fill_required_sales_attributes_fields_accepts_visible_existing(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_activate_publish_section_tab", lambda *args, **kwargs: True)
    monkeypatch.setattr(form_module, "_focus_publish_scroll_anchor", lambda *args, **kwargs: True)
    monkeypatch.setattr(
        form_module,
        "_fill_labeled_text_field",
        lambda *args, **kwargs: {"field": "current", "success": False, "write_success": True, "verify_success": False},
    )
    monkeypatch.setattr(form_module, "_visible_text_contains", lambda expected, **kwargs: expected == "10A")

    results = form_module._fill_required_sales_attributes_fields(
        {"attributes": {"current": "10A"}},
        required_visual_fields={"sales_attributes": [{"field": "current", "label": "电流", "value": "10A"}]},
        locator=SimpleNamespace(),
    )

    assert results[0]["success"] is True
    assert results[0]["method"] == "visible-text-existing"


def test_fill_required_sales_attributes_fields_accepts_auto_generated_current(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_activate_publish_section_tab", lambda *args, **kwargs: True)
    monkeypatch.setattr(form_module, "_focus_publish_scroll_anchor", lambda *args, **kwargs: True)
    monkeypatch.setattr(form_module, "_set_sku_horizontal_view", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        form_module,
        "_fill_labeled_text_field",
        lambda *args, **kwargs: {"field": "current", "success": False, "write_success": False, "verify_success": False},
    )
    monkeypatch.setattr(
        form_module,
        "_visible_text_contains",
        lambda expected, **kwargs: expected == "自动生成",
    )

    results = form_module._fill_required_sales_attributes_fields(
        {"attributes": {"current": "10A"}},
        required_visual_fields={"sales_attributes": [{"field": "current", "label": "电流", "value": "10A"}]},
        locator=SimpleNamespace(),
    )

    assert results[0]["success"] is True
    assert results[0]["method"] == "field-auto-generated"


def test_fill_required_sales_attributes_fields_supports_voltage_and_lead_time(monkeypatch):
    import actions.form as form_module

    calls = []
    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_activate_publish_section_tab", lambda *args, **kwargs: True)
    monkeypatch.setattr(form_module, "_focus_publish_scroll_anchor", lambda *args, **kwargs: True)
    monkeypatch.setattr(form_module, "_set_sku_horizontal_view", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        form_module,
        "_fill_labeled_text_field",
        lambda field, labels, value, **kwargs: calls.append((field, tuple(labels), value)) or {
            "field": field,
            "success": True,
            "write_success": True,
            "verify_success": True,
        },
    )

    results = form_module._fill_required_sales_attributes_fields(
        {
            "attributes": {"current": "10A", "rated_voltage": "250V"},
            "lead_time": "现货",
        },
        required_visual_fields={
            "sales_attributes": [
                {"field": "current", "label": "电流", "value": "10A"},
                {"field": "rated_voltage", "label": "电压", "value": "250V"},
                {"field": "lead_time", "label": "货期", "value": "现货"},
            ]
        },
        locator=SimpleNamespace(),
    )

    assert [item["field"] for item in results] == ["current", "rated_voltage", "lead_time"]
    assert ("current", ("电流", "请填写电流", "额定电流"), "10A") in calls
    assert ("rated_voltage", ("电压", "请输入电压", "额定电压"), "250V") in calls
    assert ("lead_time", ("货期", "请输入货期"), "现货") in calls


def test_build_fill_product_info_payload_dedupes_field_failures(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(form_module, "_collect_fill_page_state", lambda **kwargs: {})

    payload = form_module._build_fill_product_info_payload(
        [
            {"field": "rated_voltage", "section": "attributes", "success": True, "write_success": True, "verify_success": True},
            {"field": "rated_voltage", "section": "sales_attributes", "success": False, "write_success": False, "verify_success": False},
        ],
        inference={"inferred_values": {}, "unresolved_required_fields": [], "required_field_report": []},
        required_visual_fields={},
        locator=SimpleNamespace(),
        log=None,
        skip_page_guards=True,
    )

    assert payload["success"] is True
    assert payload.get("failed_fields", []) == []


def test_fill_required_sales_attributes_fields_reuses_existing_sku_context(monkeypatch):
    import actions.form as form_module

    activate_calls = []
    focus_calls = []
    reset_calls = []
    fill_calls = []

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_classify_fill_page_state", lambda **kwargs: "sku_table_page")
    monkeypatch.setattr(
        form_module,
        "_collect_price_area_template_state",
        lambda **kwargs: {"market_input_visible": True, "jd_input_visible": True, "sku_batch_visible": True},
    )
    monkeypatch.setattr(form_module, "_activate_publish_section_tab", lambda *args, **kwargs: activate_calls.append(args) or True)
    monkeypatch.setattr(form_module, "_focus_publish_scroll_anchor", lambda *args, **kwargs: focus_calls.append(args) or True)
    monkeypatch.setattr(form_module, "_reset_sku_horizontal_scrollbar", lambda: reset_calls.append("reset"))
    monkeypatch.setattr(form_module, "_set_sku_horizontal_view", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        form_module,
        "_fill_labeled_text_field",
        lambda field, labels, value, **kwargs: fill_calls.append(field) or {
            "field": field,
            "success": True,
            "write_success": True,
            "verify_success": True,
        },
    )
    monkeypatch.setattr(form_module.time, "sleep", lambda *_args, **_kwargs: None)

    results = form_module._fill_required_sales_attributes_fields(
        {
            "attributes": {"current": "10A", "rated_voltage": "250V"},
        },
        required_visual_fields={
            "sales_attributes": [
                {"field": "current", "label": "电流", "value": "10A"},
                {"field": "rated_voltage", "label": "电压", "value": "250V"},
            ]
        },
        locator=SimpleNamespace(),
    )

    assert [item["field"] for item in results] == ["current", "rated_voltage"]
    assert fill_calls == ["current", "rated_voltage"]
    assert activate_calls != []
    assert focus_calls != []
    assert reset_calls == ["reset"]


def test_price_area_ready_requires_real_input_targets():
    import actions.form as form_module

    assert form_module._price_area_ready(
        {
            "text_anchors": ["市场价", "销售属性"],
            "title_visible": False,
            "market_visible": False,
            "jd_visible": False,
            "market_input_visible": False,
            "jd_input_visible": False,
            "sku_batch_visible": False,
        }
    ) is False

    assert form_module._price_area_ready(
        {
            "text_anchors": ["市场价", "销售属性"],
            "title_visible": True,
            "market_visible": True,
            "jd_visible": False,
            "market_input_visible": True,
            "jd_input_visible": False,
            "sku_batch_visible": False,
        }
    ) is True

    assert form_module._price_area_ready(
        {
            "text_anchors": ["SKU灞炴€?", "鎵归噺瀵煎叆"],
            "title_visible": False,
            "market_visible": False,
            "jd_visible": False,
            "market_input_visible": False,
            "jd_input_visible": False,
            "sku_batch_visible": False,
            "sku_table_anchor_visible": True,
        }
    ) is True


def test_find_sku_product_name_target_prefers_label_nearby_edit(monkeypatch):
    import actions.form as form_module

    class Rect:
        def __init__(self, left, top, right, bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    label_rect = Rect(980, 560, 1050, 590)
    edit_rect = Rect(1180, 600, 1600, 638)
    edit = object()

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_scroll_to_sku_section", lambda **kwargs: None)
    monkeypatch.setattr(form_module, "_find_named_control", lambda *args, **kwargs: (object(), "商品名称", label_rect))
    monkeypatch.setattr(form_module, "_find_edit_elements", lambda **kwargs: [(edit, "", edit_rect)])

    target = form_module._find_sku_product_name_target(locator=SimpleNamespace())

    assert target[0] is edit
    assert target[1] is edit_rect


def test_find_price_input_target_falls_back_to_visible_edit_row(monkeypatch):
    import actions.form as form_module

    class Rect:
        def __init__(self, left, top, right, bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    market_edit = object()
    purchase_edit = object()
    jd_edit = object()

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_find_named_control", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        form_module,
        "_find_edit_elements",
        lambda **kwargs: [
            (market_edit, "", Rect(1180, 900, 1280, 936)),
            (purchase_edit, "", Rect(1320, 900, 1420, 936)),
            (jd_edit, "", Rect(1480, 900, 1580, 936)),
        ],
    )

    market_target = form_module._find_price_input_target("市场价", locator=SimpleNamespace())
    purchase_target = form_module._find_price_input_target("采购价", locator=SimpleNamespace())
    jd_target = form_module._find_price_input_target("京东价", locator=SimpleNamespace())

    assert market_target[0] is market_edit
    assert purchase_target[0] is purchase_edit
    assert jd_target[0] is jd_edit


def test_find_visible_price_edit_row_accepts_rows_above_previous_top_cutoff(monkeypatch):
    import actions.form as form_module

    class Rect:
        def __init__(self, left, top, right, bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    market_edit = object()
    purchase_edit = object()
    jd_edit = object()

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(
        form_module,
        "_find_edit_elements",
        lambda **kwargs: [
            (market_edit, "", Rect(1180, 708, 1280, 744)),
            (purchase_edit, "", Rect(1320, 710, 1420, 746)),
            (jd_edit, "", Rect(1480, 712, 1580, 748)),
        ],
    )

    row = form_module._find_visible_price_edit_row(locator=SimpleNamespace())

    assert [item[0] for item in row] == [market_edit, purchase_edit, jd_edit]


def test_find_price_input_target_accepts_lower_visible_inputs(monkeypatch):
    import actions.form as form_module

    class Rect:
        def __init__(self, left, top, right, bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    label_rect = Rect(1180, 1085, 1260, 1115)
    lower_edit = object()

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_find_named_control", lambda *args, **kwargs: (object(), "甯傚満浠?", label_rect))
    monkeypatch.setattr(
        form_module,
        "_find_edit_elements",
        lambda **kwargs: [(lower_edit, "", Rect(1185, 1155, 1295, 1193))],
    )

    target = form_module._find_price_input_target("甯傚満浠?", locator=SimpleNamespace())

    assert target[0] is lower_edit


def test_find_price_input_center_requires_consensus_when_no_direct_target(monkeypatch):
    import actions.form as form_module

    class Rect:
        def __init__(self, left, top, right, bottom):
            self.left = left
            self.top = top
            self.right = right
            self.bottom = bottom

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_find_price_input_target", lambda *args, **kwargs: None)
    monkeypatch.setattr(form_module, "_find_price_input_center_by_template", lambda *args, **kwargs: (1280, 920))
    monkeypatch.setattr(form_module, "find_jingmai_uia_window", lambda *args, **kwargs: object())
    monkeypatch.setattr(form_module, "iter_named_descendants", lambda *args, **kwargs: [])
    monkeypatch.setattr(form_module, "_find_named_control", lambda *args, **kwargs: (object(), "甯傚満浠?", Rect(1100, 820, 1180, 850)))
    monkeypatch.setattr(
        form_module,
        "_find_edit_elements",
        lambda **kwargs: [(object(), "", Rect(1230, 900, 1330, 940))],
    )
    monkeypatch.setattr(form_module, "_find_visible_price_edit_row", lambda **kwargs: [])

    center = form_module._find_price_input_center("甯傚満浠?", locator=SimpleNamespace())

    assert center == (1280, 920)


def test_find_price_input_center_returns_none_when_only_single_source_exists(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_find_price_input_target", lambda *args, **kwargs: None)
    monkeypatch.setattr(form_module, "_find_price_input_center_by_template", lambda *args, **kwargs: (1280, 920))
    monkeypatch.setattr(form_module, "find_jingmai_uia_window", lambda *args, **kwargs: None)
    monkeypatch.setattr(form_module, "_find_visible_price_edit_row", lambda **kwargs: [])

    center = form_module._find_price_input_center("甯傚満浠?", locator=SimpleNamespace())

    assert center is None


def test_ensure_price_area_visible_accepts_sku_table_context_without_vertical_blind_scroll(monkeypatch):
    import actions.form as form_module

    calls = []

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_ensure_basic_info_page", lambda **kwargs: True)
    monkeypatch.setattr(form_module, "_scroll_to_sku_section", lambda **kwargs: calls.append("scroll_sku"))
    monkeypatch.setattr(form_module, "_scroll_price_fields_into_view", lambda **kwargs: calls.append("scroll_price"))
    monkeypatch.setattr(form_module, "_debug_fill_live_context", lambda *args, **kwargs: {})
    monkeypatch.setattr(form_module.time, "sleep", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        form_module,
        "_collect_price_area_template_state",
        lambda **kwargs: {
            "text_anchors": ["SKU灞炴€?", "鎵归噺瀵煎叆"],
            "title_visible": False,
            "market_visible": False,
            "jd_visible": False,
            "market_input_visible": False,
            "jd_input_visible": False,
            "sku_batch_visible": True,
            "sku_table_anchor_visible": True,
            "visible_price_row_count": 0,
        },
    )

    class FakePyAutoGui:
        @staticmethod
        def moveTo(*args, **kwargs):
            calls.append(("moveTo", args))

        @staticmethod
        def scroll(value):
            calls.append(("scroll", value))

    monkeypatch.setitem(sys.modules, "pyautogui", FakePyAutoGui)

    result = form_module._ensure_price_area_visible(locator=SimpleNamespace(), log=None, max_rounds=1)

    assert result["success"] is True
    assert "scroll_sku" in calls
    assert "scroll_price" in calls
    assert not any(isinstance(item, tuple) and item[0] == "scroll" for item in calls)


def test_ensure_price_area_visible_prefers_sku_then_price_scroll(monkeypatch):
    import actions.form as form_module

    calls = []

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_ensure_basic_info_page", lambda **kwargs: calls.append("ensure_basic") or True)
    monkeypatch.setattr(form_module, "_scroll_to_sku_section", lambda **kwargs: calls.append("scroll_sku"))
    monkeypatch.setattr(form_module, "_scroll_price_fields_into_view", lambda **kwargs: calls.append("scroll_price"))
    monkeypatch.setattr(form_module, "_debug_fill_live_context", lambda stage, **kwargs: calls.append(stage) or {})
    monkeypatch.setattr(form_module.time, "sleep", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(form_module, "_classify_fill_page_state", lambda **kwargs: "product_info_page")

    states = iter(
        [
            {
                "text_anchors": [],
                "title_visible": False,
                "market_visible": False,
                "jd_visible": False,
                "market_input_visible": False,
                "jd_input_visible": False,
                "sku_batch_visible": False,
            },
            {
                "text_anchors": ["市场价", "销售属性"],
                "title_visible": True,
                "market_visible": True,
                "jd_visible": False,
                "market_input_visible": True,
                "jd_input_visible": False,
                "sku_batch_visible": False,
            },
        ]
    )
    monkeypatch.setattr(form_module, "_collect_price_area_template_state", lambda **kwargs: next(states))

    class FakePyAutoGui:
        @staticmethod
        def moveTo(*args, **kwargs):
            calls.append(("moveTo", args))

        @staticmethod
        def scroll(value):
            calls.append(("scroll", value))

    monkeypatch.setitem(sys.modules, "pyautogui", FakePyAutoGui)

    result = form_module._ensure_price_area_visible(locator=SimpleNamespace(), log=None, max_rounds=1)

    assert result["success"] is True
    assert "scroll_sku" in calls
    assert "scroll_price" in calls
    assert calls.index("scroll_sku") < calls.index("scroll_price")


def test_price_area_ready_accepts_missing_templates_with_title_context_and_inputs():
    import actions.form as form_module

    assert form_module._price_area_ready(
        {
            "text_anchors": [],
            "title_visible": False,
            "title_context_visible": True,
            "market_visible": False,
            "jd_visible": False,
            "market_input_visible": True,
            "jd_input_visible": True,
            "sku_batch_visible": False,
            "sku_table_anchor_visible": False,
        }
    ) is True


def test_fill_title_field_v4_accepts_existing_visible_title(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(form_module, "_fill_title_field_v2", lambda *args, **kwargs: {"field": "title", "success": False, "write_success": True})
    monkeypatch.setattr(form_module, "_fill_title_field_v3", lambda *args, **kwargs: {"field": "title", "success": False, "write_success": False})
    monkeypatch.setattr(form_module, "_visible_text_contains", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(form_module, "_scroll_publish_page_to_top", lambda **kwargs: None)

    result = form_module._fill_title_field_v4("测试标题前缀-完整内容", locator=SimpleNamespace(), log=None)

    assert result["success"] is True
    assert result["method"] == "visible-text-existing"


def test_fill_title_field_v2_accepts_visible_title_when_uia_value_empty(monkeypatch):
    import actions.form as form_module

    class FakeElement:
        def rectangle(self):
            return SimpleNamespace(left=1200, top=320, right=1800, bottom=360)

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator)
    monkeypatch.setattr(form_module, "_scroll_publish_page_to_top", lambda **kwargs: None)
    monkeypatch.setattr(
        form_module,
        "_find_named_edit_element",
        lambda *args, **kwargs: (FakeElement(), "商品标题", FakeElement().rectangle()),
    )
    monkeypatch.setattr(form_module, "_focus_uia_edit", lambda *args, **kwargs: True)
    monkeypatch.setattr(form_module, "_write_active_text", lambda *args, **kwargs: {"success": True, "method": "clipboard-paste"})
    monkeypatch.setattr(form_module, "_verify_uia_edit_value", lambda *args, **kwargs: {"success": False, "message": "uia edit value empty"})
    monkeypatch.setattr(form_module, "_verify_text_field", lambda *args, **kwargs: {"success": False, "message": "clipboard empty"})
    monkeypatch.setattr(
        form_module,
        "_visible_text_contains",
        lambda expected, **kwargs: expected.startswith("测试标题前缀"),
    )

    result = form_module._fill_title_field_v2(
        "测试标题前缀-完整内容",
        locator=SimpleNamespace(click=lambda *args, **kwargs: True),
    )

    assert result["success"] is True
    assert result["verify_success"] is True
    assert result["verification_method"] == "visible-text-existing"


def test_fill_sku_pricing_fields_v3_skips_seek_when_fail_fast(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_ensure_basic_info_page", lambda **kwargs: True)
    monkeypatch.setattr(form_module, "_scroll_to_sku_section", lambda **kwargs: None)
    monkeypatch.setattr(form_module, "_reset_sku_horizontal_scrollbar", lambda: None)
    monkeypatch.setattr(form_module, "_set_sku_horizontal_view", lambda *args, **kwargs: None)
    monkeypatch.setattr(form_module, "_fill_sku_product_name_field", lambda *args, **kwargs: {"field": "sku_product_name", "success": True})
    monkeypatch.setattr(
        form_module,
        "_collect_price_area_template_state",
        lambda **kwargs: {
            "title_visible": False,
            "title_context_visible": False,
            "market_visible": False,
            "jd_visible": False,
            "market_input_visible": False,
            "jd_input_visible": False,
            "sku_batch_visible": False,
            "sku_table_anchor_visible": False,
            "visible_price_row_count": 0,
        },
    )
    monkeypatch.setattr(
        form_module,
        "_ensure_price_area_visible",
        lambda **kwargs: {
            "success": False,
            "reason": "sku_table_context_without_price_targets",
            "state": {"sku_batch_visible": True, "sku_table_anchor_visible": True},
        },
    )
    seek_calls = []
    monkeypatch.setattr(form_module, "_seek_price_area", lambda **kwargs: seek_calls.append("seek") or {"success": False})

    details = form_module._fill_sku_pricing_fields_v3(
        {"title": "鍏墰鎻掑骇", "market_price": 70, "jd_price": 70},
        locator=SimpleNamespace(),
    )

    assert seek_calls == []
    assert details[-1]["field"] == "price_area_anchor"
    assert "sku_table_context_without_price_targets" in details[-1]["verify_error"]


def test_fill_sku_pricing_fields_v3_skips_seek_when_page_context_is_lost(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_ensure_basic_info_page", lambda **kwargs: True)
    monkeypatch.setattr(form_module, "_scroll_to_sku_section", lambda **kwargs: None)
    monkeypatch.setattr(form_module, "_reset_sku_horizontal_scrollbar", lambda: None)
    monkeypatch.setattr(form_module, "_fill_sku_product_name_field", lambda *args, **kwargs: {"field": "sku_product_name", "success": True})
    monkeypatch.setattr(
        form_module,
        "_collect_price_area_template_state",
        lambda **kwargs: {
            "title_visible": False,
            "title_context_visible": False,
            "market_visible": False,
            "jd_visible": False,
            "market_input_visible": False,
            "jd_input_visible": False,
            "sku_batch_visible": False,
            "sku_table_anchor_visible": False,
            "visible_price_row_count": 0,
        },
    )
    monkeypatch.setattr(
        form_module,
        "_ensure_price_area_visible",
        lambda **kwargs: {
            "success": False,
            "reason": "description_page_context",
            "state": {"sku_batch_visible": False, "sku_table_anchor_visible": False},
        },
    )
    seek_calls = []
    monkeypatch.setattr(form_module, "_seek_price_area", lambda **kwargs: seek_calls.append("seek") or {"success": False})

    details = form_module._fill_sku_pricing_fields_v3(
        {"title": "测试商品", "market_price": 70, "jd_price": 70},
        locator=SimpleNamespace(),
    )

    assert seek_calls == []
    assert details[-1]["field"] == "price_area_anchor"
    assert "description_page_context" in details[-1]["verify_error"]


def test_ensure_price_area_visible_stops_immediately_on_description_page(monkeypatch):
    import actions.form as form_module

    calls = []

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_ensure_basic_info_page", lambda **kwargs: True)
    monkeypatch.setattr(form_module, "_scroll_to_sku_section", lambda **kwargs: calls.append("scroll_sku"))
    monkeypatch.setattr(form_module, "_scroll_price_fields_into_view", lambda **kwargs: calls.append("scroll_price"))
    monkeypatch.setattr(
        form_module,
        "_collect_price_area_template_state",
        lambda **kwargs: {
            "title_visible": False,
            "market_visible": False,
            "jd_visible": False,
            "market_input_visible": False,
            "jd_input_visible": False,
            "sku_batch_visible": False,
            "sku_table_anchor_visible": False,
            "visible_price_row_count": 0,
        },
    )
    monkeypatch.setattr(form_module, "_classify_fill_page_state", lambda **kwargs: "description_page")
    monkeypatch.setattr(form_module, "_debug_fill_live_context", lambda *args, **kwargs: {})
    monkeypatch.setattr(form_module.time, "sleep", lambda *_args, **_kwargs: None)

    class FakePyAutoGui:
        @staticmethod
        def moveTo(*args, **kwargs):
            calls.append(("moveTo", args))

        @staticmethod
        def scroll(value):
            calls.append(("scroll", value))

    monkeypatch.setitem(sys.modules, "pyautogui", FakePyAutoGui)

    result = form_module._ensure_price_area_visible(locator=SimpleNamespace(), log=None, max_rounds=1)

    assert result["success"] is False
    assert result["reason"] == "description_page_context"
    assert calls == []


def test_fill_sku_pricing_fields_v3_stops_before_blind_click_when_price_target_missing(monkeypatch):
    import actions.form as form_module

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_ensure_basic_info_page", lambda **kwargs: True)
    monkeypatch.setattr(form_module, "_scroll_to_sku_section", lambda **kwargs: None)
    monkeypatch.setattr(form_module, "_reset_sku_horizontal_scrollbar", lambda: None)
    monkeypatch.setattr(form_module, "_fill_sku_product_name_field", lambda *args, **kwargs: {"field": "sku_product_name", "success": True})
    monkeypatch.setattr(
        form_module,
        "_collect_price_area_template_state",
        lambda **kwargs: {
            "title_visible": False,
            "title_context_visible": False,
            "market_visible": False,
            "jd_visible": False,
            "market_input_visible": False,
            "jd_input_visible": False,
            "sku_batch_visible": False,
            "sku_table_anchor_visible": False,
            "visible_price_row_count": 0,
        },
    )
    monkeypatch.setattr(
        form_module,
        "_ensure_price_area_visible",
        lambda **kwargs: {
            "success": True,
            "state": {"sku_batch_visible": True, "sku_table_anchor_visible": True},
        },
    )
    monkeypatch.setattr(form_module, "_set_sku_horizontal_view", lambda *args, **kwargs: None)
    monkeypatch.setattr(form_module, "_find_price_input_target", lambda *args, **kwargs: None)
    monkeypatch.setattr(form_module, "_find_price_input_center", lambda *args, **kwargs: None)
    hover_calls = []
    monkeypatch.setattr(form_module, "_hover_then_click", lambda *args, **kwargs: hover_calls.append((args, kwargs)) or True)

    details = form_module._fill_sku_pricing_fields_v3(
        {"title": "", "market_price": 70, "jd_price": 70},
        locator=SimpleNamespace(),
    )

    assert hover_calls == []
    assert details[0]["field"] == "market_price"
    assert details[0]["method"] == "price-target-guard"
    assert details[0]["success"] is False


def test_fill_sku_pricing_fields_v3_reuses_existing_price_context_without_extra_scroll(monkeypatch):
    import actions.form as form_module

    ensure_calls = []
    scroll_calls = []

    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_ensure_basic_info_page", lambda **kwargs: True)
    monkeypatch.setattr(form_module, "_scroll_to_sku_section", lambda **kwargs: scroll_calls.append("scroll_sku"))
    monkeypatch.setattr(form_module, "_reset_sku_horizontal_scrollbar", lambda: None)
    monkeypatch.setattr(form_module, "_set_sku_horizontal_view", lambda *args, **kwargs: None)
    monkeypatch.setattr(form_module, "_fill_sku_product_name_field", lambda *args, **kwargs: {"field": "sku_product_name", "success": True})
    monkeypatch.setattr(
        form_module,
        "_collect_price_area_template_state",
        lambda **kwargs: {
            "text_anchors": [],
            "title_visible": False,
            "title_context_visible": True,
            "market_visible": False,
            "jd_visible": False,
            "market_input_visible": True,
            "jd_input_visible": True,
            "sku_batch_visible": True,
            "sku_table_anchor_visible": False,
            "visible_price_row_count": 4,
        },
    )
    monkeypatch.setattr(
        form_module,
        "_ensure_price_area_visible",
        lambda **kwargs: ensure_calls.append("ensure") or {"success": False},
    )
    monkeypatch.setattr(form_module, "_verify_uia_edit_value", lambda field, expected, element: {"success": True, "actual": str(expected), "method": "uia"})

    class FakeElement:
        def set_edit_text(self, value):
            self.value = value

    rect = SimpleNamespace(left=1000, right=1100, top=600, bottom=640)
    monkeypatch.setattr(form_module, "_find_price_input_target", lambda *args, **kwargs: (FakeElement(), rect))

    details = form_module._fill_sku_pricing_fields_v3(
        {"title": "测试商品", "market_price": 82.35, "purchase_price": 66.5, "jd_price": 70},
        locator=SimpleNamespace(),
    )

    assert ensure_calls == []
    assert scroll_calls == []
    assert all(item.get("success") for item in details if item.get("field") in {"market_price", "purchase_price", "jd_price"})


def test_ensure_price_area_visible_fails_after_first_contextless_scroll(monkeypatch):
    import actions.form as form_module

    calls = []
    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_ensure_basic_info_page", lambda **kwargs: True)
    monkeypatch.setattr(form_module, "_scroll_to_sku_section", lambda **kwargs: calls.append("scroll_sku"))
    monkeypatch.setattr(form_module, "_scroll_price_fields_into_view", lambda **kwargs: calls.append("scroll_price"))
    monkeypatch.setattr(form_module, "_debug_fill_live_context", lambda *args, **kwargs: {})
    monkeypatch.setattr(form_module.time, "sleep", lambda *_args, **_kwargs: None)

    states = iter(
        [
            {
                "title_visible": False,
                "market_visible": False,
                "jd_visible": False,
                "market_input_visible": False,
                "jd_input_visible": False,
                "sku_batch_visible": False,
                "sku_table_anchor_visible": False,
                "visible_price_row_count": 0,
            },
            {
                "title_visible": False,
                "market_visible": False,
                "jd_visible": False,
                "market_input_visible": False,
                "jd_input_visible": False,
                "sku_batch_visible": False,
                "sku_table_anchor_visible": False,
                "visible_price_row_count": 0,
            },
        ]
    )
    page_states = iter(["product_info_page", "product_info_page", "product_info_page"])
    monkeypatch.setattr(form_module, "_collect_price_area_template_state", lambda **kwargs: next(states))
    monkeypatch.setattr(form_module, "_classify_fill_page_state", lambda **kwargs: "product_info_page")
    monkeypatch.setattr(form_module, "_classify_fill_page_state", lambda **kwargs: "product_info_page")
    monkeypatch.setattr(form_module, "_classify_fill_page_state", lambda **kwargs: next(page_states))

    class FakePyAutoGui:
        @staticmethod
        def moveTo(*args, **kwargs):
            calls.append(("moveTo", args))

        @staticmethod
        def scroll(value):
            calls.append(("scroll", value))

    monkeypatch.setitem(sys.modules, "pyautogui", FakePyAutoGui)

    result = form_module._ensure_price_area_visible(locator=SimpleNamespace(), log=None, max_rounds=1)

    assert result["success"] is False
    assert result["reason"] == "page_context_lost_before_price_area"
    assert ("scroll", -240) in calls
    assert ("scroll", -320) not in calls


def test_fill_product_info_stops_after_pricing_context_failure(monkeypatch):
    import actions.form as form_module

    later_calls = []
    monkeypatch.setattr(form_module, "_get_locator", lambda locator, log=None: locator or SimpleNamespace())
    monkeypatch.setattr(form_module, "_ensure_basic_info_page", lambda **kwargs: True)
    monkeypatch.setattr(form_module, "_guard_fill_product_info_page_context", lambda *args, **kwargs: {"success": True, "page_state": "product_info_page"})
    monkeypatch.setattr(form_module, "_is_category_selection_page", lambda **kwargs: False)
    monkeypatch.setattr(
        form_module,
        "_fill_title_field_v4",
        lambda *args, **kwargs: {"field": "title", "success": True, "write_success": True, "verify_success": True},
    )
    monkeypatch.setattr(
        form_module,
        "_fill_model_field_v2",
        lambda *args, **kwargs: {"field": "model", "success": True, "write_success": True, "verify_success": True},
    )
    monkeypatch.setattr(form_module, "_fill_procurement_erp_field", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        form_module,
        "_fill_sku_pricing_fields_v3",
        lambda *args, **kwargs: [
            {
                "field": "price_area_anchor",
                "success": False,
                "write_success": False,
                "verify_success": False,
                "verify_error": "price area not visible (description_page_context)",
                "context_failure_reason": "description_page_context",
            }
        ],
    )
    monkeypatch.setattr(form_module, "_fill_brand_field_v2", lambda *args, **kwargs: later_calls.append("brand") or {"field": "brand", "success": True})
    monkeypatch.setattr(form_module, "_fill_supported_attributes", lambda *args, **kwargs: later_calls.append("attributes") or [])
    monkeypatch.setattr(form_module, "_fill_required_sales_attributes_fields", lambda *args, **kwargs: later_calls.append("sales_attributes") or [])
    monkeypatch.setattr(form_module, "_fill_required_sku_image_fields", lambda *args, **kwargs: later_calls.append("sku_images") or [])
    monkeypatch.setattr(form_module, "_fill_required_logistics_fields", lambda *args, **kwargs: later_calls.append("logistics") or [])

    result = form_module.fill_product_info(
        {"title": "测试商品", "market_price": 70, "jd_price": 70},
        locator=SimpleNamespace(click=lambda *args, **kwargs: True),
    )

    assert result["success"] is False
    assert result["recovery_hint"] == "description_page_context"
    assert result["requires_action"] == "select_category"
    assert later_calls == []
