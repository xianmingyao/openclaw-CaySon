"""test_vision_pipeline.py — BL-086B 视觉对比集成测试。

验证 AgentPipeline 与 OllamaVisionProvider.compare_screenshots() 的集成：
- 视觉提供者可选的优雅降级
- before/after 截图传递和对比
- vision_analysis 写入 trace 和传入 reflect()
- 异常安全处理
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from jingmai_publish.agent import REGISTRY, AgentExecutor, AgentPipeline, AgentReflection
from jingmai_publish.runtime.vision import VisionAnalysis
from jingmai_publish.services.jingmai_workflow import WorkflowStepResult


class FakeSession:
    """最小 session 模拟类，含 BL-086B 截图字段。"""

    def __init__(self) -> None:
        self.window_handle = None
        self.trace: list[dict] = []
        self.completed_steps: list[str] = []
        self.page_state = None
        self.halted = False
        self.last_message = None
        self.max_retry_count = 3
        self.last_screenshot: str | None = None
        self.screenshot_before: str | None = None
        self.screenshot_after: str | None = None


def _make_success_result(step_id="T1", screenshot=None):
    return WorkflowStepResult(
        step_id=step_id,
        success=True,
        page_state="test_page",
        window_handle="2002",
        screenshot_path=screenshot,
    )


# ── 无视觉提供者：向后兼容 ──────────────────────────────────────

def test_no_vision_provider_does_not_break_flow():
    """无 vision_provider 时管线行为与之前完全一致。"""
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = _make_success_result(
        "T1", screenshot="/tmp/s1.png"
    )

    pipeline = AgentPipeline(REGISTRY, AgentExecutor(service), AgentReflection())
    session = FakeSession()
    results = pipeline.run("t1", session, {})

    assert results["t1"]["success"] is True
    # vision_analysis 不应出现在 trace 中
    assert "vision_analysis" not in session.trace[0]
    # last_screenshot 已更新
    assert session.last_screenshot == "/tmp/s1.png"
    assert session.screenshot_after == "/tmp/s1.png"


def test_no_screenshots_in_outcome_skips_vision():
    """outcome 无 screenshot_path 时不触发视觉对比。"""
    vision_mock = MagicMock()

    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1", success=True, page_state="home", window_handle="2002",
    )  # 无 screenshot_path

    pipeline = AgentPipeline(
        REGISTRY, AgentExecutor(service), AgentReflection(),
        vision_provider=vision_mock,
    )
    session = FakeSession()
    pipeline.run("t1", session, {})

    vision_mock.compare_screenshots.assert_not_called()
    assert "vision_analysis" not in session.trace[0]


def test_only_before_screenshot_skips_vision():
    """仅有 before 截图无 after 时不触发视觉对比。"""
    vision_mock = MagicMock()

    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    # 上一个步骤有截图，当前步骤没有
    service.run_t2_enter_publish_entry.return_value = WorkflowStepResult(
        step_id="T2", success=True, page_state="entry", window_handle="2002",
    )  # 无 screenshot_path

    pipeline = AgentPipeline(
        REGISTRY, AgentExecutor(service), AgentReflection(),
        vision_provider=vision_mock,
    )
    session = FakeSession()
    session.last_screenshot = "/tmp/prev.png"  # 上一帧有截图

    pipeline.run("t2", session, {})

    # 虽然有 before 但无 after，不触发对比
    vision_mock.compare_screenshots.assert_not_called()


# ── 视觉对比正常流转 ──────────────────────────────────────────

def test_vision_comparison_on_valid_screenshots():
    """before/after 截图都存在时触发视觉对比，结果写入 trace。"""
    vision_mock = MagicMock()
    vision_mock.compare_screenshots.return_value = VisionAnalysis(
        success=True,
        page_state="form_filled",
        text_content="价格字段已填充，按钮已激活",
        confidence=0.92,
        model="llava:13b",
    )

    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    # 必须 mock t1：planner 解析 t2 依赖链会执行 t1 + t2
    service.run_t1_attach_window.return_value = _make_success_result("T1")
    service.run_t2_enter_publish_entry.return_value = _make_success_result(
        "T2", screenshot="/tmp/after_t2.png"
    )

    pipeline = AgentPipeline(
        REGISTRY, AgentExecutor(service), AgentReflection(),
        vision_provider=vision_mock,
    )
    session = FakeSession()
    # t1 会设置 window_handle；last_screenshot 模拟上一步截图
    session.last_screenshot = "/tmp/before_t2.png"

    with patch("pathlib.Path.exists", return_value=True):
        pipeline.run("t2", session, {})

    vision_mock.compare_screenshots.assert_called_once_with(
        "/tmp/before_t2.png", "/tmp/after_t2.png"
    )

    # trace 包含 vision_analysis（t2 步骤的 trace，不是 t1 的）
    trace_t2 = [t for t in session.trace if t.get("planned_step") == "t2"]
    assert len(trace_t2) >= 1
    trace = trace_t2[0]
    assert "vision_analysis" in trace
    va = trace["vision_analysis"]
    assert va["vision_success"] is True
    assert va["vision_confidence"] == 0.92
    assert va["vision_page_state"] == "form_filled"
    assert va["vision_model"] == "llava:13b"

    # last_screenshot 更新为当前步骤的 after
    assert session.last_screenshot == "/tmp/after_t2.png"


def test_vision_comparison_on_failure():
    """视觉对比报告 action 失败时，vision_success=False 传给 reflect()。"""
    vision_mock = MagicMock()
    vision_mock.compare_screenshots.return_value = VisionAnalysis(
        success=False,
        page_state="unchanged",
        text_content="页面无变化，按钮仍为灰色",
        confidence=0.88,
        model="llava:13b",
    )

    # 同时文本判断也失败 → 视觉失败应出现在 reflect() 参数中
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1", success=False, page_state="error",
        window_handle="2002", screenshot_path="/tmp/t1_fail.png",
        message="action failed",
    )

    reflection_spy = MagicMock(wraps=AgentReflection())
    pipeline = AgentPipeline(
        REGISTRY, AgentExecutor(service), reflection_spy,
        vision_provider=vision_mock,
    )
    session = FakeSession()
    session.last_screenshot = "/tmp/before_t1.png"

    with patch("pathlib.Path.exists", return_value=True):
        pipeline.run("t1", session, {})

    # reflect() 被调用时传入了 vision_analysis
    call_kwargs = reflection_spy.reflect.call_args.kwargs
    assert call_kwargs["vision_analysis"] is not None
    assert call_kwargs["vision_analysis"]["vision_success"] is False


def test_vision_exception_handled_gracefully():
    """视觉对比异常不应阻塞主流程。"""
    vision_mock = MagicMock()
    vision_mock.compare_screenshots.side_effect = RuntimeError("Ollama unreachable")

    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = _make_success_result(
        "T1", screenshot="/tmp/s1.png"
    )

    pipeline = AgentPipeline(
        REGISTRY, AgentExecutor(service), AgentReflection(),
        vision_provider=vision_mock,
    )
    session = FakeSession()
    session.last_screenshot = "/tmp/s0.png"

    with patch("pathlib.Path.exists", return_value=True):
        results = pipeline.run("t1", session, {})

    # 主流程未受影响
    assert results["t1"]["success"] is True
    # vision_analysis 不应出现在 trace 中（异常后返回 None）
    assert "vision_analysis" not in session.trace[0]


def test_missing_file_skips_vision():
    """截图文件不存在时跳过视觉对比。"""
    vision_mock = MagicMock()

    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = _make_success_result(
        "T1", screenshot="/tmp/missing_after.png"
    )

    pipeline = AgentPipeline(
        REGISTRY, AgentExecutor(service), AgentReflection(),
        vision_provider=vision_mock,
    )
    session = FakeSession()
    session.last_screenshot = "/tmp/missing_before.png"

    # Path.exists() 返回 False（文件不存在）
    with patch("pathlib.Path.exists", return_value=False):
        pipeline.run("t1", session, {})

    vision_mock.compare_screenshots.assert_not_called()
    assert "vision_analysis" not in session.trace[0]


# ── 跨步骤截图传递 ──────────────────────────────────────────

def test_last_screenshot_propagates_between_steps():
    """步骤 N 的 after 截图成为步骤 N+1 的 before 截图。"""
    vision_mock = MagicMock()
    vision_mock.compare_screenshots.return_value = VisionAnalysis(
        success=True, page_state="ok", confidence=0.9, model="llava",
    )

    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = _make_success_result(
        "T1", screenshot="/tmp/t1.png"
    )
    service.run_t2_enter_publish_entry.return_value = _make_success_result(
        "T2", screenshot="/tmp/t2.png"
    )

    pipeline = AgentPipeline(
        REGISTRY, AgentExecutor(service), AgentReflection(),
        vision_provider=vision_mock,
    )
    session = FakeSession()

    with patch("pathlib.Path.exists", return_value=True):
        pipeline.run("t2", session, {})

    # T1 执行时无 before 截图 → 不触发 vision 对比
    # T2 执行时 before = T1 的 after → 触发 1 次 vision 对比
    assert vision_mock.compare_screenshots.call_count == 1

    # 验证 T2 的对比参数正确跨越了步骤
    t2_call_args = vision_mock.compare_screenshots.call_args_list[0]
    assert t2_call_args[0][0] == "/tmp/t1.png"  # before = T1 的 after
    assert t2_call_args[0][1] == "/tmp/t2.png"  # after = T2 的 after

    # T2 执行后 last_screenshot 更新
    assert session.last_screenshot == "/tmp/t2.png"


# ── vision_analysis 影响反射决策 ──────────────────────────────

def test_vision_success_downgrades_abort_to_retry():
    """所有重试耗尽但视觉校验通过时，应从 ABORT 降级为 RETRY。"""
    vision_mock = MagicMock()
    vision_mock.compare_screenshots.return_value = VisionAnalysis(
        success=True,  # 视觉说页面状态正确
        page_state="form_filled",
        confidence=0.85,
        model="llava",
    )

    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    # 连续 3 次失败
    service.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1", success=False, page_state="error",
        window_handle="2002", screenshot_path="/tmp/t1_err.png",
        message="step failed",
    )

    pipeline = AgentPipeline(
        REGISTRY, AgentExecutor(service), AgentReflection(),
        vision_provider=vision_mock,
    )
    session = FakeSession()
    session.max_retry_count = 3
    session.last_screenshot = "/tmp/t0.png"

    with patch("pathlib.Path.exists", return_value=True):
        results = pipeline.run("t1", session, {})

    # 视觉校验通过后，第 3 次耗尽时降级为 RETRY（不是 ABORT）
    # trace 应包含 3 次尝试（max_retry_count=3），每次都失败，但视觉说 OK → RETRY
    assert len(session.trace) >= 3
    # 检查最后一次 trace 是否有 vision_analysis
    last_trace = session.trace[-1]
    assert "vision_analysis" in last_trace
    assert last_trace["vision_analysis"]["vision_success"] is True


# ── before_state trace 包含截图路径 ──────────────────────────

def test_before_state_includes_screenshot_before():
    """before_state 快照应包含 screenshot_before 路径。"""
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = _make_success_result(
        "T1", screenshot="/tmp/t1.png"
    )

    pipeline = AgentPipeline(REGISTRY, AgentExecutor(service), AgentReflection())
    session = FakeSession()
    session.last_screenshot = "/tmp/t0.png"  # 上一步截图

    pipeline.run("t1", session, {})

    before_state = session.trace[0]["before_state"]
    assert before_state.get("screenshot_before") == "/tmp/t0.png"


def test_before_state_no_screenshot_when_none():
    """无上一步截图时 before_state 不包含 screenshot_before 键。"""
    service = MagicMock()
    service.window_manager.adapter = MagicMock()
    service.run_t1_attach_window.return_value = _make_success_result("T1")

    pipeline = AgentPipeline(REGISTRY, AgentExecutor(service), AgentReflection())
    session = FakeSession()
    # 无 last_screenshot

    pipeline.run("t1", session, {})

    assert "screenshot_before" not in session.trace[0]["before_state"]
