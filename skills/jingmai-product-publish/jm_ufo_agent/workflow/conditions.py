"""工作流路由条件。"""

from __future__ import annotations

from jm_ufo_agent.workflow.state import GraphState, WorkflowStatus


def should_continue(state: GraphState) -> bool:
    """判断工作流是否可以继续。"""

    # 只要状态已经 HALTED，就停止后续节点。
    # blockers 为空是继续的必要条件。
    # 该函数不修改 state，保证路由判断可重复。
    return state.status != WorkflowStatus.HALTED and not state.blockers


def can_save_draft(state: GraphState, threshold: float = 0.90) -> bool:
    """判断是否允许进入保存草稿。"""

    # 完成度必须达到阈值。
    # review_decision 必须明确允许 save_draft。
    # 存在任何 blocker 都不允许保存。
    return should_continue(state) and state.completion_score >= threshold and state.review_decision == "save_draft"


_MAX_RETRY_LOOPS = 4


def route_after_fill(state: GraphState) -> str:
    """FILL_FIELD 完成后路由：正常→VERIFY_FIELD，异常→REFLECT_FAILURE。"""

    # FILL_FIELD 之后必须走 VERIFY_FIELD 闭环验证。
    # 如果 fill 阶段已经 halt 或产生 blocker，直接跳反思。
    if not should_continue(state):
        return "REFLECT_FAILURE"
    return "VERIFY_FIELD"


def route_after_assess(state: GraphState) -> str:
    """ASSESS_FORM_COMPLETION 完成后路由。"""

    # halt 状态 → REFLECT_FAILURE。
    # 完成度不够且还没经过 review → 进 MINIMAX_REVIEW_SCORE 评审。
    # review 决定 revise → 回 PLAN_FIELDS 重做。
    # review 决定 save_draft → 进 SAVE_DRAFT。
    # 还没经过 review → 进 MINIMAX_REVIEW_SCORE（默认路径）。
    if not should_continue(state):
        return "REFLECT_FAILURE"
    if state.review_decision == "revise":
        return "PLAN_FIELDS"
    if can_save_draft(state):
        return "SAVE_DRAFT"
    # 默认：完成度足够但尚未 review，进入评审节点
    return "MINIMAX_REVIEW_SCORE"


def route_after_review(state: GraphState) -> str:
    """MINIMAX_REVIEW_SCORE 完成后路由。"""

    # review 决策决定走向：save_draft/revise/halt 三路分发。
    # halt 走 REFLECT_FAILURE 而非直接 HALT，保留反思证据。
    mapping = {"save_draft": "SAVE_DRAFT", "revise": "PLAN_FIELDS", "halt": "REFLECT_FAILURE"}
    return mapping.get(state.review_decision, "REFLECT_FAILURE")


def route_after_reflect(state: GraphState) -> str:
    """REFLECT_FAILURE 完成后路由：重试→RECOVER，超限→HALT。"""

    # evaluation_loop_count 由 minimax_review_score_node 维护。
    # 超过最大重试次数后，不再循环，直接 HALT。
    if state.evaluation_loop_count >= _MAX_RETRY_LOOPS:
        return "HALT"
    return "RECOVER"
