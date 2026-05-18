"""AgentPipeline: Planner → Executor → Reflection orchestration.

BL-091: Replaces TaskRunner.run() hardcoded dispatch with structured pipeline.
The pipeline owns the full decision loop: plan, execute with retry, reflect,
and accumulate session state / trace.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .executor import AgentExecutor
from .planner import AgentPlanner
from .reflection import AgentReflection
from .registry import ActionRegistry
from .types import ActionStep, ReflectionDecision, RetryLane, StepValidationError


class AgentPipeline:
    """Orchestrates the Planner → Executor → Reflection decision loop.

    Usage::

        pipeline = AgentPipeline(registry, executor, reflection)
        results = pipeline.run("both", session, params)
    """

    def __init__(
            self,
            registry: ActionRegistry,
            executor: AgentExecutor,
            reflection: AgentReflection,
            vision_provider: Any | None = None,
    ) -> None:
        self.planner = AgentPlanner(registry)
        self.executor = executor
        self.reflection = reflection
        self.vision_provider = vision_provider  # BL-086B: 可选视觉校验

    def run(
            self,
            step_name: str,
            session: Any,
            params: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a complete plan for the requested step.

        Returns a dict compatible with the original TaskRunner.run() format:
        {t1: {...}, t2: {...}, ..., session: {...}}
        """
        plan = self.planner.plan(step_name)
        results: dict[str, Any] = {}

        for action_step in plan.steps:
            outcome = self._execute_step_with_retry(action_step, session, params)
            result_key = action_step.step_name.replace("-", "_")

            from jingmai_publish.services.jingmai_workflow import WorkflowStepResult  # 延迟导入
            if isinstance(outcome, WorkflowStepResult):
                results[result_key] = asdict(outcome)
                self._apply_workflow_result(session, outcome)
                if not outcome.success:
                    session.halted = True
                    break
            else:
                results[result_key] = outcome

        return results

    # ── 步骤执行 + 重试循环 (BL-103 Lane Switching) ──────────────

    def _execute_step_with_retry(
            self,
            step: ActionStep,
            session: Any,
            params: dict[str, Any],
    ) -> Any:
        """Execute a single step with retry logic guided by reflection decisions.

        BL-103: Three-level retry strategy.
        - Same lane retry (attempt 1..same_lane_max_retries)
        - Lane switch (try next alternative lane in step.retry_lanes)
        - Human escalation (all lanes exhausted)

        When step.retry_lanes is empty, falls back to simple retry (backward compatible).

        Inner loop: execute → reflect → CONTINUE/RETRY/RETRY_NEXT_LANE/SKIP/ABORT/HUMAN_ESCALATE.
        Trace entries are appended to session.trace after each attempt, with lane info.
        """
        lanes = step.retry_lanes
        lane_count = len(lanes)
        lane_index = 0
        attempt_in_lane = 1
        last_outcome = None

        while True:
            # 选择当前 lane（无 lane 时 lane=None，走默认方法）
            lane = lanes[lane_index] if lane_index < lane_count else None

            # BL-086B: 设置 before 截图（来自上一步的 after 截图）
            session.screenshot_before = getattr(session, "last_screenshot", None)

            before_state = self._capture_before_state(session)

            try:
                outcome = self.executor.execute(step, session, params, lane=lane)
            except StepValidationError:
                raise  # 参数/内容校验错误直接传播
            except Exception as exc:
                from jingmai_publish.services.jingmai_workflow import WorkflowStepResult  # 延迟导入，避免循环依赖
                outcome = WorkflowStepResult(
                    step_id=step.step_name.upper(),
                    success=False,
                    page_state="error",
                    message=str(exc),
                )

            last_outcome = outcome

            # BL-086B: 设置 after 截图（WorkflowStepResult 自带 screenshot_path）
            from jingmai_publish.services.jingmai_workflow import WorkflowStepResult  # 延迟导入
            if isinstance(outcome, WorkflowStepResult) and outcome.screenshot_path:
                session.screenshot_after = outcome.screenshot_path
                # 更新 last_screenshot，供下一步作为 before 使用
                session.last_screenshot = outcome.screenshot_path

            # BL-086B: 视觉对比校验
            vision_analysis = self._compare_with_vision(session)

            # 记录 trace（兼容原 TaskRunner 格式）
            verified = self.reflection._is_success(outcome)
            after_state = self._capture_after_state(outcome, session)
            failure_signature = (
                self._build_failure_signature(step, attempt_in_lane, outcome, lane)
                if not verified
                else None
            )
            trace_entry: dict[str, Any] = {
                "planned_step": step.step_name,
                "attempt_no": attempt_in_lane,
                "before_state": before_state,
                "after_state": after_state,
                "verified": verified,
                "failure_signature": failure_signature,
            }
            if lane:
                trace_entry["lane"] = lane.lane_name
                trace_entry["lane_index"] = lane_index
                trace_entry["lane_count"] = lane_count
            # BL-086B: trace 记录视觉校验结果
            if vision_analysis:
                trace_entry["vision_analysis"] = vision_analysis
            session.trace.append(trace_entry)

            # 反射决策（含 lane 上下文 + 视觉分析）
            decision = self.reflection.reflect(
                step, outcome, session, attempt_in_lane,
                lane_index=lane_index, lane_count=lane_count,
                vision_analysis=vision_analysis,
            )

            if decision == ReflectionDecision.CONTINUE:
                return outcome
            elif decision == ReflectionDecision.RETRY:
                attempt_in_lane += 1
                continue
            elif decision == ReflectionDecision.RETRY_NEXT_LANE:
                lane_index += 1
                attempt_in_lane = 1
                continue
            elif decision in (ReflectionDecision.SKIP, ReflectionDecision.ABORT,
                              ReflectionDecision.HUMAN_ESCALATE):
                break

        return last_outcome

    # ── session 状态管理 ──────────────────────────────────────────

    @staticmethod
    def _apply_workflow_result(session: Any, result: WorkflowStepResult) -> None:
        """将 WorkflowStepResult 的状态写回 session。

        保持与原 TaskRunner._apply_workflow_result() 完全一致的行为。
        """
        session.window_handle = result.window_handle or session.window_handle
        session.page_state = result.page_state
        session.completed_steps.append(result.step_id)
        session.last_message = result.message

    @staticmethod
    def _capture_before_state(session: Any) -> dict[str, Any]:
        """捕获步骤执行前的 session 状态快照（用于 trace）。

        BL-086B: 包含 before 截图路径，用于视觉对比溯源。
        """
        snapshot: dict[str, Any] = {
            "window_handle": session.window_handle,
            "page_state": session.page_state,
            "completed_steps": list(session.completed_steps),
        }
        before = getattr(session, "screenshot_before", None)
        if before:
            snapshot["screenshot_before"] = before
        return snapshot

    @staticmethod
    def _capture_after_state(outcome: Any, session: Any) -> dict[str, Any]:
        """捕获步骤执行后的状态快照（用于 trace）。"""
        from jingmai_publish.services.jingmai_workflow import WorkflowStepResult  # 延迟导入
        if isinstance(outcome, WorkflowStepResult):
            return {
                "window_handle": outcome.window_handle or session.window_handle,
                "page_state": outcome.page_state,
                "screenshot_path": outcome.screenshot_path,
                "message": outcome.message,
            }
        return {
            "window_handle": session.window_handle,
            "page_state": session.page_state,
            "result_type": type(outcome).__name__,
        }

    @staticmethod
    def _build_failure_signature(
            step: ActionStep, attempt_no: int, outcome: Any,
            lane: RetryLane | None = None,
    ) -> str:
        """构建失败签名（用于 trace + memory provider 持久化）。

        BL-103: 包含 lane 信息以便区分不同 lane 的失败模式。
        """
        from jingmai_publish.services.jingmai_workflow import WorkflowStepResult  # 延迟导入
        lane_tag = f"|lane={lane.lane_name}" if lane else ""
        if isinstance(outcome, WorkflowStepResult):
            message = outcome.message or "no_message"
            return (
                f"{step.step_name}{lane_tag}|attempt={attempt_no}"
                f"|page={outcome.page_state}|message={message}"
            )
        return f"{step.step_name}{lane_tag}|attempt={attempt_no}|result=unverified"

    # ── BL-086B: 视觉对比校验 ──────────────────────────────────────

    def _compare_with_vision(self, session: Any) -> dict[str, Any] | None:
        """对比 before/after 截图，返回 vision_analysis dict。

        当 vision_provider 可用且 before/after 截图都存在时，
        调用 compare_screenshots() 进行视觉差异分析。

        返回 dict 包含: vision_success, vision_confidence, vision_page_state,
        vision_text_diff, vision_elements_changed, vision_raw_response, vision_model.
        """
        if self.vision_provider is None:
            return None

        before = getattr(session, "screenshot_before", None)
        after = getattr(session, "screenshot_after", None)

        if not before or not after:
            return None

        try:
            from pathlib import Path
            if not Path(before).exists() or not Path(after).exists():
                return None

            result = self.vision_provider.compare_screenshots(before, after)

            return {
                "vision_success": result.success,
                "vision_confidence": result.confidence,
                "vision_page_state": result.page_state,
                "vision_text_diff": result.text_content or "",
                "vision_elements_changed": len(result.elements) if result.elements else 0,
                "vision_raw_response": result.raw_response,
                "vision_model": result.model,
            }
        except Exception:
            # 视觉校验失败不阻塞主流程
            return None
