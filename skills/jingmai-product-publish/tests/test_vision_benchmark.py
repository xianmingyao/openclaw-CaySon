from tools.vision_benchmark import build_report, infer_actual_from_signals, score_case


def test_score_case_returns_full_score_for_perfect_match():
    result = score_case(
        {
            "id": "perfect",
            "expected": {
                "page_state": "description_page",
                "should_block_fill_product_info": True,
                "anchors": ["返回商家后台", "京东智铺"],
            },
            "actual": {
                "page_state": "description_page",
                "should_block_fill_product_info": True,
                "anchors": ["返回商家后台", "京东智铺"],
            },
        }
    )

    assert result.score == 100
    assert result.failures == []


def test_build_report_aggregates_scores():
    report = build_report(
        [
            {
                "id": "perfect",
                "expected": {
                    "page_state": "description_page",
                    "should_block_fill_product_info": True,
                    "anchors": ["返回商家后台", "京东智铺"],
                },
                "actual": {
                    "page_state": "description_page",
                    "should_block_fill_product_info": True,
                    "anchors": ["返回商家后台", "京东智铺"],
                },
            },
            {
                "id": "partial",
                "expected": {
                    "page_state": "sku_table_page",
                    "should_block_fill_product_info": False,
                    "anchors": ["SKU属性", "批量导入", "默认全部SKU"],
                },
                "actual": {
                    "page_state": "sku_table_page",
                    "should_block_fill_product_info": False,
                    "anchors": ["SKU属性"],
                },
            },
        ]
    )

    assert report["summary"]["case_count"] == 2
    assert report["summary"]["total_score"] == 180
    assert report["summary"]["average_score"] == 90.0
    assert report["summary"]["full_score_count"] == 1


def test_build_report_counts_full_scores():
    report = build_report(
        [
            {
                "id": "perfect-a",
                "expected": {"page_state": "product_info_page", "should_block_fill_product_info": False, "anchors": ["商品标题"]},
                "actual": {"page_state": "product_info_page", "should_block_fill_product_info": False, "anchors": ["商品标题"]},
            },
            {
                "id": "perfect-b",
                "expected": {"page_state": "description_page", "should_block_fill_product_info": True, "anchors": ["返回商家后台"]},
                "actual": {"page_state": "description_page", "should_block_fill_product_info": True, "anchors": ["返回商家后台"]},
            },
        ]
    )

    assert report["summary"]["full_score_count"] == 2


def test_infer_actual_from_signals_detects_description_page():
    actual = infer_actual_from_signals(
        {
            "signals": {
                "markers": ["返回商家后台", "京东智铺", "详情"],
                "basic_tab": False,
            }
        }
    )

    assert actual["page_state"] == "description_page"
    assert actual["should_block_fill_product_info"] is True


def test_infer_actual_from_signals_detects_sku_table_page():
    actual = infer_actual_from_signals(
        {
            "signals": {
                "markers": ["SKU属性", "批量导入"],
                "basic_tab": True,
                "sku_table_anchor_visible": True,
                "visible_price_row_count": 0,
            }
        }
    )

    assert actual["page_state"] == "sku_table_page"
    assert actual["should_block_fill_product_info"] is False
