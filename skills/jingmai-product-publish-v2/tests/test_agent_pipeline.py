"""test_agent_pipeline.py — AgentPipeline 测试。
BL-091: 验证全管线集成、T1 失败停止、重试成功、结果结构兼容。
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from jingmai_publish.agent import REGISTRY, AgentExecutor, AgentPipeline, AgentReflection
from jingmai_publish.services.jingmai_workflow import WorkflowStepResult


class FakeSession:
    """最小 session 模拟类。"""

    def __init__(self) -> None:
        self.window_handle = None
        self.trace: list[dict] = []
        self.completed_steps: list[str] = []
        self.page_state = None
        self.halted = False
        self.last_message = None
        self.max_retry_count = 3


def _build_pipeline(service):
    executor = AgentExecutor(service)
    reflection = AgentReflection()
    return AgentPipeline(REGISTRY, executor, reflection)


def test_pipeline_both_full_flow():
    """both 全管线：T1 + T2 均成功，结果结构兼容。"""
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1", success=True, page_state="jingmai_home", window_handle="2002",
    )
    service.run_t2_enter_publish_entry.return_value = WorkflowStepResult(
        step_id="T2", success=True, page_state="publish_entry", window_handle="2002",
    )

    pipeline = _build_pipeline(service)
    session = FakeSession()
    results = pipeline.run("both", session, {})

    assert "t1" in results
    assert "t2" in results
    assert results["t1"]["success"] is True
    assert results["t2"]["success"] is True
    assert session.completed_steps == ["T1", "T2"]
    assert session.halted is False


def test_pipeline_t1_failure_stops_plan():
    """T1 失败应 halted=True，不执行后续步骤。"""
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.side_effect = ValueError("window missing")

    pipeline = _build_pipeline(service)
    session = FakeSession()
    results = pipeline.run("both", session, {})

    assert results["t1"]["success"] is False
    assert "t2" not in results
    assert session.halted is True


def test_pipeline_retry_on_failure():
    """首次失败后重试，第二次成功。"""
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1", success=True, page_state="jingmai_home", window_handle="2002",
    )
    service.run_t2_enter_publish_entry.side_effect = [
        WorkflowStepResult(step_id="T2", success=False, page_state="error", message="fail-1"),
        WorkflowStepResult(step_id="T2", success=True, page_state="publish_entry", window_handle="2002"),
    ]

    pipeline = _build_pipeline(service)
    session = FakeSession()
    results = pipeline.run("both", session, {})

    assert service.run_t2_enter_publish_entry.call_count == 2
    assert results["t2"]["success"] is True
    assert len(session.trace) >= 2  # at least 2 trace entries (T1 + T2)
    t2_trace = [t for t in session.trace if t["planned_step"] == "t2"]
    assert len(t2_trace) == 2
    assert t2_trace[0]["verified"] is False
    assert t2_trace[1]["verified"] is True


def test_pipeline_trace_entries_format():
    """trace 条目格式应与原 TaskRunner 兼容。"""
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1", success=True, page_state="home", window_handle="2002",
    )

    pipeline = _build_pipeline(service)
    session = FakeSession()
    pipeline.run("t1", session, {})

    assert len(session.trace) == 1
    entry = session.trace[0]
    assert entry["planned_step"] == "t1"
    assert entry["attempt_no"] == 1
    assert "before_state" in entry
    assert "after_state" in entry
    assert "verified" in entry


def test_pipeline_exception_wraps_as_workflow_result():
    """异常应被包装为 WorkflowStepResult(success=False)。"""
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.side_effect = RuntimeError("unexpected crash")

    pipeline = _build_pipeline(service)
    session = FakeSession()
    results = pipeline.run("t1", session, {})

    assert results["t1"]["success"] is False
    assert results["t1"]["page_state"] == "error"
    assert "unexpected crash" in results["t1"]["message"]


def test_pipeline_result_structure_matches_original():
    """结果结构应与原 TaskRunner.run() 兼容。"""
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1", success=True, page_state="jingmai_home", window_handle="2002",
    )
    service.run_t2_enter_publish_entry.return_value = WorkflowStepResult(
        step_id="T2", success=True, page_state="publish_entry", window_handle="2002",
    )

    pipeline = _build_pipeline(service)
    session = FakeSession()
    results = pipeline.run("both", session, {})

    # 原 TaskRunner 返回结构中有 't1' 和 't2' 键
    assert "t1" in results
    assert "t2" in results
    assert results["t1"]["step_id"] == "T1"
    assert results["t2"]["step_id"] == "T2"
    assert results["t1"]["success"] is True
    assert results["t2"]["success"] is True
