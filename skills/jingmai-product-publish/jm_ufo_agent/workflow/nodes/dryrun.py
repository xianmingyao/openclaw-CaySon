"""dry-run 工作流节点。"""

from __future__ import annotations

from jm_ufo_agent.agents.base import AgentContext
from jm_ufo_agent.agents.image_transform import ImageTransformAgent
from jm_ufo_agent.strategies.action import GuardedActionStrategy
from jm_ufo_agent.strategies.completion import FormCompletionScoreStrategy
from jm_ufo_agent.strategies.observe import ObserveStrategy
from jm_ufo_agent.strategies.plan import DeterministicPlanStrategy, FieldPlan
from jm_ufo_agent.strategies.review_score import MiniMaxReviewScoreStrategy
from jm_ufo_agent.strategies.verify import VerifyStrategy
from jm_ufo_agent.runtime.evidence import draft_verification_from_save_evidence
from jm_ufo_agent.workflow.state import GraphState, WorkflowStatus


async def bootstrap_node(state: GraphState) -> list[str]:
    """初始化工作流状态。"""

    # BOOTSTRAP 是所有 dry-run 的入口。
    # 状态从 pending 切到 running，表示本轮执行已开始。
    # 返回节点日志，便于 CLI 展示。
    state.current_node = "BOOTSTRAP"
    state.status = WorkflowStatus.RUNNING
    state.add_evidence("bootstrap", {"workflow": "dry-run", "row_index": state.row_index})
    return ["BOOTSTRAP"]


async def observe_page_node(state: GraphState, strategy: ObserveStrategy) -> list[str]:
    """观察页面节点。"""

    # OBSERVE_PAGE 只写观察证据。
    # 观察失败时写入 blocker，由外层 workflow 停止。
    # 不在这里推断字段完成。
    state.current_node = "OBSERVE_PAGE"
    observation = await strategy.observe()
    state.add_evidence("observe_page", observation)
    if not observation["ok"]:
        state.halt(observation["message"])
    return ["OBSERVE_PAGE"]


async def prepare_assets_node(state: GraphState, image_transform: ImageTransformAgent | None = None) -> list[str]:
    """准备图片资产并执行本地可测的 VLM 失败边界。"""

    # PREPARE_ASSETS 放在打开/填写页面之前，避免进入 GUI 后才发现图片不可用。
    # 默认 ImageTransformAgent 是 dry-run，不会触发真实 VLM 或外部网络。
    # 注入会失败的 handler 时，这里会按三次重试规则 halt 当前 row。
    state.current_node = "PREPARE_ASSETS"
    agent = image_transform or ImageTransformAgent()
    context = AgentContext(task_id=state.task_id, row_index=state.row_index, product=state.product, evidence=state.evidence)
    result = await agent.transform_with_retry(context)
    state.add_evidence("prepare_assets", {"ok": result.ok, "message": result.message, **result.data})
    if not result.ok:
        state.halt(result.message, result.data)
    return ["PREPARE_ASSETS"]


async def noop_node(state: GraphState, node_name: str, evidence_key: str | None = None) -> list[str]:
    """记录尚未接入真实 backend 的显式节点。"""

    # 这个节点用于把设计文档里的 18 个节点先落成可观测的状态机节点。
    # 当前不会执行真实京麦窗口、真实截图或外部账号动作。
    # 后续接入 UFO/UIA/Win32 时，可以逐个文件替换这里的 noop 行为。
    state.current_node = node_name
    state.add_evidence(evidence_key or node_name.lower(), {"ok": True, "mode": "local-safe-noop"})
    return [node_name]


async def plan_fields_node(state: GraphState, strategy: DeterministicPlanStrategy) -> list[FieldPlan]:
    """字段计划节点。"""

    # PLAN_FIELDS 根据商品数据和已验证字段生成计划。
    # 已验证字段来自 state，可支持字段级断点恢复。
    # 计划本身也写入 evidence，便于排查字段顺序。
    state.current_node = "PLAN_FIELDS"
    plans = strategy.build_field_plan(state.product, state.verified_fields)
    state.add_evidence("field_plan", [plan.field_name for plan in plans])
    return plans


async def fill_fields_node(state: GraphState, plans: list[FieldPlan], action: GuardedActionStrategy, verify: VerifyStrategy) -> list[str]:
    """填充并验证字段节点。"""

    # 每个字段都先执行动作，再做验证。
    # action 成功不等于字段成功，必须看 VerifyStrategy 结果。
    # 任一必填字段验证失败会 halt 当前 row。
    state.current_node = "FILL_AND_VERIFY_FIELDS"
    completed: list[str] = []
    for plan in plans:
        action_result = await action.fill_field(plan, evidence={"row_index": state.row_index})
        state.add_evidence(f"{plan.field_name}_action", action_result.data)
        verify_result = verify.verify_field(plan, evidence={"action_ok": action_result.ok})
        state.add_evidence(f"{plan.field_name}_verify", {"ok": verify_result.ok, "reason": verify_result.reason})
        if not verify_result.ok:
            state.halt(f"{plan.field_name}: {verify_result.reason}")
            break
        state.verify_field(plan.field_name)
        completed.append(plan.field_name)
    return completed


async def assess_form_completion_node(state: GraphState, strategy: FormCompletionScoreStrategy) -> float:
    """表单完成度评分节点。"""

    # 完成度由必填字段和 verified_fields 计算。
    # blockers 存在时即使分数够高也不允许通过。
    # 分数写入 state，供评审节点和 CLI 使用。
    state.current_node = "ASSESS_FORM_COMPLETION"
    required_fields = list(DeterministicPlanStrategy.default_fields)
    score, passed = strategy.score(required_fields, state.verified_fields, state.blockers)
    state.completion_score = score
    state.add_evidence("completion", {"score": score, "passed": passed})
    if not passed:
        state.halt("表单完成度未达到保存草稿阈值")
    return score


async def minimax_review_score_node(state: GraphState, strategy: MiniMaxReviewScoreStrategy) -> str:
    """MiniMax 评审决策节点。"""

    # 默认仍是本地确定性决策；注入 MiniMax client 时才会触发外部评审。
    # 真实 API 返回也必须映射为 revise/save_draft/halt 三类决策。
    # halt 决策会写 blocker，阻止保存草稿。
    state.current_node = "MINIMAX_REVIEW_SCORE"
    score = await strategy.decide_async(state.completion_score, state.blockers, state.evaluation_loop_count, state.to_dict())
    state.review_decision = score.decision
    state.add_evidence(
        "review_score",
        {
            "decision": score.decision,
            "overall_score": score.overall_score,
            "blocking_gaps": score.blocking_gaps,
            "recommendations": score.recommendations,
        },
    )
    if score.decision == "revise":
        state.evaluation_loop_count += 1
    if score.decision == "halt":
        state.halt(";".join(score.blocking_gaps) or "评审器要求中止")
    return score.decision


async def save_draft_node(state: GraphState, action: GuardedActionStrategy) -> bool:
    """保存草稿节点。"""

    # 该节点只调用保存草稿，不包含发布路径。
    # SafetyPolicy 会再次校验动作 label。
    # 动作结果写入 evidence，后续 VERIFY_DRAFT 使用。
    state.current_node = "SAVE_DRAFT"
    result = await action.save_draft(evidence={"completion_score": state.completion_score})
    state.add_evidence("save_draft", {"ok": result.ok, "message": result.message})
    if not result.ok:
        state.halt(result.message)
    return result.ok


async def verify_draft_node(state: GraphState, verify: VerifyStrategy) -> bool:
    """验证草稿节点。"""

    # dry-run 用 save_draft evidence 作为保存证据。
    # 真实实现应替换为列表页/草稿 ID/页面提示验证。
    # 验证通过后才把状态置为 SAVED_DRAFT。
    state.current_node = "VERIFY_DRAFT"
    draft_snapshot = draft_verification_from_save_evidence(state.evidence.get("save_draft"))
    result = verify.verify_draft_saved(draft_snapshot.to_dict())
    state.add_evidence("verify_draft", {**draft_snapshot.to_dict(), "strategy_reason": result.reason})
    if not result.ok:
        state.halt(result.reason, draft_snapshot.to_dict())
        return False
    state.status = WorkflowStatus.SAVED_DRAFT
    return True
