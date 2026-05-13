import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.planner import PlannerAgent


def _field_map(items):
    return {item["field"]: item for item in items}


def test_required_visual_fields_reuses_existing_product_values_extended_logistics():
    fields = PlannerAgent._build_required_visual_fields(
        {
            "brand": "公牛",
            "model": "无",
            "unit": "个",
            "notes": "数量：2",
            "attributes": {
                "socket_config": "8位",
                "rated_voltage": "250V",
                "cable_length": "1.6米",
                "current": "10A",
            },
        }
    )

    basic_info_fields = _field_map(fields["basic_info"])
    sales_fields = _field_map(fields["sales_attributes"])
    logistics_fields = _field_map(fields["logistics"])
    assert basic_info_fields["brand"]["value"] == "公牛"
    assert basic_info_fields["socket_config"]["value"] == "8位"
    assert sales_fields["current"]["value"] == "10A"
    assert sales_fields["rated_voltage"]["value"] == "250V"
    assert logistics_fields["sales_unit"]["value"] == "个"
    assert logistics_fields["packing_list"]["value"] == "数量：2"


def test_required_visual_fields_include_sku_image_section():
    fields = PlannerAgent._build_required_visual_fields(
        {
            "sku_image": r"E:\images\square.jpg",
            "transparent_image": r"E:\images\transparent.png",
        }
    )

    assert fields["sku_images"][0]["field"] == "sku_square_image"
    assert fields["sku_images"][0]["value"] == r"E:\images\square.jpg"
    assert fields["sku_images"][0]["interaction_strategy"]["container_component"] == "scrollable_table"
    assert fields["sku_images"][1]["field"] == "sku_transparent_image"
    assert fields["sku_images"][1]["value"] == r"E:\images\transparent.png"


def test_required_visual_fields_derive_pricing_defaults_from_jd_price():
    fields = PlannerAgent._build_required_visual_fields(
        {
            "jd_price": 70,
        }
    )

    assert fields["pricing"][0]["value"] == 82.35
    assert fields["pricing"][1]["value"] == 70
    assert fields["pricing"][2]["value"] == 66.5
