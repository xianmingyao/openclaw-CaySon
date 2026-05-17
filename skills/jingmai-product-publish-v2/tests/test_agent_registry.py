"""test_agent_registry.py — ActionRegistry 测试。
BL-091: 验证 24 个 ActionStep 全覆盖、method_name 有效性、preconditions 一致性。
"""

from __future__ import annotations

import pytest

from jingmai_publish.agent.registry import REGISTRY, REGISTRY_ENTRIES, ActionRegistry
from jingmai_publish.agent.types import StepCategory


def test_registry_has_24_entries():
    """REGISTRY 应包含完整的 24 个 ActionStep 条目。"""
    assert len(REGISTRY_ENTRIES) == 24
    assert len(REGISTRY.list_all()) == 24


def test_registry_validates_known_steps():
    """所有 step_name 应通过 validate_step 验证。"""
    for entry in REGISTRY_ENTRIES:
        assert REGISTRY.validate_step(entry.step_name), f"expected {entry.step_name} to be valid"


def test_registry_rejects_unknown_step():
    """未知 step 应失败 validate_step 并 raise ValueError on get()。"""
    assert not REGISTRY.validate_step("nonexistent-step")
    with pytest.raises(ValueError, match="unknown step"):
        REGISTRY.get("nonexistent-step")


def test_registry_preconditions_are_valid():
    """所有 preconditions 引用的 step_name 必须在 REGISTRY 中存在。"""
    for entry in REGISTRY_ENTRIES:
        for precondition in entry.preconditions:
            assert REGISTRY.validate_step(precondition), (
                f"{entry.step_name} precondition {precondition} not registered"
            )


def test_registry_step_names_sorted():
    """step_names 属性应返回排序后的列表。"""
    names = REGISTRY.step_names
    assert names == sorted(names)
    assert "both" in names
    assert "t1" in names
    assert "t8-publish-product" in names


def test_registry_all_categories_present():
    """所有 StepCategory 值应有至少一个条目。"""
    categories = {entry.category for entry in REGISTRY_ENTRIES}
    expected = {
        StepCategory.ATTACHMENT,
        StepCategory.NAVIGATION,
        StepCategory.DATA_ENTRY,
        StepCategory.PROBE,
        StepCategory.UPLOAD,
        StepCategory.CONTENT,
        StepCategory.ACTION,
        StepCategory.COMPOSITE,
    }
    assert categories == expected


def test_registry_get_returns_action_step():
    """get() 应返回正确填充的 ActionStep。"""
    step = REGISTRY.get("t1")
    assert step.step_name == "t1"
    assert step.method_name == "run_t1_attach_window"
    assert step.category == StepCategory.ATTACHMENT
    assert step.max_retry_count == 2


def test_custom_entries_work():
    """可以用自定义 entries 创建 ActionRegistry。"""
    custom = ActionRegistry([
        REGISTRY_ENTRIES[0],  # t1
    ])
    assert custom.validate_step("t1")
    assert not custom.validate_step("t2")
