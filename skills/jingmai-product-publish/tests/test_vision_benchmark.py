from tools.vision_benchmark import build_report, score_case


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
