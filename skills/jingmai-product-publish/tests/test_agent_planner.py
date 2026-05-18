"""test_agent_planner.py — AgentPlanner 测试。
BL-091: 验证 both/t2/t4/t1/invalid/topological 各场景。
"""

from __future__ import annotations

import pytest

from jingmai_publish.agent.planner import AgentPlanner
from jingmai_publish.agent.registry import REGISTRY


@pytest.fixture
def planner():
    return AgentPlanner(REGISTRY)


def test_plan_both_returns_t1_t2(planner):
    """both 复合步骤应展开为 [t1, t2]。"""
    plan = planner.plan("both")
    step_names = [s.step_name for s in plan.steps]
    assert step_names == ["t1", "t2"]
    assert plan.target_step == "both"


def test_plan_t2_includes_precondition(planner):
    """t2 应包含其 precondition t1，且 t1 在 t2 之前。"""
    plan = planner.plan("t2")
    step_names = [s.step_name for s in plan.steps]
    assert "t1" in step_names
    assert "t2" in step_names
    # t1 必须在 t2 之前
    assert step_names.index("t1") < step_names.index("t2")
    assert plan.target_step == "t2"


def test_plan_t4_includes_all_preconditions(planner):
    """t4 应包含 t1 和 t3（preconditions）。"""
    plan = planner.plan("t4")
    step_names = [s.step_name for s in plan.steps]
    assert "t1" in step_names
    assert "t3" in step_names
    assert "t4" in step_names
    assert step_names.index("t1") < step_names.index("t3")
    assert step_names.index("t3") < step_names.index("t4")
    assert plan.target_step == "t4"


def test_plan_t1_returns_single_step(planner):
    """无 precondition 的 t1 应返回单步计划。"""
    plan = planner.plan("t1")
    step_names = [s.step_name for s in plan.steps]
    assert step_names == ["t1"]
    assert plan.target_step == "t1"


def test_plan_invalid_step_raises(planner):
    """无效 step 名应抛出 ValueError。"""
    with pytest.raises(ValueError, match="unsupported"):
        planner.plan("t99")


def test_plan_topological_order_preserved(planner):
    """任意步骤的依赖应按拓扑顺序排列。"""
    # t4-extra 依赖 t1 → t3 → t4，以此验证拓扑正确性
    plan = planner.plan("t4-extra")
    step_names = [s.step_name for s in plan.steps]

    # t1 必须在 t3 之前
    assert step_names.index("t1") < step_names.index("t3")
    # t3 必须在 t4 之前
    assert step_names.index("t3") < step_names.index("t4")
    # t4 必须在 t4-extra 之前
    assert step_names.index("t4") < step_names.index("t4-extra")
    assert plan.target_step == "t4-extra"
