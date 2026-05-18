"""test_agent_reflection.py — AgentReflection 测试。
BL-091: 验证四种决策分支、事件发射、无 event_loop 优雅降级。
"""

from __future__ import annotations

import pytest

from jingmai_publish.agent.reflection import AgentReflection
from jingmai_publish.agent.types import ActionStep, ReflectionDecision, StepCategory
from jingmai_publish.runtime.event_loop import EventType, RuntimeEventLoop
from jingmai_publish.services.jingmai_workflow import WorkflowStepResult


@pytest.fixture
def step():
    return ActionStep(
        step_name="t2",
        method_name="run_t2_enter_publish_entry",
        category=StepCategory.NAVIGATION,
        max_retry_count=3,
    )


@pytest.fixture
def probe_step():
    return ActionStep(
        step_name="t5-probe",
        method_name="_run_t5_probe",
        category=StepCategory.PROBE,
        max_retry_count=3,
    )


class FakeSession:
    pass


def test_reflect_success_returns_continue(step):
    """成功结果应返回 CONTINUE。"""
    reflection = AgentReflection()
    outcome = WorkflowStepResult(step_id="T2", success=True, page_state="ok")
    decision = reflection.reflect(step, outcome, FakeSession(), 1)
    assert decision == ReflectionDecision.CONTINUE


def test_reflect_window_not_found_returns_abort(step):
    """窗口丢失应返回 ABORT。"""
    reflection = AgentReflection()
    outcome = WorkflowStepResult(step_id="T2", success=False, page_state="window_not_found")
    decision = reflection.reflect(step, outcome, FakeSession(), 1)
    assert decision == ReflectionDecision.ABORT


def test_reflect_probe_fail_returns_skip(probe_step):
    """探测步骤失败应返回 SKIP（非关键步骤）。"""
    reflection = AgentReflection()
    outcome = WorkflowStepResult(step_id="T5", success=False, page_state="error")
    decision = reflection.reflect(probe_step, outcome, FakeSession(), 1)
    assert decision == ReflectionDecision.SKIP


def test_reflect_retry_before_max_attempts(step):
    """未超过 max_retry_count 应返回 RETRY。"""
    reflection = AgentReflection()
    outcome = WorkflowStepResult(step_id="T2", success=False, page_state="error")
    decision = reflection.reflect(step, outcome, FakeSession(), 2)  # attempt 2 < max 3
    assert decision == ReflectionDecision.RETRY


def test_reflect_abort_after_max_attempts(step):
    """重试次数耗尽应返回 ABORT。"""
    reflection = AgentReflection()
    outcome = WorkflowStepResult(step_id="T2", success=False, page_state="error")
    decision = reflection.reflect(step, outcome, FakeSession(), 3)  # attempt 3 >= max 3
    assert decision == ReflectionDecision.ABORT


def test_reflect_emits_event_when_event_loop_present(step):
    """有 event_loop 时应发射 REFLECTION_RECORDED 事件。"""
    import time
    event_loop = RuntimeEventLoop()
    event_loop.start()
    reflection = AgentReflection(event_loop=event_loop)
    outcome = WorkflowStepResult(step_id="T2", success=True, page_state="ok")
    reflection.reflect(step, outcome, FakeSession(), 1)

    time.sleep(0.2)  # 等待 worker 线程处理事件队列
    event_loop.stop()
    events = event_loop.event_history()
    reflection_events = [e for e in events if e["event_type"] == EventType.REFLECTION_RECORDED.value]
    assert len(reflection_events) == 1


def test_reflect_no_event_loop_does_not_raise(step):
    """无 event_loop 时不应抛出异常。"""
    reflection = AgentReflection(event_loop=None)
    outcome = WorkflowStepResult(step_id="T2", success=True, page_state="ok")
    decision = reflection.reflect(step, outcome, FakeSession(), 1)
    assert decision == ReflectionDecision.CONTINUE


def test_reflect_dict_outcome_success():
    """dict 类型 outcome 有 'success' 键时正确判断。"""
    reflection = AgentReflection()
    step = ActionStep(
        step_name="test", method_name="test",
        category=StepCategory.PROBE, max_retry_count=3,
    )
    outcome = {"success": True, "page_state": "ok"}
    decision = reflection.reflect(step, outcome, FakeSession(), 1)
    assert decision == ReflectionDecision.CONTINUE
