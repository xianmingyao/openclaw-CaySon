"""dry-run 工作流编排与 StateGraph 规格。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from jm_ufo_agent.agents.image_transform import ImageTransformAgent
from jm_ufo_agent.storage.repositories.models import FieldProgressRecord, RowExecutionRecord
from jm_ufo_agent.strategies.action import GuardedActionStrategy
from jm_ufo_agent.strategies.completion import FormCompletionScoreStrategy
from jm_ufo_agent.strategies.observe import ObserveStrategy
from jm_ufo_agent.strategies.plan import DeterministicPlanStrategy
from jm_ufo_agent.strategies.review_score import MiniMaxReviewScoreStrategy
from jm_ufo_agent.strategies.verify import VerifyStrategy
from jm_ufo_agent.workflow.conditions import can_save_draft, should_continue
from jm_ufo_agent.workflow.nodes import (
    assess_form_completion_node,
    bootstrap_node,
    fill_fields_node,
    minimax_review_score_node,
    observe_page_node,
    plan_fields_node,
    prepare_assets_node,
    save_draft_node,
    verify_draft_node,
)
from jm_ufo_agent.workflow.state import GraphState

if TYPE_CHECKING:
    from jm_ufo_agent.storage.checkpointer import AsyncMySQLSaver
    from jm_ufo_agent.storage.repositories.field_progress import FieldProgressRepository
    from jm_ufo_agent.storage.repositories.rows import RowExecutionRepository


class DryRunWorkflow:
    """无外部依赖的确定性工作流。"""

    def __init__(
        self,
        observe: ObserveStrategy | None = None,
        plan: DeterministicPlanStrategy | None = None,
        action: GuardedActionStrategy | None = None,
        verify: VerifyStrategy | None = None,
        completion: FormCompletionScoreStrategy | None = None,
        review: MiniMaxReviewScoreStrategy | None = None,
        image_transform: ImageTransformAgent | None = None,
        saver: "AsyncMySQLSaver | None" = None,
        field_progress: "FieldProgressRepository | None" = None,
        row_progress: "RowExecutionRepository | None" = None,
    ):
        """初始化工作流依赖。"""

        # 所有策略都可注入，便于测试和后续替换真实实现。
        # 默认策略都是 dry-run，不访问外部账号或真实桌面。
        # 该类保留可运行闭环，build_state_graph 负责暴露 LangGraph 节点规格。
        self.observe = observe or ObserveStrategy()
        self.plan = plan or DeterministicPlanStrategy()
        self.action = action or GuardedActionStrategy()
        self.verify = verify or VerifyStrategy()
        self.completion = completion or FormCompletionScoreStrategy()
        self.review = review or MiniMaxReviewScoreStrategy()
        self.image_transform = image_transform or ImageTransformAgent()
        self.saver = saver
        self.field_progress = field_progress
        self.row_progress = row_progress

    async def run(self, state: GraphState) -> GraphState:
        """运行完整 dry-run 工作流。"""

        # 节点之间只通过 GraphState 传递证据和状态。
        # 每个条件判断都在节点后执行，失败立即停止。
        # 保存草稿前必须通过完成度和评审决策双闸门。
        await bootstrap_node(state)
        await self._checkpoint(state)
        await self._select_row(state)
        await self._recover_verified_fields(state)
        await self._mark_row(state, "in_progress")
        await self._checkpoint(state)
        await prepare_assets_node(state, self.image_transform)
        await self._checkpoint(state)
        if not should_continue(state):
            await self._mark_row(state, "halted")
            return state
        await observe_page_node(state, self.observe)
        await self._checkpoint(state)
        if not should_continue(state):
            await self._mark_row(state, "halted")
            return state
        plans = await plan_fields_node(state, self.plan)
        await self._checkpoint(state)
        completed_fields = await fill_fields_node(state, plans, self.action, self.verify)
        await self._mark_verified_fields(state, completed_fields)
        await self._checkpoint(state)
        if not should_continue(state):
            await self._mark_row(state, "halted")
            return state
        await assess_form_completion_node(state, self.completion)
        await self._checkpoint(state)
        if not should_continue(state):
            await self._mark_row(state, "halted")
            return state
        await minimax_review_score_node(state, self.review)
        await self._checkpoint(state)
        if not can_save_draft(state, self.completion.threshold):
            await self._mark_row(state, "halted")
            return state
        await save_draft_node(state, self.action)
        await self._checkpoint(state)
        if not should_continue(state):
            await self._mark_row(state, "halted")
            return state
        await verify_draft_node(state, self.verify)
        await self._mark_row(state, "committed")
        state.add_evidence("commit_row", {"row_index": state.row_index, "status": "committed"})
        await self._checkpoint(state)
        return state

    async def _select_row(self, state: GraphState) -> None:
        """执行本地可测的 SELECT_ROW 恢复规则。"""

        # 当前只实现 row5-row7 草稿证据齐全后跳到 row82 的规则。
        # 没有 row_progress 时保持调用方传入的 row_index，兼容纯 dry-run。
        # 真实批量调度后续可以在这里扩展为“查找下一条 pending row”。
        state.current_node = "SELECT_ROW"
        if self.row_progress is None:
            state.add_evidence("select_row", {"requested_row": state.row_index, "selected_row": state.row_index})
            return
        requested = state.row_index
        selected = await self.row_progress.next_row_after_seed(state.task_id, requested)
        state.row_index = selected
        state.add_evidence("select_row", {"requested_row": requested, "selected_row": selected})

    async def _recover_verified_fields(self, state: GraphState) -> None:
        """从字段进度表恢复 verified 字段。"""

        # 字段级恢复发生在 PLAN_FIELDS 前，确保已验证字段不会重复填。
        # 只读取 status=verified 的字段，pending/filling/failed 都不会被跳过。
        # 没有仓库时记录空恢复证据，保持纯 dry-run 可重复。
        state.current_node = "RECOVER"
        if self.field_progress is None:
            state.add_evidence("recover_fields", {"verified_fields": []})
            return
        fields = await self.field_progress.list_verified_fields(state.task_id, state.row_index)
        state.restore_verified_fields(fields)
        state.add_evidence("recover_fields", {"verified_fields": sorted(fields)})

    async def _mark_verified_fields(self, state: GraphState, field_names: list[str]) -> None:
        """把本轮验证通过的字段写入字段进度表。"""

        # 该方法只写本轮新完成的字段，恢复时已有字段不会重复写。
        # 每个字段都带上对应 action/verify 证据，方便人工定位失败点。
        # 没有字段仓库时直接返回，保持 dry-run 不依赖数据库。
        if self.field_progress is None:
            return
        for field_name in field_names:
            await self.field_progress.mark(
                FieldProgressRecord(
                    task_id=state.task_id,
                    row_index=state.row_index,
                    field_name=field_name,
                    status="verified",
                    evidence={
                        "action": state.evidence.get(f"{field_name}_action", {}),
                        "verify": state.evidence.get(f"{field_name}_verify", {}),
                    },
                )
            )

    async def _mark_row(self, state: GraphState, status: str) -> None:
        """把当前行状态写入行级进度表。"""

        # 行级进度用于崩溃恢复和 committed row 不重做。
        # draft_evidence 只在 save/verify 后存在，row82 规则会检查该证据。
        # 没有 row_progress 时直接返回，避免 dry-run 连接数据库。
        if self.row_progress is None:
            return
        completion = state.evidence.get("completion", {})
        review = state.evidence.get("review_score", {})
        draft_evidence = {
            "save_draft": state.evidence.get("save_draft"),
            "verify_draft": state.evidence.get("verify_draft"),
        }
        await self.row_progress.upsert(
            RowExecutionRecord(
                task_id=state.task_id,
                row_index=state.row_index,
                status=status,
                current_field=None,
                last_error=";".join(state.blockers) if state.blockers else None,
                page_signature=state.evidence.get("observe_page", {}).get("signature") if isinstance(state.evidence.get("observe_page"), dict) else None,
                completion_score=state.completion_score,
                completion_passed=bool(completion.get("passed")) if isinstance(completion, dict) else False,
                completion_details=completion if isinstance(completion, dict) else {},
                evaluation_loop_count=state.evaluation_loop_count,
                review_score=float(review.get("overall_score") or 0.0) if isinstance(review, dict) else 0.0,
                review_decision=state.review_decision,
                review_details=review if isinstance(review, dict) else {},
                draft_evidence={key: value for key, value in draft_evidence.items() if value},
            )
        )

    async def _checkpoint(self, state: GraphState) -> None:
        """按需保存 checkpoint。"""

        # saver 为空时保持纯内存 dry-run，适合无数据库测试。
        # saver 存在时每个关键节点后保存一次状态。
        # 持久化失败不吞掉，让调用方知道 checkpoint 写入失败。
        if self.saver is not None:
            await self.saver.aput(state)


@dataclass(frozen=True)
class LocalStateGraphSpec:
    """无 langgraph 依赖时的本地状态机规格。"""

    node_order: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    graph: Any | None = None

    def has_node(self, node_name: str) -> bool:
        """判断节点是否已经注册。"""

        # 测试和 CLI 可以用这个方法验证节点覆盖度。
        # 该方法不执行节点，只检查状态机定义是否完整。
        # 使用 tuple 保持节点顺序稳定，便于 diff 和文档核对。
        return node_name in self.node_order


def build_state_graph() -> LocalStateGraphSpec:
    """构建 v2 设计要求的 18 节点 StateGraph 规格（含条件路由）。"""

    node_order = (
        "BOOTSTRAP",
        "RECOVER",
        "SELECT_ROW",
        "PREPARE_ASSETS",
        "OPEN_PAGE",
        "OBSERVE_PAGE",
        "ASSERT_PAGE_SIGNATURE",
        "CALIBRATE_LOCATORS",
        "PLAN_FIELDS",
        "FILL_FIELD",
        "VERIFY_FIELD",
        "ASSESS_FORM_COMPLETION",
        "MINIMAX_REVIEW_SCORE",
        "SAVE_DRAFT",
        "VERIFY_DRAFT",
        "COMMIT_ROW",
        "REFLECT_FAILURE",
        "HALT",
    )

    # 线性边：只保留无条件推进的顺序连接
    linear_edges = (
        ("BOOTSTRAP", "RECOVER"),
        ("RECOVER", "SELECT_ROW"),
        ("SELECT_ROW", "PREPARE_ASSETS"),
        ("PREPARE_ASSETS", "OPEN_PAGE"),
        ("OPEN_PAGE", "OBSERVE_PAGE"),
        ("OBSERVE_PAGE", "ASSERT_PAGE_SIGNATURE"),
        ("ASSERT_PAGE_SIGNATURE", "CALIBRATE_LOCATORS"),
        ("CALIBRATE_LOCATORS", "PLAN_FIELDS"),
        ("PLAN_FIELDS", "FILL_FIELD"),
        # FILL_FIELD → 条件路由 (route_after_fill)
        ("VERIFY_FIELD", "ASSESS_FORM_COMPLETION"),
        # ASSESS_FORM_COMPLETION → 条件路由 (route_after_assess)
        # MINIMAX_REVIEW_SCORE → 条件路由 (route_after_review)
        ("SAVE_DRAFT", "VERIFY_DRAFT"),
        ("VERIFY_DRAFT", "COMMIT_ROW"),
        ("COMMIT_ROW", "HALT"),
        # REFLECT_FAILURE → 条件路由 (route_after_reflect)
    )

    from jm_ufo_agent.workflow.conditions import (
        route_after_assess,
        route_after_fill,
        route_after_reflect,
        route_after_review,
    )

    edges = linear_edges

    try:
        from langgraph.graph import StateGraph  # type: ignore
    except Exception:
        return LocalStateGraphSpec(node_order=node_order, edges=edges)

    graph = StateGraph(dict)
    for node_name in node_order:
        # 真实节点执行仍由 DryRunWorkflow 承担；这里先注册稳定节点名。
        # lambda 使用默认参数绑定节点名，避免闭包拿到最后一个节点。
        # 返回 state 本体，保证该规格图可被 compile 阶段接受。
        graph.add_node(node_name, lambda state, _node_name=node_name: state)
    graph.set_entry_point("BOOTSTRAP")

    for start, end in linear_edges:
        graph.add_edge(start, end)

    # 条件边
    graph.add_conditional_edges("FILL_FIELD", route_after_fill)
    graph.add_conditional_edges("ASSESS_FORM_COMPLETION", route_after_assess)
    graph.add_conditional_edges("MINIMAX_REVIEW_SCORE", route_after_review)
    graph.add_conditional_edges("REFLECT_FAILURE", route_after_reflect)

    graph.set_finish_point("HALT")
    return LocalStateGraphSpec(node_order=node_order, edges=edges, graph=graph)
