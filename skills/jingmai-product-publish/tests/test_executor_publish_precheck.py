import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.executor import ExecutorAgent


def test_publish_product_precheck_hint_mentions_submit_button():
    hint = ExecutorAgent._build_precheck_action_hint("publish_product")

    assert "提交发布" in hint
    assert "status=ok" in hint


def test_executor_coerces_publish_product_precheck_when_still_on_publish_form():
    agent = ExecutorAgent()

    result = agent._coerce_precheck_for_action(
        "publish_product",
        {
            "status": "error",
            "reason": '页面显示内容与预期不符，当前应处于商品信息填写页，但实际显示为"发布商品"页（含发布按钮及价格编辑区域）',
            "current_state": "发布商品",
            "suggested_action": "recover",
        },
        history=[{"action": "fill_product_info", "success": True}],
    )

    assert result["status"] == "ok"
    assert result["suggested_action"] == "proceed"


def test_executor_preserves_publish_product_precheck_for_list_page():
    agent = ExecutorAgent()

    result = agent._coerce_precheck_for_action(
        "publish_product",
        {
            "status": "error",
            "reason": "当前页面为商品列表页，未进入发布表单",
            "current_state": "商品列表",
            "suggested_action": "recover",
        },
        history=[{"action": "verify_result", "success": True}],
    )

    assert result["status"] == "error"
