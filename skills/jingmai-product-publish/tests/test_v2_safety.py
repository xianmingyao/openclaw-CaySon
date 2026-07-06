from decimal import Decimal

import pytest

from jm_ufo_agent.commands.base import Command
from jm_ufo_agent.safety.policy import SafetyPolicy, SafetyViolation
from scripts.check_safety_policy import main as safety_check_main


def test_safety_policy_blocks_publish_action():
    policy = SafetyPolicy()

    with pytest.raises(SafetyViolation, match="高风险动作"):
        policy.assert_allowed(Command(action="click", target="button", label="发布商品"))


def test_safety_policy_allows_save_draft_label():
    policy = SafetyPolicy()

    policy.assert_allowed(Command(action="click", target="button", label="保存草稿"))


def test_safety_policy_blocks_price_without_evidence():
    policy = SafetyPolicy()

    with pytest.raises(SafetyViolation, match="缺少必要证据"):
        policy.assert_allowed(Command(action="fill_price", target="price", value="10.00"))


def test_safety_policy_blocks_price_outside_allowed_range():
    policy = SafetyPolicy()
    command = Command(
        action="fill_price",
        target="sale_price",
        value="200.00",
        metadata={"purchase_price": "100.00", "market_price": "120.00"},
    )

    with pytest.raises(SafetyViolation, match="超出允许范围"):
        policy.assert_allowed(command)


def test_safety_policy_allows_price_inside_allowed_range():
    policy = SafetyPolicy()
    command = Command(
        action="fill_price",
        target="sale_price",
        value="108.00",
        metadata={"purchase_price": "100.00", "market_price": "120.00"},
    )

    policy.assert_allowed(command)
    bounds = policy.price_bounds(Decimal("100"), Decimal("120"))
    assert bounds.min_price == Decimal("90.00")
    assert bounds.max_price == Decimal("132.00")


def test_safety_static_check_passes_project_sources():
    assert safety_check_main(["jm_ufo_agent/agents"]) == 0


def test_safety_static_check_blocks_unprotected_method(tmp_path):
    path = tmp_path / "bad_agent.py"
    path.write_text(
        """
class BadAgent:
    async def click(self, target):
        return await self.backend.execute(target)
""",
        encoding="utf-8",
    )

    assert safety_check_main([str(path)]) == 1
