# tests/test_v2_integration_closure.py
"""最后一公里集成验证 — DesktopAgent+UfoBackend + RowDispatcher+ConditionalRouting。"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from jm_ufo_agent.agents.desktop import DesktopAgent
from jm_ufo_agent.agents.base import AgentResult
from jm_ufo_agent.backends.ufo_backend import UfoDesktopBackend
from jm_ufo_agent.runtime.dispatcher import RowDispatcher, RowResult
from jm_ufo_agent.safety.policy import SafetyPolicy, SafetyViolation


class TestDesktopAgentWithUfoBackend:
    """DesktopAgent 注入 UfoDesktopBackend 后的委托行为。"""

    @pytest.mark.asyncio
    async def test_agent_uses_ufo_backend(self):
        """DesktopAgent click 应通过 UfoDesktopBackend 执行并返回 AgentResult。"""
        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        # 跳过 _ensure_loaded，直接注入 mock controller
        mock_controller = MagicMock()
        mock_controller.click = MagicMock(return_value=True)
        backend._controller = mock_controller

        agent = DesktopAgent(name="test_agent", backend=backend)
        result = await agent.click(target="价格输入框", label="点击价格")
        assert isinstance(result, AgentResult)
        assert result.ok is True
        assert result.data["action"] == "click"

    @pytest.mark.asyncio
    async def test_agent_fill_through_ufo(self):
        """DesktopAgent fill 命令应通过 UfoDesktopBackend 执行。"""
        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        mock_controller = MagicMock()
        mock_controller.set_text = MagicMock(return_value=True)
        backend._controller = mock_controller

        agent = DesktopAgent(name="test_agent", backend=backend)
        result = await agent.fill(target="标题", value="测试商品", label="填写标题")
        assert isinstance(result, AgentResult)
        assert result.ok is True
        assert result.data["action"] == "fill"

    @pytest.mark.asyncio
    async def test_agent_submit_blocked_by_safety(self):
        """包含发布关键字的 submit 应被 SafetyPolicy 拦截并抛出 SafetyViolation。"""
        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        mock_controller = MagicMock()
        mock_controller.click = MagicMock(return_value=True)
        backend._controller = mock_controller

        agent = DesktopAgent(name="test_agent", backend=backend)
        # "发布商品" target 包含 blocked keyword "发布"，应触发 SafetyViolation
        with pytest.raises(SafetyViolation):
            await agent.submit(target="发布商品", label="发布")

    @pytest.mark.asyncio
    async def test_agent_submit_draft_allowed(self):
        """保存草稿类 submit 应通过 SafetyPolicy 校验。"""
        backend = UfoDesktopBackend(ufo_root=Path("/fake/ufo"))
        mock_controller = MagicMock()
        mock_controller.click = MagicMock(return_value=True)
        backend._controller = mock_controller

        agent = DesktopAgent(name="test_agent", backend=backend)
        result = await agent.submit(target="保存草稿按钮", label="保存草稿")
        assert isinstance(result, AgentResult)
        assert result.ok is True


class TestRowDispatcherWithWorkflow:
    """RowDispatcher 与 workflow handler 的集成。"""

    @pytest.mark.asyncio
    async def test_dispatcher_runs_rows_through_handler(self):
        """RowDispatcher 应能为每行调用 handler 并返回排序后的结果。"""
        call_log: list[int] = []

        async def row_handler(index: int, data: dict) -> RowResult:
            call_log.append(index)
            return RowResult(row_index=index, ok=True, message="完成")

        dispatcher = RowDispatcher(max_concurrency=2)
        rows = [{"title": f"商品{i}"} for i in range(4)]
        results = await dispatcher.dispatch(rows=rows, handler=row_handler)

        assert len(results) == 4
        assert all(r.ok for r in results)
        # 结果按 row_index 排序
        assert [r.row_index for r in results] == [0, 1, 2, 3]
        # handler 被每行都调用了
        assert sorted(call_log) == [0, 1, 2, 3]

    @pytest.mark.asyncio
    async def test_dispatcher_isolates_row_failures(self):
        """单行失败不影响其他行的执行。"""
        async def row_handler(index: int, data: dict) -> RowResult:
            if index == 1:
                raise ValueError("模拟第2行异常")
            return RowResult(row_index=index, ok=True, message="完成")

        dispatcher = RowDispatcher(max_concurrency=2)
        rows = [{"title": f"商品{i}"} for i in range(3)]
        results = await dispatcher.dispatch(rows=rows, handler=row_handler)

        assert len(results) == 3
        # 第2行（index=1）失败，其他行成功
        assert results[0].ok is True
        assert results[1].ok is False
        assert "模拟第2行异常" in results[1].error
        assert results[2].ok is True

    @pytest.mark.asyncio
    async def test_dispatcher_empty_rows(self):
        """空行列表应返回空结果。"""
        async def row_handler(index: int, data: dict) -> RowResult:
            return RowResult(row_index=index, ok=True)

        dispatcher = RowDispatcher()
        results = await dispatcher.dispatch(rows=[], handler=row_handler)
        assert results == []


class TestConditionalRoutingIntegration:
    """条件路由函数在各种状态下的路由行为。"""

    def test_route_after_fill_halted_to_reflect(self):
        """HALTED 状态应路由到 REFLECT_FAILURE。"""
        from jm_ufo_agent.workflow.conditions import route_after_fill
        from jm_ufo_agent.workflow.state import GraphState, WorkflowStatus

        state = GraphState(
            task_id="t1", row_index=0, product={}, status=WorkflowStatus.HALTED,
        )
        assert route_after_fill(state) == "REFLECT_FAILURE"

    def test_route_after_fill_running_to_verify(self):
        """RUNNING 状态应路由到 VERIFY_FIELD。"""
        from jm_ufo_agent.workflow.conditions import route_after_fill
        from jm_ufo_agent.workflow.state import GraphState, WorkflowStatus

        state = GraphState(
            task_id="t1", row_index=0, product={}, status=WorkflowStatus.RUNNING,
        )
        assert route_after_fill(state) == "VERIFY_FIELD"

    def test_route_after_fill_with_blockers_to_reflect(self):
        """存在 blockers 时应路由到 REFLECT_FAILURE。"""
        from jm_ufo_agent.workflow.conditions import route_after_fill
        from jm_ufo_agent.workflow.state import GraphState, WorkflowStatus

        state = GraphState(
            task_id="t1", row_index=0, product={},
            status=WorkflowStatus.RUNNING, blockers=["字段校验失败"],
        )
        assert route_after_fill(state) == "REFLECT_FAILURE"

    def test_reflect_recover_loop_under_max(self):
        """evaluation_loop_count < _MAX_RETRY_LOOPS 应路由到 RECOVER。"""
        from jm_ufo_agent.workflow.conditions import route_after_reflect
        from jm_ufo_agent.workflow.state import GraphState

        state = GraphState(task_id="t1", row_index=0, product={}, evaluation_loop_count=2)
        assert route_after_reflect(state) == "RECOVER"

    def test_reflect_recover_loop_at_max(self):
        """evaluation_loop_count >= _MAX_RETRY_LOOPS 应路由到 HALT。"""
        from jm_ufo_agent.workflow.conditions import route_after_reflect
        from jm_ufo_agent.workflow.state import GraphState

        # _MAX_RETRY_LOOPS = 4，所以 count=4 时应 HALT
        state = GraphState(task_id="t1", row_index=0, product={}, evaluation_loop_count=4)
        assert route_after_reflect(state) == "HALT"

    def test_reflect_halt_after_exceeding_max_retries(self):
        """evaluation_loop_count 远超最大重试次数也应路由到 HALT。"""
        from jm_ufo_agent.workflow.conditions import route_after_reflect
        from jm_ufo_agent.workflow.state import GraphState

        state = GraphState(task_id="t1", row_index=0, product={}, evaluation_loop_count=5)
        assert route_after_reflect(state) == "HALT"

    def test_route_after_review_save_draft(self):
        """review_decision=save_draft 应路由到 SAVE_DRAFT。"""
        from jm_ufo_agent.workflow.conditions import route_after_review
        from jm_ufo_agent.workflow.state import GraphState

        state = GraphState(task_id="t1", row_index=0, product={}, review_decision="save_draft")
        assert route_after_review(state) == "SAVE_DRAFT"

    def test_route_after_review_revise(self):
        """review_decision=revise 应路由到 PLAN_FIELDS。"""
        from jm_ufo_agent.workflow.conditions import route_after_review
        from jm_ufo_agent.workflow.state import GraphState

        state = GraphState(task_id="t1", row_index=0, product={}, review_decision="revise")
        assert route_after_review(state) == "PLAN_FIELDS"
