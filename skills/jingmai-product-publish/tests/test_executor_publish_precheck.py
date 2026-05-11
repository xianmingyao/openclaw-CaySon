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


def test_executor_coerces_navigate_to_precheck_when_already_inside_publish_flow():
    agent = ExecutorAgent()

    result = agent._coerce_precheck_for_action(
        "navigate_to",
        {
            "status": "error",
            "reason": "当前截图显示京麦客户端工作台，包含发布商品、商品信息、下一步等关键元素。",
            "current_state": "商品基本信息页",
            "suggested_action": "navigate_to",
        },
        history=[{"action": "activate_window", "success": True}],
    )

    assert result["status"] == "ok"
    assert result["suggested_action"] == "proceed"


def test_executor_coerces_navigate_to_precheck_when_llm_reason_says_can_continue():
    agent = ExecutorAgent()

    result = agent._coerce_precheck_for_action(
        "navigate_to",
        {
            "status": "error",
            "reason": "当前截图显示京麦客户端的发布商品流程界面，当前处于商品发布流程中，符合要求，可以继续后续操作。",
            "current_state": "商品基本信息页",
            "suggested_action": "recover",
        },
        history=[{"action": "activate_window", "success": True}],
    )

    assert result["status"] == "ok"
    assert result["suggested_action"] == "proceed"


def test_executor_doc_strict_postcheck_accepts_forward_page_state():
    agent = ExecutorAgent()

    result = agent._apply_doc_strict_guard(
        "navigate_to",
        {
            "action": "navigate_to",
            "doc_strict": True,
            "doc_strict_guard": {
                "postcheck": {
                    "allowed_page_states": ["category_page", "product_info_page"],
                    "required_markers": ["商品标题"],
                    "reject_markers": ["系统错误"],
                }
            },
        },
        {
            "status": "ok",
            "reason": "商品描述 图文编辑 代码编辑",
            "current_state": "商品描述页面",
            "suggested_action": "proceed",
        },
        stage="postcheck",
    )

    assert result["status"] == "ok"
    assert result["page_state"] == "description_page"


def test_executor_select_category_postcheck_accepts_positive_category_page_reason():
    agent = ExecutorAgent()

    result = agent._coerce_postcheck_for_action(
        "select_category",
        {
            "status": "error",
            "reason": "当前页面显示类目选择界面，页面内容完整且可操作，符合流程正常状态，可以继续后续操作。",
            "current_state": "类目选择页",
            "suggested_action": "recover",
            "page_state": "category_page",
        },
        step={"action": "select_category"},
    )

    assert result["status"] == "ok"
    assert result["suggested_action"] == "proceed"


def test_executor_select_category_postcheck_accepts_forward_action_steps():
    agent = ExecutorAgent()

    result = agent._coerce_postcheck_for_action(
        "select_category",
        {
            "status": "error",
            "reason": "当前页面未显示类目路径，但页面主要展示商品信息填写内容。",
            "current_state": "未知",
            "suggested_action": "recover",
        },
        step={"action": "select_category"},
        act_result={"success": True, "steps": ["search", "next", "product_info_ready"]},
    )

    assert result["status"] == "ok"
    assert result["suggested_action"] == "proceed"
