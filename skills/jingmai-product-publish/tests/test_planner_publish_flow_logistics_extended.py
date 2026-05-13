import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.planner import PlannerAgent


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

    assert fields["basic_info"][0]["value"] == "公牛"
    assert fields["basic_info"][2]["value"] == "8位"
    assert fields["sales_attributes"][0]["value"] == "10A"
    assert fields["sales_attributes"][1]["value"] == "250V"
    assert fields["logistics"][1]["value"] == "个"
    assert fields["logistics"][7]["value"] == "数量：2"


def test_required_visual_fields_include_sku_image_section():
    fields = PlannerAgent._build_required_visual_fields(
        {
            "sku_image": r"E:\images\square.jpg",
            "transparent_image": r"E:\images\transparent.png",
        }
    )

    assert fields["sku_images"][0]["field"] == "sku_square_image"
    assert fields["sku_images"][0]["value"] == r"E:\images\square.jpg"
    assert fields["sku_images"][1]["field"] == "sku_transparent_image"
    assert fields["sku_images"][1]["value"] == r"E:\images\transparent.png"
