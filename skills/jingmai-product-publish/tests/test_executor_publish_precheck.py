import sys
from pathlib import Path
from types import SimpleNamespace

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

    assert result["status"] == "error"


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


def test_prepare_resume_context_replays_select_category_when_fill_product_info_starts_on_category_page(monkeypatch):
    agent = ExecutorAgent()
    agent._locator = SimpleNamespace()
    agent._logger = None
    agent._plan = [
        {"action": "fill_product_info", "params": {"product": {"category": "电脑、办公 > 外设产品 > 插座/转换器"}}}
    ]
    calls = []

    monkeypatch.setattr(agent, "_recover_locator", lambda **kwargs: True)
    monkeypatch.setattr(agent, "_detect_local_page_state", lambda action_name="": "category_page" if not calls else "product_info_page")
    monkeypatch.setattr("actions.form._ensure_basic_info_page", lambda **kwargs: False)
    monkeypatch.setattr("actions.form._is_category_selection_page", lambda **kwargs: True)
    monkeypatch.setattr(
        agent,
        "_run_recovery_action",
        lambda action, step_index: calls.append((action, step_index)) or {"success": True, "type": action.get("type")},
    )

    agent._prepare_resume_context("fill_product_info", target_step=1)

    assert calls
    assert calls[0][0]["type"] == "select_category"
    assert calls[0][0]["search_text"] == "电脑、办公 > 外设产品 > 插座/转换器"


def test_executor_passes_precheck_observation_into_fill_product_info_action():
    agent = ExecutorAgent()
    captured = {}

    class DummyBreaker:
        def can_execute(self):
            return True

        def record_failure(self):
            return None

        def record_success(self):
            return None

    agent._circuit_breaker = DummyBreaker()
    agent.start = lambda: None
    agent.finish = lambda *args, **kwargs: None
    agent._check_safety = lambda action_name: True
    agent._ensure_locator = lambda: None
    agent._prepare_resume_context = lambda *args, **kwargs: None
    agent._capture_visual_artifacts = lambda *args, **kwargs: {"primary_path": ""}
    agent._react_precheck = lambda **kwargs: {"status": "ok", "current_state": "商品信息编辑页面", "reason": "可安全继续"}
    agent._coerce_precheck_for_action = lambda action_name, observation, **kwargs: observation
    agent._should_block_precheck = lambda action_name, observation: False
    agent._capture_window_summary = lambda: None
    agent._diff_window_summary = lambda before, after: {}
    agent._log_window_diff_risk = lambda *args, **kwargs: None
    agent._call_react_observe = lambda *args, **kwargs: {"status": "ok", "reason": "ok"}
    agent._record_vision_fallback = lambda *args, **kwargs: None
    agent._remember = lambda *args, **kwargs: None
    agent._update_plan_file = lambda *args, **kwargs: None
    agent._db = None
    agent._on_progress = None
    agent._logger = None
    agent._step_artifacts = {}
    agent._risk_stats = {}
    agent._vision_fallback_stats = {}
    agent._last_recovery_error = ""
    agent._recovery_attempts = {}
    agent._resume_step_index = 0
    agent.state = SimpleNamespace(step_index=0, total_steps=0, current_action="")

    def fake_act(action_name, params):
        captured.update(params)
        return {"success": True}

    agent.act = fake_act

    result = agent.run_react_loop(
        [{"action": "fill_product_info", "params": {"product": {"title": "公牛插座"}}}],
    )

    assert result["success"] is True
    assert captured["_precheck_observation"]["status"] == "ok"
    assert captured["_precheck_screenshot"] == ""
