"""条件路由函数和 StateGraph 条件边测试。"""

from jm_ufo_agent.workflow.conditions import (
    can_save_draft,
    route_after_fill,
    route_after_assess,
    route_after_review,
    route_after_reflect,
    should_continue,
)
from jm_ufo_agent.workflow.state import GraphState, WorkflowStatus


def _make_state(**overrides) -> GraphState:
    """构建测试用 GraphState。"""
    defaults = dict(task_id="t1", row_index=0, product={"title": "测试"})
    defaults.update(overrides)
    return GraphState(**defaults)


class TestShouldContinue:
    def test_running_no_blockers(self):
        state = _make_state(status=WorkflowStatus.RUNNING)
        assert should_continue(state) is True

    def test_halted(self):
        state = _make_state(status=WorkflowStatus.HALTED)
        assert should_continue(state) is False

    def test_with_blockers(self):
        state = _make_state(status=WorkflowStatus.RUNNING, blockers=["bad"])
        assert should_continue(state) is False


class TestRouteAfterFill:
    def test_halted_goes_reflect(self):
        state = _make_state(status=WorkflowStatus.HALTED)
        assert route_after_fill(state) == "REFLECT_FAILURE"

    def test_blocked_goes_reflect(self):
        state = _make_state(status=WorkflowStatus.RUNNING, blockers=["x"])
        assert route_after_fill(state) == "REFLECT_FAILURE"

    def test_normal_goes_verify(self):
        state = _make_state(status=WorkflowStatus.RUNNING)
        assert route_after_fill(state) == "VERIFY_FIELD"


class TestRouteAfterAssess:
    def test_no_review_yet_goes_minimax(self):
        """完成度不足且未 review → 进 MINIMAX_REVIEW_SCORE 评审。"""
        state = _make_state(status=WorkflowStatus.RUNNING, completion_score=0.5)
        assert route_after_assess(state) == "MINIMAX_REVIEW_SCORE"

    def test_score_enough_review_save(self):
        state = _make_state(
            status=WorkflowStatus.RUNNING,
            completion_score=0.95,
            review_decision="save_draft",
        )
        assert route_after_assess(state) == "SAVE_DRAFT"

    def test_review_revise(self):
        state = _make_state(
            status=WorkflowStatus.RUNNING,
            completion_score=0.95,
            review_decision="revise",
        )
        assert route_after_assess(state) == "PLAN_FIELDS"

    def test_halted_goes_reflect(self):
        state = _make_state(status=WorkflowStatus.HALTED)
        assert route_after_assess(state) == "REFLECT_FAILURE"

    def test_score_enough_no_review_goes_minimax(self):
        """完成度足够但尚未 review → 进评审节点。"""
        state = _make_state(status=WorkflowStatus.RUNNING, completion_score=0.95)
        assert route_after_assess(state) == "MINIMAX_REVIEW_SCORE"


class TestRouteAfterReview:
    def test_save_draft(self):
        state = _make_state(review_decision="save_draft")
        assert route_after_review(state) == "SAVE_DRAFT"

    def test_revise(self):
        state = _make_state(review_decision="revise")
        assert route_after_review(state) == "PLAN_FIELDS"

    def test_halt(self):
        state = _make_state(review_decision="halt")
        assert route_after_review(state) == "REFLECT_FAILURE"

    def test_unknown_decision_goes_reflect(self):
        """未知 review_decision 应走 REFLECT_FAILURE 安全兜底。"""
        state = _make_state(review_decision="other")
        assert route_after_review(state) == "REFLECT_FAILURE"

    def test_empty_decision_goes_reflect(self):
        state = _make_state(review_decision="")
        assert route_after_review(state) == "REFLECT_FAILURE"


class TestRouteAfterReflect:
    def test_retry_within_limit(self):
        state = _make_state(evaluation_loop_count=2)
        assert route_after_reflect(state) == "RECOVER"

    def test_exceed_retry_limit(self):
        state = _make_state(evaluation_loop_count=5)
        assert route_after_reflect(state) == "HALT"

    def test_boundary_at_threshold(self):
        """恰好等于阈值 4 应返回 HALT。"""
        state = _make_state(evaluation_loop_count=4)
        assert route_after_reflect(state) == "HALT"

    def test_boundary_below_threshold(self):
        """恰好低于阈值 3 应返回 RECOVER。"""
        state = _make_state(evaluation_loop_count=3)
        assert route_after_reflect(state) == "RECOVER"


class TestStateGraphConditionalEdges:
    def test_graph_has_conditional_edges(self):
        """graph 应包含条件边而非纯线性。"""
        from jm_ufo_agent.workflow.graph import build_state_graph

        spec = build_state_graph()
        linear_edges = set(spec.edges)
        # FILL_FIELD→VERIFY_FIELD 不应再是线性边
        assert ("FILL_FIELD", "VERIFY_FIELD") not in linear_edges
        # REFLECT_FAILURE→RECOVER 也不应是线性边
        assert ("REFLECT_FAILURE", "RECOVER") not in linear_edges

    def test_graph_compiles(self):
        """条件路由图应能成功编译。"""
        from jm_ufo_agent.workflow.graph import build_state_graph

        spec = build_state_graph()
        if spec.graph is not None:
            compiled = spec.graph.compile()
            assert compiled is not None
