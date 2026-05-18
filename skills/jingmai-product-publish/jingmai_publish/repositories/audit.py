"""Phase D 审计 Repository —— UiArtifact / ActionEvent / ReflectionCase。

对应 BL-102 三张审计表，记录 AgentPipeline 执行过程中产生的：
- UI 元素观测（UiArtifact）
- 自动化动作事件（ActionEvent）
- 反思决策案例（ReflectionCase）
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from jingmai_publish.models import ActionEvent, ReflectionCase, UiArtifact


class AuditRepository:
    """审计数据写入仓库。

    注入 SQLAlchemy Session，所有方法遵循 RuntimeLogRepository 模式：
    创建模型实例 → session.add() → session.flush() → 返回实例。
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    # ── UiArtifact ────────────────────────────────────────────────

    def append_ui_artifact(
            self,
            *,
            task_id: str,
            session_id: str,
            step_id: str,
            artifact_type: str,  # window/control/text/tree
            automation_id: str | None = None,
            control_type: str | None = None,
            class_name: str | None = None,
            name: str | None = None,
            text_value: str | None = None,
            rect_left: int | None = None,
            rect_top: int | None = None,
            rect_right: int | None = None,
            rect_bottom: int | None = None,
            properties_json: dict | None = None,
            screenshot_path: str | None = None,
    ) -> UiArtifact:
        """记录一次 UI 元素观测。"""
        artifact = UiArtifact(
            task_id=task_id,
            session_id=session_id,
            step_id=step_id,
            artifact_type=artifact_type,
            automation_id=automation_id,
            control_type=control_type,
            class_name=class_name,
            name=name,
            text_value=text_value,
            rect_left=rect_left,
            rect_top=rect_top,
            rect_right=rect_right,
            rect_bottom=rect_bottom,
            properties_json=properties_json,
            screenshot_path=screenshot_path,
        )
        self.session.add(artifact)
        self.session.flush()
        return artifact

    # ── ActionEvent ───────────────────────────────────────────────

    def append_action_event(
            self,
            *,
            task_id: str,
            session_id: str,
            step_id: str,
            action_type: str,  # click/fill/upload/select/navigate
            target_element: str | None = None,
            lane_name: str | None = None,
            action_params_json: str | None = None,
            outcome: str = "success",
            duration_ms: int | None = None,
            retry_attempt: int = 1,
            screenshot_before: str | None = None,
            screenshot_after: str | None = None,
            error_message: str | None = None,
    ) -> ActionEvent:
        """记录一次自动化动作事件。"""
        event = ActionEvent(
            task_id=task_id,
            session_id=session_id,
            step_id=step_id,
            action_type=action_type,
            target_element=target_element,
            lane_name=lane_name,
            action_params_json=action_params_json,
            outcome=outcome,
            duration_ms=duration_ms,
            retry_attempt=retry_attempt,
            screenshot_before=screenshot_before,
            screenshot_after=screenshot_after,
            error_message=error_message,
        )
        self.session.add(event)
        self.session.flush()
        return event

    # ── ReflectionCase ────────────────────────────────────────────

    def append_reflection_case(
            self,
            *,
            task_id: str,
            session_id: str,
            step_id: str,
            decision: str,  # continue/retry/skip/abort
            reason: str,
            attempt_no: int = 1,
            lane_index: int | None = None,
            lane_count: int | None = None,
            vision_success: int | None = None,  # 0/1
            vision_confidence: float | None = None,
            vision_page_state: str | None = None,
            before_screenshot_path: str | None = None,
            after_screenshot_path: str | None = None,
            text_diff: str | None = None,
            failure_pattern: str | None = None,
    ) -> ReflectionCase:
        """记录一次反思决策案例。"""
        case = ReflectionCase(
            task_id=task_id,
            session_id=session_id,
            step_id=step_id,
            decision=decision,
            reason=reason,
            attempt_no=attempt_no,
            lane_index=lane_index,
            lane_count=lane_count,
            vision_success=vision_success,
            vision_confidence=vision_confidence,
            vision_page_state=vision_page_state,
            before_screenshot_path=before_screenshot_path,
            after_screenshot_path=after_screenshot_path,
            text_diff=text_diff,
            failure_pattern=failure_pattern,
        )
        self.session.add(case)
        self.session.flush()
        return case
