"""Minimal runtime kernel: Session + TaskRunner (delegated to AgentPipeline).

BL-091: 用 AgentPipeline 替代硬编码 if/elif 调度链。
保留 RunnerSession、run() 签名、_build_debug_output()。
删除 ~300 行 _build_plan/_execute_step/_execute_with_retry/_run_t5_*。
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from jingmai_publish.agent import REGISTRY, AgentExecutor, AgentPipeline, AgentReflection

# 重新导出 RunnerSession，保持外部引用兼容
__all__ = ["RunnerSession", "TaskRunner"]


@dataclass(slots=True)
class RunnerSession:
    """Minimum session state for a runtime execution."""

    requested_step: str
    session_id: str = field(default_factory=lambda: f"runner-{uuid.uuid4().hex[:12]}")
    window_handle: str | None = None
    page_state: str | None = None
    completed_steps: list[str] = field(default_factory=list)
    trace: list[dict[str, object]] = field(default_factory=list)
    halted: bool = False
    last_message: str | None = None
    max_retry_count: int = 3
    # BL-086B: 跨步骤 before/after 截图路径，用于视觉对比
    last_screenshot: str | None = None
    screenshot_before: str | None = None
    screenshot_after: str | None = None


class TaskRunner:
    """Drive the observe → decide → act → verify loop via AgentPipeline.

    BL-091: 所有步骤调度委托给 AgentPipeline (Planner → Executor → Reflection)。
    TaskRunner 只负责：参数验证、session 创建、debug 输出、结果格式化。
    """

    def __init__(self, workflow_service, *, event_loop=None, vision_provider=None) -> None:
        self.workflow_service = workflow_service
        self._executor = AgentExecutor(workflow_service, event_loop=event_loop)
        self._reflection = AgentReflection(event_loop=event_loop)
        self._pipeline = AgentPipeline(
            REGISTRY, self._executor, self._reflection,
            vision_provider=vision_provider,
        )

    def run(self, step: str = "both", debug: bool = False, **kwargs) -> dict[str, object]:
        """执行验证步骤管线。

        签名和返回结构与原 TaskRunner 完全兼容。
        """
        if not REGISTRY.validate_step(step):
            raise ValueError(f"unsupported verification step: {step}")

        session = RunnerSession(requested_step=step)
        results = self._pipeline.run(step, session, dict(kwargs))

        if debug:
            results["debug"] = self._build_debug_output(session.window_handle, "发布商品")

        results["session"] = {
            "session_id": session.session_id,
            "requested_step": session.requested_step,
            "window_handle": session.window_handle,
            "page_state": session.page_state,
            "completed_steps": session.completed_steps,
            "trace": session.trace,
            "halted": session.halted,
            "last_message": session.last_message,
            "max_retry_count": session.max_retry_count,
            # BL-086B: 视觉对比截图路径
            "screenshot_before": session.screenshot_before,
            "screenshot_after": session.screenshot_after,
        }
        return results

    def _build_debug_output(
            self, window_handle: str | None, target_text: str
    ) -> dict[str, object]:
        """构建调试输出（窗口快照、候选控件、点击诊断）。

        保留用于 debug=True 模式，与原实现完全一致。
        """
        adapter = self.workflow_service.window_manager.adapter
        output: dict[str, object] = {}
        if hasattr(adapter, "build_window_debug_snapshot"):
            output["window_snapshot"] = adapter.build_window_debug_snapshot()
        if window_handle and hasattr(adapter, "list_candidate_controls"):
            output["candidate_controls"] = adapter.list_candidate_controls(
                window_handle, target_text
            )
        if window_handle and hasattr(adapter, "build_click_diagnostics"):
            output["click_diagnostics"] = adapter.build_click_diagnostics(
                window_handle, target_text
            )
        return output
