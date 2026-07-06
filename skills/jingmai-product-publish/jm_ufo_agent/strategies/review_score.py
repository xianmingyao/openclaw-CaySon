"""MiniMax 评审评分策略接口。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from jm_ufo_agent.integrations.minimax_review import MiniMaxReviewClient, ReviewRubricItem


@dataclass(frozen=True)
class ReviewScore:
    """需求覆盖评审结果。"""

    decision: str
    overall_score: int
    blocking_gaps: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class MiniMaxReviewScoreStrategy:
    """MiniMax-M3 评审循环的本地可测试边界。"""

    def __init__(self, max_loop_steps: int = 3, client: MiniMaxReviewClient | None = None):
        """初始化评审循环上限。"""

        # client 为空时走本地确定性策略，保证 dry-run 和 CI 不访问外网。
        # client 存在时才执行 /models preflight 和 chat scoring。
        # max_loop_steps 防止评审循环无限返回 revise。
        self.max_loop_steps = max_loop_steps
        self.client = client

    def decide(self, completion_score: float, blockers: list[str] | None = None, loop_step: int = 0) -> ReviewScore:
        """根据完成度和阻断项生成评审决策。

        # 有阻断项时直接 halt，不能让评审器掩盖安全/证据问题。
        # 完成度不足且仍有循环次数时返回 revise。
        # 完成度达标时允许进入 save_draft。
        """

        current_blockers = blockers or []
        if current_blockers:
            return ReviewScore(decision="halt", overall_score=0, blocking_gaps=current_blockers)
        if completion_score < 0.90 and loop_step < self.max_loop_steps:
            return ReviewScore(decision="revise", overall_score=int(completion_score * 100), recommendations=["继续补齐未验证字段"])
        if completion_score < 0.90:
            return ReviewScore(decision="halt", overall_score=int(completion_score * 100), blocking_gaps=["完成度低于阈值且循环次数耗尽"])
        return ReviewScore(decision="save_draft", overall_score=int(completion_score * 100))

    async def decide_async(
        self,
        completion_score: float,
        blockers: list[str] | None = None,
        loop_step: int = 0,
        state_payload: dict[str, Any] | None = None,
    ) -> ReviewScore:
        """异步评审入口，可接真实 MiniMax client。"""

        # 没有注入 client 时保持原来的本地确定性行为。
        # 注入 client 后先做 preflight，模型不可用则返回 halt。
        # MiniMax 只能收窄风险，不能覆盖确定性完成度和 blocker。
        if self.client is None:
            return self.decide(completion_score, blockers, loop_step)
        if blockers:
            return ReviewScore(decision="halt", overall_score=0, blocking_gaps=blockers)
        try:
            available = await self.client.preflight()
            if not available:
                return ReviewScore(decision="halt", overall_score=0, blocking_gaps=["review_scorer_unavailable"])
            parsed = await self.client.score(
                spec_markdown="jm_ufo_agent runtime state review",
                rubric=[
                    ReviewRubricItem(item="完成度闸门", evidence=["ASSESS_FORM_COMPLETION"]),
                    ReviewRubricItem(item="安全策略", evidence=["SafetyPolicy"]),
                    ReviewRubricItem(item="草稿保存证据", evidence=["SAVE_DRAFT"]),
                ],
            )
        except Exception as exc:
            return ReviewScore(decision="halt", overall_score=0, blocking_gaps=[f"review_scorer_unavailable:{exc.__class__.__name__}"])
        if parsed.blocking_gaps:
            return ReviewScore(decision="halt", overall_score=parsed.overall_score, blocking_gaps=parsed.blocking_gaps, recommendations=parsed.recommendations)
        if completion_score < 0.90 and loop_step < self.max_loop_steps:
            return ReviewScore(decision="revise", overall_score=parsed.overall_score, recommendations=parsed.recommendations or ["继续补齐未验证字段"])
        if parsed.overall_score >= 90 and completion_score >= 0.90:
            return ReviewScore(decision="save_draft", overall_score=parsed.overall_score, recommendations=parsed.recommendations)
        return ReviewScore(decision="halt", overall_score=parsed.overall_score, blocking_gaps=["review_score_below_threshold"], recommendations=parsed.recommendations)
