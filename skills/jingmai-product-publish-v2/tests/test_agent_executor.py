"""test_agent_executor.py — AgentExecutor 测试。
BL-091: 验证正确方法调度、参数过滤、缺失参数报错、异常包装、window_handle 注入。
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from jingmai_publish.agent.executor import AgentExecutor
from jingmai_publish.agent.registry import REGISTRY
from jingmai_publish.agent.types import ActionStep
from jingmai_publish.services.jingmai_workflow import WorkflowStepResult


@pytest.fixture
def service():
    """创建 mock workflow_service。"""
    svc = MagicMock()
    svc.window_manager.adapter = MagicMock()
    svc.run_t1_attach_window.return_value = WorkflowStepResult(
        step_id="T1", success=True, page_state="home", window_handle="2002"
    )
    svc.run_t2_enter_publish_entry.return_value = WorkflowStepResult(
        step_id="T2", success=True, page_state="publish_entry", window_handle="2002"
    )
    svc.run_t4_fill_base_info.return_value = WorkflowStepResult(
        step_id="T4", success=True, page_state="base_info_completed", window_handle="2002"
    )
    svc.run_t8_publish_product.return_value = WorkflowStepResult(
        step_id="T8", success=True, page_state="published", window_handle="2002"
    )
    svc.run_t6_upload_transparent_image.return_value = WorkflowStepResult(
        step_id="T6", success=True, page_state="uploaded", window_handle="2002"
    )
    return svc


class FakeSession:
    """最小化 session，供 executor 测试使用。"""
    window_handle = "2002"
    trace = []
    completed_steps = []
    page_state = None
    halted = False
    last_message = None
    max_retry_count = 3


def test_execute_t1_no_window_handle_required(service):
    """T1 不需要 window_handle，应直接调用 workflow 方法。"""
    executor = AgentExecutor(service)
    step = REGISTRY.get("t1")
    session = MagicMock(window_handle=None)
    # T1 不应要求 window_handle（见 executor.execute 逻辑）
    result = executor.execute(step, session, {})
    service.run_t1_attach_window.assert_called_once()
    assert result.success is True


def test_execute_workflow_service_method(service):
    """从 registry 获取步骤，通过 workflow_service 反射调用。"""
    executor = AgentExecutor(service)
    step = REGISTRY.get("t2")
    session = FakeSession()

    result = executor.execute(step, session, {})
    service.run_t2_enter_publish_entry.assert_called_once_with("2002")
    assert result.success is True


def test_execute_missing_window_handle_raises(service):
    """非 T1 步骤缺少 window_handle 应抛出 RuntimeError。"""
    executor = AgentExecutor(service)
    step = REGISTRY.get("t2")
    session = MagicMock(window_handle=None)

    with pytest.raises(RuntimeError, match="missing window handle"):
        executor.execute(step, session, {})


def test_execute_private_method_with_required_params(service):
    """私有 executor 方法需要 params 中的 required_params。"""
    executor = AgentExecutor(service)
    step = REGISTRY.get("t5-input-probe")
    session = FakeSession()
    service.window_manager.adapter = MagicMock()
    service.window_manager.adapter.inspect_controls_by_automation_id.return_value = []
    service.window_manager.adapter.activate_cell_by_automation_id.return_value = {"success": True}
    service.window_manager.adapter.type_into_focused_control.return_value = {"success": True}

    result = executor.execute(step, session, {
        "sku_cell_id": "jd-id-test",
        "sku_value": "test_value",
    })

    assert isinstance(result, dict)
    assert "success" in result


def test_execute_t8_publish(service):
    """T8 发布步骤应通过 workflow_service 反射调用（无额外参数）。"""
    executor = AgentExecutor(service)
    step = REGISTRY.get("t8-publish-product")
    session = FakeSession()

    result = executor.execute(step, session, {"confirm_publish": True})
    service.run_t8_publish_product.assert_called_once_with("2002", confirm_publish=True)
    assert result.success is True


def test_execute_t4_forwards_optional_brand_param(service):
    executor = AgentExecutor(service)
    step = REGISTRY.get("t4")
    session = FakeSession()

    result = executor.execute(
        step,
        session,
        {
            "title": "测试商品标题",
            "model": "B5440",
            "required_attribute": "B5440",
            "brand": "公牛（BULL）",
        },
    )

    service.run_t4_fill_base_info.assert_called_once_with(
        "2002",
        title="测试商品标题",
        model="B5440",
        required_attribute="B5440",
        brand="公牛（BULL）",
    )
    assert result.success is True


def test_build_kwargs_with_param_map(service):
    """_build_kwargs 应正确映射参数名。"""
    executor = AgentExecutor(service)
    step = ActionStep(
        step_name="test", method_name="run_test",
        required_params=("image_path",),
        param_map={"image_path": "file_path"},
    )
    kwargs = executor._build_kwargs(step, {"image_path": "/tmp/test.png"})
    assert kwargs == {"file_path": "/tmp/test.png"}


def test_build_kwargs_missing_required_raises(service):
    """缺少 required_params 应抛出 ValueError。"""
    executor = AgentExecutor(service)
    step = ActionStep(
        step_name="test", method_name="run_test",
        required_params=("image_path",),
    )
    with pytest.raises(ValueError, match="requires image_path"):
        executor._build_kwargs(step, {})
