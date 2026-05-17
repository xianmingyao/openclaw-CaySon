"""test_agent_retry_lanes.py — BL-103 Retry Lane Switching 测试。

验证三级重试策略：同 lane 重试 → lane 切换 → 人工升级。
覆盖 Reflection 决策、Pipeline lane 调度、Executor lane 参数传递。
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from jingmai_publish.agent.executor import AgentExecutor
from jingmai_publish.agent.pipeline import AgentPipeline
from jingmai_publish.agent.reflection import AgentReflection
from jingmai_publish.agent.registry import ActionRegistry, REGISTRY_ENTRIES
from jingmai_publish.agent.types import (
    ActionStep,
    ReflectionDecision,
    RetryLane,
    StepCategory,
)
from jingmai_publish.runtime.event_loop import RuntimeEventLoop
from jingmai_publish.services.jingmai_workflow import WorkflowStepResult


# ── Fixtures ──────────────────────────────────────────────────────


@pytest.fixture
def step_with_lanes():
    """带 3 个 retry lanes 的 ActionStep。"""
    return ActionStep(
        step_name="t6-main-image",
        method_name="run_t6_upload_main_image",
        description="上传商品主图",
        required_params=("image_path",),
        param_map={"image_path": "file_path"},
        category=StepCategory.UPLOAD,
        max_retry_count=2,
        same_lane_max_retries=2,
        retry_lanes=(
            RetryLane("hover_modal", "run_t6_upload_main_image",
                       "悬停槽位上传", {"upload_strategy": "hover_modal"}),
            RetryLane("text_fallback", "run_t6_upload_main_image",
                       "文件对话框输入", {"upload_strategy": "text_fallback"}),
            RetryLane("direct_click", "run_t6_upload_main_image",
                       "直接点击上传", {"upload_strategy": "direct_click"}),
        ),
    )


@pytest.fixture
def step_no_lanes():
    """无 retry lanes 的普通 ActionStep（向后兼容）。"""
    return ActionStep(
        step_name="t2",
        method_name="run_t2_enter_publish_entry",
        category=StepCategory.NAVIGATION,
        max_retry_count=3,
    )


class FakeSession:
    def __init__(self):
        self.window_handle = "hwnd-123"
        self.page_state = "ok"
        self.completed_steps: list[str] = []
        self.last_message = ""
        self.halted = False
        self.trace: list[dict] = []


# ── Reflection 决策测试 ────────────────────────────────────────────


def test_reflect_retry_same_lane_with_lanes(step_with_lanes):
    """带 lane 时，attempt < same_lane_max_retries → RETRY（同 lane 重试）。"""
    reflection = AgentReflection()
    outcome = WorkflowStepResult(step_id="T6", success=False, page_state="error")
    decision = reflection.reflect(
        step_with_lanes, outcome, FakeSession(),
        attempt_no=1, lane_index=0, lane_count=3,
    )
    assert decision == ReflectionDecision.RETRY


def test_reflect_retry_next_lane(step_with_lanes):
    """当前 lane 重试耗尽 + 还有下一个 lane → RETRY_NEXT_LANE。"""
    reflection = AgentReflection()
    outcome = WorkflowStepResult(step_id="T6", success=False, page_state="error")
    decision = reflection.reflect(
        step_with_lanes, outcome, FakeSession(),
        attempt_no=2, lane_index=0, lane_count=3,
    )
    assert decision == ReflectionDecision.RETRY_NEXT_LANE


def test_reflect_human_escalate(step_with_lanes):
    """所有 lane 都耗尽 → HUMAN_ESCALATE。"""
    reflection = AgentReflection()
    outcome = WorkflowStepResult(step_id="T6", success=False, page_state="error")
    decision = reflection.reflect(
        step_with_lanes, outcome, FakeSession(),
        attempt_no=2, lane_index=2, lane_count=3,
    )
    assert decision == ReflectionDecision.HUMAN_ESCALATE


def test_reflect_no_lanes_fallback_to_retry(step_no_lanes):
    """无 lane 时保持旧行为：attempt < max_retry_count → RETRY。"""
    reflection = AgentReflection()
    outcome = WorkflowStepResult(step_id="T2", success=False, page_state="error")
    decision = reflection.reflect(
        step_no_lanes, outcome, FakeSession(),
        attempt_no=2, lane_index=0, lane_count=0,
    )
    assert decision == ReflectionDecision.RETRY


def test_reflect_no_lanes_fallback_to_abort(step_no_lanes):
    """无 lane 时保持旧行为：重试耗尽 → ABORT。"""
    reflection = AgentReflection()
    outcome = WorkflowStepResult(step_id="T2", success=False, page_state="error")
    decision = reflection.reflect(
        step_no_lanes, outcome, FakeSession(),
        attempt_no=3, lane_index=0, lane_count=0,
    )
    assert decision == ReflectionDecision.ABORT


def test_reflect_success_ignores_lanes(step_with_lanes):
    """成功后直接 CONTINUE，不进入 lane 逻辑。"""
    reflection = AgentReflection()
    outcome = WorkflowStepResult(step_id="T6", success=True, page_state="ok")
    decision = reflection.reflect(
        step_with_lanes, outcome, FakeSession(),
        attempt_no=3, lane_index=2, lane_count=3,
    )
    assert decision == ReflectionDecision.CONTINUE


def test_reflect_window_not_found_ignores_lanes(step_with_lanes):
    """窗口丢失始终 ABORT，无论 lane 状态。"""
    reflection = AgentReflection()
    outcome = WorkflowStepResult(step_id="T6", success=False, page_state="window_not_found")
    decision = reflection.reflect(
        step_with_lanes, outcome, FakeSession(),
        attempt_no=1, lane_index=0, lane_count=3,
    )
    assert decision == ReflectionDecision.ABORT


# ── Executor lane 参数测试 ─────────────────────────────────────────


def test_executor_lane_uses_method_name():
    """lane 指定了 method_name 时，executor 应使用 lane 的方法名。"""
    mock_wf = MagicMock()
    mock_wf.window_manager = MagicMock()
    executor = AgentExecutor(mock_wf)
    step = ActionStep(
        step_name="test", method_name="original_method",
        category=StepCategory.ACTION,
    )
    lane = RetryLane("alt", "alternative_method", "替代方案")

    # 确认 executor 使用 lane.method_name
    # 由于 workflow_service 是 mock，alt_method 不存在于 executor 上
    # 它会走 else 分支（workflow_service 反射调度）
    session = FakeSession()
    executor.execute(step, session, {"image_path": "/tmp/test.png"}, lane=lane)
    mock_wf.alternative_method.assert_called_once()


def test_executor_lane_param_overrides_merge():
    """lane.param_overrides 应合并到 params 中（lane 优先）。"""
    mock_wf = MagicMock()
    mock_wf.window_manager = MagicMock()
    executor = AgentExecutor(mock_wf)
    step = ActionStep(
        step_name="test", method_name="original_method",
        category=StepCategory.ACTION,
        required_params=("image_path",),
        param_map={"image_path": "file_path"},
    )
    lane = RetryLane("alt", "original_method", "替代方案",
                     {"upload_strategy": "text_fallback"})

    session = FakeSession()
    executor.execute(step, session, {"image_path": "/tmp/test.png"}, lane=lane)
    call_kwargs = mock_wf.original_method.call_args[1]
    assert call_kwargs.get("upload_strategy") == "text_fallback"
    assert call_kwargs.get("file_path") == "/tmp/test.png"


# ── Pipeline lane 调度测试 ─────────────────────────────────────────


def test_pipeline_lane_switch_on_retry_next_lane():
    """RETRY_NEXT_LANE 时应切换到下一个 lane 继续执行。"""
    mock_wf = MagicMock()
    # 第一次执行失败，第二次（新 lane）成功
    mock_wf.run_t6_upload_main_image.side_effect = [
        WorkflowStepResult(step_id="T6", success=False, page_state="error", message="lane 1 failed"),
        WorkflowStepResult(step_id="T6", success=False, page_state="error", message="lane 1 retry failed"),
        WorkflowStepResult(step_id="T6", success=True, page_state="ok", message="lane 2 succeeded"),
    ]
    mock_wf.window_manager = MagicMock()

    registry = ActionRegistry([ActionStep(
        step_name="t6-main-image",
        method_name="run_t6_upload_main_image",
        category=StepCategory.UPLOAD,
        preconditions=(),
        required_params=("image_path",),
        param_map={"image_path": "file_path"},
        same_lane_max_retries=2,
        retry_lanes=(
            RetryLane("hover_modal", "run_t6_upload_main_image",
                       "悬停槽位", {"upload_strategy": "hover_modal"}),
            RetryLane("text_fallback", "run_t6_upload_main_image",
                       "文件对话框", {"upload_strategy": "text_fallback"}),
        ),
    )])

    executor = AgentExecutor(mock_wf)
    reflection = AgentReflection()
    pipeline = AgentPipeline(registry, executor, reflection)

    session = FakeSession()
    results = pipeline.run("t6-main-image", session, {"image_path": "/tmp/test.png"})

    assert results["t6_main_image"]["success"] is True
    # 应调用 3 次：lane 0 attempt 1 + lane 0 attempt 2 + lane 1 attempt 1
    assert mock_wf.run_t6_upload_main_image.call_count == 3


def test_pipeline_human_escalate_stops():
    """所有 lane 都失败时应停止（HUMAN_ESCALATE）。"""
    mock_wf = MagicMock()
    # 所有尝试都失败
    mock_wf.run_t6_upload_main_image.return_value = WorkflowStepResult(
        step_id="T6", success=False, page_state="error", message="all failed",
    )
    mock_wf.window_manager = MagicMock()

    registry = ActionRegistry([ActionStep(
        step_name="t6-main-image",
        method_name="run_t6_upload_main_image",
        category=StepCategory.UPLOAD,
        required_params=("image_path",),
        param_map={"image_path": "file_path"},
        same_lane_max_retries=1,
        retry_lanes=(
            RetryLane("hover_modal", "run_t6_upload_main_image",
                       "悬停槽位", {"upload_strategy": "hover_modal"}),
            RetryLane("text_fallback", "run_t6_upload_main_image",
                       "文件对话框", {"upload_strategy": "text_fallback"}),
        ),
    )])

    executor = AgentExecutor(mock_wf)
    reflection = AgentReflection()
    pipeline = AgentPipeline(registry, executor, reflection)

    session = FakeSession()
    results = pipeline.run("t6-main-image", session, {"image_path": "/tmp/test.png"})

    # 2 个 lane × 1 次重试 = 2 次调用
    assert mock_wf.run_t6_upload_main_image.call_count == 2
    assert results["t6_main_image"]["success"] is False
    assert session.halted is True


def test_pipeline_trace_includes_lane_info():
    """trace 条目应包含 lane 名称和索引。"""
    mock_wf = MagicMock()
    mock_wf.run_t6_upload_main_image.side_effect = [
        WorkflowStepResult(step_id="T6", success=False, page_state="error", message="fail"),
        WorkflowStepResult(step_id="T6", success=True, page_state="ok", message="ok"),
    ]
    mock_wf.window_manager = MagicMock()

    registry = ActionRegistry([ActionStep(
        step_name="t6-main-image",
        method_name="run_t6_upload_main_image",
        category=StepCategory.UPLOAD,
        required_params=("image_path",),
        param_map={"image_path": "file_path"},
        same_lane_max_retries=1,
        retry_lanes=(
            RetryLane("hover_modal", "run_t6_upload_main_image", "悬停槽位"),
            RetryLane("text_fallback", "run_t6_upload_main_image", "文件对话框"),
        ),
    )])

    executor = AgentExecutor(mock_wf)
    reflection = AgentReflection()
    pipeline = AgentPipeline(registry, executor, reflection)

    session = FakeSession()
    pipeline.run("t6-main-image", session, {"image_path": "/tmp/test.png"})

    assert len(session.trace) == 2
    # 第一条 trace：lane 0 失败
    assert session.trace[0]["lane"] == "hover_modal"
    assert session.trace[0]["lane_index"] == 0
    assert session.trace[0]["verified"] is False
    # 第二条 trace：lane 1 成功
    assert session.trace[1]["lane"] == "text_fallback"
    assert session.trace[1]["lane_index"] == 1
    assert session.trace[1]["verified"] is True


def test_pipeline_no_lanes_fallback(step_no_lanes):
    """无 retry_lanes 的步骤保持旧的简单重试行为。"""
    mock_wf = MagicMock()
    mock_wf.run_t2_enter_publish_entry.side_effect = [
        WorkflowStepResult(step_id="T2", success=False, page_state="error", message="fail"),
        WorkflowStepResult(step_id="T2", success=True, page_state="ok", message="ok"),
    ]
    mock_wf.window_manager = MagicMock()

    registry = ActionRegistry([step_no_lanes])
    executor = AgentExecutor(mock_wf)
    reflection = AgentReflection()
    pipeline = AgentPipeline(registry, executor, reflection)

    session = FakeSession()
    results = pipeline.run("t2", session, {})

    assert mock_wf.run_t2_enter_publish_entry.call_count == 2
    assert results["t2"]["success"] is True
    # 无 lane info
    assert "lane" not in session.trace[0]


# ── Registry 验证测试 ──────────────────────────────────────────────


def test_registry_critical_steps_have_lanes():
    """关键步骤 (t4, t6-main-image, t6-detail-editor, t8-save-draft) 应有 lanes。"""
    registry = ActionRegistry(REGISTRY_ENTRIES)
    critical_steps = ["t4", "t6-main-image", "t6-detail-editor", "t8-save-draft"]
    for name in critical_steps:
        step = registry.get(name)
        assert len(step.retry_lanes) > 0, f"{name} missing retry_lanes"


def test_action_step_has_new_fields():
    """验证 ActionStep 新增字段存在且有默认值。"""
    step = ActionStep(step_name="test", method_name="test_method")
    assert step.retry_lanes == ()
    assert step.same_lane_max_retries == 3
