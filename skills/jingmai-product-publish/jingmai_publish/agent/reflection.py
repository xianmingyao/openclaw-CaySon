"""AgentReflection: rule-driven decision engine for step execution outcomes.

BL-091: Replaces _is_verified() + hardcoded retry logic with structured
ReflectionDecision enum and RuntimeEventLoop integration.

Phase C (BL-092/BL-095): Optional vision_analysis parameter strengthens
CONTINUE/RETRY decisions with visual confirmation of UI state changes.
"""

from __future__ import annotations

from typing import Any

from jingmai_publish.runtime.event_loop import EventType, RuntimeEventLoop
from .types import ActionStep, ReflectionDecision, StepCategory


class AgentReflection:
    """Evaluates execution outcomes and produces ReflectionDecisions.

    Rule-driven (Phase B), with extension points for LLM providers (Phase C).
    Emits REFLECTION_RECORDED events through the optional event loop.

    Phase C: accept optional vision_analysis dict to strengthen decisions.
    When vision confirms the expected UI state change, confidence increases;
    when vision contradicts text-based success, RETRY is preferred over ABORT.
    """

    def __init__(self, event_loop: RuntimeEventLoop | None = None) -> None:
        self.event_loop = event_loop

    def reflect(
            self,
            step: ActionStep,
            outcome: Any,
            session: Any,
            attempt_no: int,
            lane_index: int = 0,
            lane_count: int = 0,
            vision_analysis: dict[str, Any] | None = None,
    ) -> ReflectionDecision:
        """Evaluate an execution outcome and return a decision.

        BL-103: Lane-aware decision logic.
        When lane_count > 0 (retry lanes defined):
          1. success → CONTINUE
          2. window_not_found → ABORT
          3. probe + fail → SKIP
          4. attempt_no < step.same_lane_max_retries → RETRY (same lane)
          5. lane_index + 1 < lane_count → RETRY_NEXT_LANE
          6. otherwise → HUMAN_ESCALATE

        When lane_count == 0 (no lanes, backward compatible):
          1. success → CONTINUE
          2. window_not_found → ABORT
          3. probe + fail → SKIP
          4. attempt < max_retry_count → RETRY
          5. otherwise → ABORT

        Phase C vision_analysis: 可选 dict，含 vision_success/vision_confidence/vision_page_state。
        当文本判断为失败但视觉校验通过时，降级为 RETRY 而非 ABORT。
        """
        success = self._is_success(outcome)

        # Phase C: vision-assisted decision refinement
        vision_success = None
        if vision_analysis:
            vision_success = vision_analysis.get("vision_success")

        decision: ReflectionDecision
        reason: str

        if success:
            decision = ReflectionDecision.CONTINUE
            reason = "step succeeded"
        elif self._is_window_not_found(outcome):
            decision = ReflectionDecision.ABORT
            reason = "window not found"
        elif step.category == StepCategory.PROBE:
            decision = ReflectionDecision.SKIP
            reason = "probe step failed, non-critical — skipping"
        elif lane_count > 0:
            # BL-103: lane-aware retry
            if attempt_no < step.same_lane_max_retries:
                decision = ReflectionDecision.RETRY
                reason = (
                    f"lane {lane_index + 1}/{lane_count} "
                    f"attempt {attempt_no}/{step.same_lane_max_retries} failed, retrying same lane"
                )
            elif lane_index + 1 < lane_count:
                decision = ReflectionDecision.RETRY_NEXT_LANE
                reason = (
                    f"lane {lane_index + 1}/{lane_count} exhausted "
                    f"({attempt_no} attempts), switching to lane {lane_index + 2}"
                )
            else:
                # Phase C: 视觉校验通过时不直接 ABORT，降级为 RETRY（最多一次额外重试）
                if vision_success is True and attempt_no < step.same_lane_max_retries + 1:
                    decision = ReflectionDecision.RETRY
                    reason = (
                        f"all lanes exhausted but vision confirms expected state — retrying "
                        f"(attempt {attempt_no})"
                    )
                else:
                    decision = ReflectionDecision.HUMAN_ESCALATE
                    reason = (
                        f"all {lane_count} lanes exhausted ({attempt_no} attempts on final lane), "
                        f"escalating to human review"
                    )
        elif attempt_no < step.max_retry_count:
            decision = ReflectionDecision.RETRY
            reason = f"attempt {attempt_no}/{step.max_retry_count} failed, retrying"
        else:
            # Phase C: 视觉校验通过时不直接 ABORT，降级为 RETRY（最多一次额外重试）
            if vision_success is True and attempt_no < step.max_retry_count + 1:
                decision = ReflectionDecision.RETRY
                reason = (
                    f"all {attempt_no} attempts exhausted but vision confirms expected state "
                    f"— granting one extra retry"
                )
            else:
                decision = ReflectionDecision.ABORT
                reason = f"all {attempt_no} attempts exhausted"

        self._emit(step, outcome, decision, reason, attempt_no)
        return decision

    # ── outcome 分析 ──────────────────────────────────────────────

    @staticmethod
    def _is_success(outcome: Any) -> bool:
        """判断执行结果是否成功。

        WorkflowStepResult → .success 字段
        dict → "success" 键
        其他 → 视为成功（保守策略）
        """
        from jingmai_publish.services.jingmai_workflow import WorkflowStepResult  # 延迟导入，避免循环依赖
        if isinstance(outcome, WorkflowStepResult):
            return bool(outcome.success)
        if isinstance(outcome, dict) and "success" in outcome:
            return bool(outcome["success"])
        return True

    @staticmethod
    def _is_window_not_found(outcome: Any) -> bool:
        """检测窗口丢失错误（触发 ABORT）。"""
        from jingmai_publish.services.jingmai_workflow import WorkflowStepResult  # 延迟导入，避免循环依赖
        if isinstance(outcome, WorkflowStepResult):
            return outcome.page_state == "window_not_found"
        if isinstance(outcome, dict):
            return outcome.get("page_state") == "window_not_found"
        return False

    @staticmethod
    def _extract_message(outcome: Any) -> str:
        """从 outome 中提取错误消息（用于事件 payload）。"""
        from jingmai_publish.services.jingmai_workflow import WorkflowStepResult  # 延迟导入，避免循环依赖
        if isinstance(outcome, WorkflowStepResult):
            return outcome.message or ""
        if isinstance(outcome, dict):
            return str(outcome.get("message", ""))
        return ""

    # ── 事件发射 ──────────────────────────────────────────────────

    def _emit(
            self,
            step: ActionStep,
            outcome: Any,
            decision: ReflectionDecision,
            reason: str,
            attempt_no: int,
    ) -> None:
        """发射 REFLECTION_RECORDED 事件（如果有 event_loop）。"""
        if self.event_loop is None:
            return
        self.event_loop.enqueue(EventType.REFLECTION_RECORDED, {
            "step_name": step.step_name,
            "category": step.category.value,
            "attempt_no": attempt_no,
            "max_retry": step.max_retry_count,
            "success": self._is_success(outcome),
            "decision": decision.value,
            "reason": reason,
            "message": self._extract_message(outcome),
            "lane_count": len(step.retry_lanes),
        })
