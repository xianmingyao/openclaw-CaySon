from jm_ufo_agent.strategies.completion import FormCompletionScoreStrategy
from jm_ufo_agent.strategies.plan import DeterministicPlanStrategy
from jm_ufo_agent.strategies.review_score import MiniMaxReviewScoreStrategy
from jm_ufo_agent.strategies.verify import VerifyStrategy


def test_plan_strategy_skips_verified_fields():
    strategy = DeterministicPlanStrategy()

    plans = strategy.build_field_plan({"title": "测试", "brand": "品牌"}, verified_fields={"title"})

    assert [plan.field_name for plan in plans][0] == "category"
    assert "title" not in {plan.field_name for plan in plans}
    assert len(strategy.default_fields) == 12


def test_verify_strategy_rejects_empty_required_field():
    strategy = VerifyStrategy()
    plan = DeterministicPlanStrategy().build_field_plan({"title": ""})[0]

    result = strategy.verify_field(plan)

    assert result.ok is False
    assert result.reason == "必填字段为空"


def test_completion_strategy_requires_threshold_and_no_blockers():
    strategy = FormCompletionScoreStrategy(threshold=0.9)

    score, passed = strategy.score(["a", "b"], {"a", "b"}, blockers=[])
    blocked_score, blocked_passed = strategy.score(["a", "b"], {"a", "b"}, blockers=["页面不一致"])

    assert score == 1.0
    assert passed is True
    assert blocked_score == 1.0
    assert blocked_passed is False


def test_minimax_review_score_strategy_is_deterministic_boundary():
    strategy = MiniMaxReviewScoreStrategy(max_loop_steps=1)

    assert strategy.decide(1.0).decision == "save_draft"
    assert strategy.decide(0.5, loop_step=0).decision == "revise"
    assert strategy.decide(0.5, loop_step=1).decision == "halt"
    assert strategy.decide(1.0, blockers=["安全阻断"]).decision == "halt"
