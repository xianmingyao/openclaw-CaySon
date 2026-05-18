"""Tests for BL-102 Audit Repository (UiArtifact / ActionEvent / ReflectionCase)."""

from __future__ import annotations

import pytest

from jingmai_publish.models import ActionEvent, ReflectionCase, UiArtifact
from jingmai_publish.repositories.audit import AuditRepository


class FakeSession:
    """Mock SQLAlchemy Session for repository unit tests."""

    def __init__(self) -> None:
        self.added: list = []
        self.flushed = False
        self.committed = False

    def add(self, instance) -> None:
        self.added.append(instance)

    def flush(self) -> None:
        self.flushed = True

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        pass


@pytest.fixture
def repo() -> AuditRepository:
    return AuditRepository(FakeSession())


# ── UiArtifact 测试 ──────────────────────────────────────────────


class TestAppendUiArtifact:
    def test_basic_artifact(self, repo):
        artifact = repo.append_ui_artifact(
            task_id="task-001",
            session_id="sess-001",
            step_id="t1",
            artifact_type="window",
            name="京麦商家后台",
        )
        assert isinstance(artifact, UiArtifact)
        assert artifact.task_id == "task-001"
        assert artifact.artifact_type == "window"
        assert artifact.name == "京麦商家后台"

    def test_all_fields_persisted(self, repo):
        artifact = repo.append_ui_artifact(
            task_id="task-002",
            session_id="sess-002",
            step_id="t2",
            artifact_type="control",
            automation_id="btnPublish",
            control_type="Button",
            class_name="QPushButton",
            name="发布",
            text_value="发布",
            rect_left=100,
            rect_top=200,
            rect_right=300,
            rect_bottom=250,
            properties_json={"enabled": True},
            screenshot_path="/tmp/screenshots/t2_before.png",
        )
        assert artifact.automation_id == "btnPublish"
        assert artifact.control_type == "Button"
        assert artifact.class_name == "QPushButton"
        assert artifact.rect_left == 100
        assert artifact.rect_bottom == 250
        assert artifact.properties_json == {"enabled": True}
        assert artifact.screenshot_path == "/tmp/screenshots/t2_before.png"

    def test_flushes_session(self, repo):
        repo.append_ui_artifact(
            task_id="task-003",
            session_id="sess-003",
            step_id="t3",
            artifact_type="text",
            text_value="商品已保存",
        )
        assert repo.session.flushed is True

    def test_adds_to_session(self, repo):
        artifact = repo.append_ui_artifact(
            task_id="task-004",
            session_id="sess-004",
            step_id="t4",
            artifact_type="window",
        )
        assert artifact in repo.session.added


# ── ActionEvent 测试 ─────────────────────────────────────────────


class TestAppendActionEvent:
    def test_basic_event(self, repo):
        event = repo.append_action_event(
            task_id="task-001",
            session_id="sess-001",
            step_id="t2",
            action_type="click",
            target_element="btnPublish",
            outcome="success",
        )
        assert isinstance(event, ActionEvent)
        assert event.action_type == "click"
        assert event.outcome == "success"
        assert event.retry_attempt == 1

    def test_failure_event(self, repo):
        event = repo.append_action_event(
            task_id="task-002",
            session_id="sess-002",
            step_id="t6",
            action_type="fill",
            target_element="inputTitle",
            outcome="failure",
            error_message="element not found",
            retry_attempt=2,
        )
        assert event.outcome == "failure"
        assert event.error_message == "element not found"
        assert event.retry_attempt == 2

    def test_with_screenshots(self, repo):
        event = repo.append_action_event(
            task_id="task-003",
            session_id="sess-003",
            step_id="t3",
            action_type="upload",
            screenshot_before="/tmp/before.png",
            screenshot_after="/tmp/after.png",
            duration_ms=1500,
        )
        assert event.screenshot_before == "/tmp/before.png"
        assert event.screenshot_after == "/tmp/after.png"
        assert event.duration_ms == 1500

    def test_with_lane_info(self, repo):
        event = repo.append_action_event(
            task_id="task-004",
            session_id="sess-004",
            step_id="t5",
            action_type="fill",
            lane_name="uia_text",
        )
        assert event.lane_name == "uia_text"

    def test_flushes_session(self, repo):
        repo.append_action_event(
            task_id="task-005",
            session_id="sess-005",
            step_id="t6",
            action_type="navigate",
        )
        assert repo.session.flushed is True


# ── ReflectionCase 测试 ──────────────────────────────────────────


class TestAppendReflectionCase:
    def test_basic_continue(self, repo):
        case = repo.append_reflection_case(
            task_id="task-001",
            session_id="sess-001",
            step_id="t1",
            decision="continue",
            reason="步骤执行成功，无异常",
            attempt_no=1,
        )
        assert isinstance(case, ReflectionCase)
        assert case.decision == "continue"
        assert case.reason == "步骤执行成功，无异常"
        assert case.attempt_no == 1

    def test_retry_decision(self, repo):
        case = repo.append_reflection_case(
            task_id="task-002",
            session_id="sess-002",
            step_id="t5",
            decision="retry",
            reason="控件未找到，尝试重试",
            attempt_no=2,
            lane_index=1,
            lane_count=4,
        )
        assert case.decision == "retry"
        assert case.attempt_no == 2
        assert case.lane_index == 1
        assert case.lane_count == 4

    def test_with_vision_analysis(self, repo):
        case = repo.append_reflection_case(
            task_id="task-003",
            session_id="sess-003",
            step_id="t3",
            decision="retry",
            reason="视觉对比发现差异较大",
            attempt_no=1,
            vision_success=0,
            vision_confidence=0.35,
            vision_page_state="upload_failed",
            before_screenshot_path="/tmp/before_t3.png",
            after_screenshot_path="/tmp/after_t3.png",
            text_diff="页面文本差异: 预期'上传成功'实际'上传失败'",
            failure_pattern="视觉校验不通过",
        )
        assert case.vision_success == 0
        assert case.vision_confidence == 0.35
        assert case.vision_page_state == "upload_failed"
        assert case.before_screenshot_path == "/tmp/before_t3.png"
        assert case.text_diff is not None
        assert case.failure_pattern == "视觉校验不通过"

    def test_abort_decision(self, repo):
        case = repo.append_reflection_case(
            task_id="task-004",
            session_id="sess-004",
            step_id="t6",
            decision="abort",
            reason="窗口丢失，重试耗尽",
            attempt_no=3,
        )
        assert case.decision == "abort"

    def test_skip_decision(self, repo):
        case = repo.append_reflection_case(
            task_id="task-005",
            session_id="sess-005",
            step_id="t4",
            decision="skip",
            reason="非必填步骤，跳过",
            attempt_no=1,
        )
        assert case.decision == "skip"

    def test_flushes_session(self, repo):
        repo.append_reflection_case(
            task_id="task-006",
            session_id="sess-006",
            step_id="t2",
            decision="continue",
            reason="ok",
        )
        assert repo.session.flushed is True
