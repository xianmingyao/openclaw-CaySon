import asyncio
from decimal import Decimal

import pytest

from jm_ufo_agent.utils.cosine_sim import cosine_similarity
from jm_ufo_agent.utils.pricing import calculate_sale_price, quantize_money
from jm_ufo_agent.utils.retry import RetryPolicy, retry_async


def test_quantize_money_uses_two_decimal_places():
    assert quantize_money("10.235") == Decimal("10.24")


def test_calculate_sale_price_caps_by_market_upper_bound():
    assert calculate_sale_price("100", "105") == Decimal("115.50")


def test_cosine_similarity_handles_normal_vectors():
    assert cosine_similarity([1, 0], [1, 0]) == 1.0
    assert cosine_similarity([1, 0], [0, 1]) == 0.0


def test_cosine_similarity_rejects_dimension_mismatch():
    with pytest.raises(ValueError, match="维度不一致"):
        cosine_similarity([1], [1, 2])


async def test_retry_async_retries_until_success(monkeypatch):
    calls = 0
    sleeps: list[float] = []

    async def operation():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise RuntimeError("temporary")
        return "ok"

    async def fake_sleep(seconds: float):
        sleeps.append(seconds)

    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    result = await retry_async(operation, RetryPolicy(max_attempts=3, base_delay_sec=1, max_delay_sec=10))

    assert result == "ok"
    assert sleeps == [1, 2]
