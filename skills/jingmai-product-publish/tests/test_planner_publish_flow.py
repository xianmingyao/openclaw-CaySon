import sys
from pathlib import Path
import zipfile

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
        "procurement_erp",
    ]
    assert [item["field"] for item in required_fields["pricing"]] == [
        "market_price",
        "jd_price",
        "purchase_price",
    ]
    assert [item["field"] for item in required_fields["sales_attributes"]] == ["current", "rated_voltage", "lead_time", "sku_image"]
    assert [item["field"] for item in required_fields["description"]] == ["detail_content", "description_images"]
    assert [item["field"] for item in required_fields["logistics"]] == [
        "shelf_life_days",
        "sales_unit",
        "package_spec",
        "package_spec_unit",
        "package_type",
        "special_delivery_mark",
        "hazardous_goods",
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
    assert fields["sales_attributes"][1]["value"] == "250V"
    assert fields["logistics"][0]["value"] == "个"
    assert fields["logistics"][3]["value"] == "数量：2"


def test_doc_strict_template_tracks_workflow_doc_metadata():
    agent = PlannerAgent()

    plan = agent._template_plan(
        {
            "title": "测试商品",
            "price": 70,
            "category": "插座",
        },
        workflow_policy="doc_strict",
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
    assert all(step["workflow_source"].endswith(".docx") for step in plan)
    assert plan[3]["workflow_section"] == "选择商品所属类目"
    assert plan[4]["workflow_section"] == "商品信息 / 物流售后及其他"
    assert plan[5]["workflow_section"] == "规格描述"
    assert "选择所上架的商品所属的类目" in plan[3]["workflow_requirement"]
    assert "商品基本信息" in plan[4]["workflow_excerpt"]
    assert "物流售后及其他" in plan[4]["workflow_excerpt"]
    assert "商品规格描述" in plan[5]["workflow_excerpt"]
    assert plan[3]["workflow_paragraphs"]
    assert plan[4]["workflow_paragraphs"]
    assert plan[5]["workflow_paragraphs"]


def test_doc_strict_batch_template_splits_info_and_sku_phases():
    agent = PlannerAgent()

    plan = agent._template_plan(
        {
            "title": "批量测试商品",
            "price": 70,
            "category": "插座",
            "publish_mode": "batch",
        },
        workflow_policy="doc_strict",
    )

    assert [step["action"] for step in plan] == [
        "find_window",
        "activate_window",
        "navigate_to",
        "select_category",
        "fill_product_info",
        "fill_product_info",
        "fill_product_description",
        "publish_product",
        "verify_result",
    ]
    assert plan[4]["phase"] == "product_basic_ready"
    assert plan[4]["params"]["field_groups"] == ["basic_info", "attributes"]
    assert plan[4]["params"]["batch_scope"] == "product_basic"
    assert plan[5]["phase"] == "batch_sku_ready"
    assert plan[5]["params"]["field_groups"] == ["pricing", "sales_attributes", "logistics"]
    assert plan[5]["params"]["batch_scope"] == "sku_batch"
    assert plan[5]["params"]["publish_mode"] == "batch"
    assert plan[6]["params"]["batch_scope"] == "description_assets"


def test_plan_doc_strict_skips_llm_planning(monkeypatch):
    agent = PlannerAgent()
    called = {"llm": 0}

    def fake_llm_plan(*args, **kwargs):
        called["llm"] += 1
        return [{"action": "bad_plan", "params": {}}]

    monkeypatch.setattr(agent, "_llm_plan", fake_llm_plan)
    monkeypatch.setattr(agent, "_capture_screen_context", lambda: {})

    result = agent.run(
        product_data={"title": "测试商品", "category": "插座", "publish_mode": "single"},
        workflow_policy="doc_strict",
    )

    assert result["success"] is True
    assert called["llm"] == 0
    assert result["plan"][0]["action"] == "find_window"


def test_doc_strict_template_attaches_page_guards():
    agent = PlannerAgent()

    plan = agent._template_plan(
        {
            "title": "测试商品",
            "price": 70,
            "category": "插座",
            "brand": "公牛",
        },
        workflow_policy="doc_strict",
    )
    plan = agent._attach_react_contracts(plan, {"title": "测试商品", "price": 70, "category": "插座", "brand": "公牛"})

    navigate_step = next(step for step in plan if step["action"] == "navigate_to")
    fill_step = next(step for step in plan if step["action"] == "fill_product_info")

    assert navigate_step["doc_strict"] is True
    assert navigate_step["doc_strict_guard"]["precheck"]["allowed_page_states"] == [
        "browser_host",
        "unknown",
        "product_list_page",
        "category_page",
        "product_info_page",
    ]
    assert navigate_step["doc_strict_guard"]["postcheck"]["allowed_page_states"] == ["category_page", "product_info_page"]
    assert "类目" in navigate_step["react_contract"]["postcheck"]["expect_any"]
    assert fill_step["doc_strict_guard"]["precheck"]["allowed_page_states"] == ["product_info_page"]
    assert fill_step["doc_strict_guard"]["recovery_hint"] == "navigate_to"
    assert "商品标题" in fill_step["react_contract"]["postcheck"]["expect_any"]


def test_doc_strict_category_guard_uses_leaf_markers_for_nested_path():
    guard = PlannerAgent._build_doc_strict_guard(
        "select_category",
        {
            "search_text": "电脑、办公 > 外设产品 > 插座/转换器",
        },
    )

    precheck_markers = guard["precheck"]["required_markers"]
    postcheck_markers = guard["postcheck"]["required_markers"]

    assert "电脑、办公 > 外设产品 > 插座/转换器" in precheck_markers
    assert "插座" in precheck_markers
    assert "转换器" in precheck_markers
    assert "转换器" in postcheck_markers


def test_build_doc_step_specs_from_paragraphs_uses_real_doc_content():
    paragraphs = [
        "京麦商品上柜指南",
        "京麦上柜操作路径：首页→商品→发布商品→选择商品所属类目。",
        "第一步：首页点击商品—发布商品",
        "第二步：选择所上架的商品所属的类目，从一级类目到最末级类目依次选择。",
        "在选择了末级类目之后，系统会自动匹配品牌。",
        "商品信息",
        "商品基本信息",
        "商品基本信息包含标品选择、商品标题、品牌、短标题、型号。",
        "采销信息",
        "价格",
        "商品属性",
        "商品规格描述",
        "商品图片",
        "商品描述",
        "物流售后及其他",
        "商品物流",
        "商品售后及其他",
        "最后再检查所有带星号的信息都填写完整之后点击发布商品—继续发布就进入采销审核阶段。",
    ]

    specs = PlannerAgent._build_doc_step_specs_from_paragraphs(paragraphs)

    assert [step["action"] for step in specs] == [
        "find_window",
        "activate_window",
        "navigate_to",
        "select_category",
        "fill_product_info",
        "fill_product_description",
        "publish_product",
        "verify_result",
    ]
    assert "首页→商品→发布商品" in specs[2]["requirement"]
    assert "选择所上架的商品所属的类目" in specs[3]["requirement"]
    assert "商品基本信息" in specs[4]["excerpt"]
    assert "商品物流" in specs[4]["excerpt"]
    assert specs[4]["params"]["doc_sections"] == [
        "商品信息",
        "商品基本信息",
        "采销信息",
        "价格",
        "商品属性",
        "物流售后及其他",
        "商品物流",
        "商品售后及其他",
    ]
    assert specs[5]["params"]["doc_sections"] == [
        "商品规格描述",
        "商品图片",
        "商品描述",
    ]
    assert "继续发布就进入采销审核阶段" in specs[7]["requirement"]


def test_load_workflow_paragraphs_prefers_original_docx(tmp_path: Path, monkeypatch):
    document_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
      <w:body>
        <w:p><w:r><w:t>京麦商品上架指南</w:t></w:r></w:p>
        <w:p><w:r><w:t>京麦上架操作路径：首页→商品→发布商品→选择商品所属类目。</w:t></w:r></w:p>
        <w:p><w:r><w:t>商品信息</w:t></w:r></w:p>
        <w:p><w:r><w:t>商品基本信息</w:t></w:r></w:p>
      </w:body>
    </w:document>
    """
    docx_path = tmp_path / "京麦上架流程.docx"
    with zipfile.ZipFile(docx_path, "w") as archive:
        archive.writestr("word/document.xml", document_xml)

    monkeypatch.chdir(tmp_path)
    PlannerAgent._load_workflow_paragraphs.cache_clear()
    try:
        paragraphs = PlannerAgent._load_workflow_paragraphs()
    finally:
        PlannerAgent._load_workflow_paragraphs.cache_clear()

    assert paragraphs[:4] == [
        "京麦商品上架指南",
        "京麦上架操作路径：首页→商品→发布商品→选择商品所属类目。",
        "商品信息",
        "商品基本信息",
    ]
