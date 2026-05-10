import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.planner import PlannerAgent


def test_template_plan_uses_direct_publish_flow():
    agent = PlannerAgent()

    plan = agent._template_plan(
        {
            "title": "测试商品",
            "price": 70,
            "category": "插座",
        }
    )

    assert [step["action"] for step in plan] == [
        "find_window",
        "activate_window",
        "navigate_to",
        "select_category",
        "fill_product_info",
        "fill_product_description",
        "publish_product",
        "verify_result",
    ]
    fill_step = next(step for step in plan if step["action"] == "fill_product_info")
    required_fields = fill_step["params"]["required_visual_fields"]
    assert [item["field"] for item in required_fields["basic_info"]] == [
        "brand",
        "model",
        "socket_config",
        "rated_voltage",
        "cable_length",
    ]
    assert [item["field"] for item in required_fields["sales_attributes"]] == ["current", "sku_image"]
    assert [item["field"] for item in required_fields["description"]] == ["detail_content"]
    assert [item["field"] for item in required_fields["logistics"]] == [
        "sales_unit",
        "package_type",
        "special_delivery_mark",
        "packing_list",
        "warranty_period",
    ]


def test_planner_canonicalizes_legacy_draft_then_publish_sequence():
    agent = PlannerAgent()

    canonical = agent._canonicalize_publish_plan(
        [
            {"action": "find_window", "params": {}},
            {"action": "activate_window", "params": {}},
            {"action": "navigate_to", "params": {"page": "publish"}},
            {"action": "fill_text", "params": {"field": "title", "text": "测试商品"}},
            {"action": "fill_product_info", "params": {"product": {"title": "测试商品"}}},
            {"action": "fill_product_description", "params": {"product": {"title": "测试商品"}}},
            {"action": "save_draft", "params": {}},
            {"action": "verify_result", "params": {"check_errors": True}},
            {"action": "publish_product", "params": {}},
            {"action": "verify_result", "params": {"check_errors": True}},
        ]
    )

    assert [step["action"] for step in canonical] == [
        "find_window",
        "activate_window",
        "navigate_to",
        "fill_text",
        "fill_product_info",
        "fill_product_description",
        "publish_product",
        "verify_result",
    ]


def test_required_visual_fields_reuses_existing_product_values():
    fields = PlannerAgent._build_required_visual_fields(
        {
            "brand": "公牛",
            "model": "无",
            "unit": "个",
            "notes": "数量：2",
            "attributes": {
                "socket_config": "八位",
                "rated_voltage": "250V",
                "cable_length": "1.6米",
                "current": "10A",
            },
        }
    )

    assert fields["basic_info"][0]["value"] == "公牛"
    assert fields["basic_info"][2]["value"] == "八位"
    assert fields["sales_attributes"][0]["value"] == "10A"
    assert fields["logistics"][0]["value"] == "个"
    assert fields["logistics"][3]["value"] == "数量：2"
