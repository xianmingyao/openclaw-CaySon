"""RowDispatcher 多行并发调度测试。"""

import asyncio
from unittest.mock import AsyncMock

import pytest

from jm_ufo_agent.runtime.dispatcher import RowDispatcher, RowResult


class TestRowResult:
    def test_success_result(self):
        result = RowResult(row_index=0, ok=True, message="完成")
        assert result.ok is True
        assert result.row_index == 0

    def test_failure_result(self):
        result = RowResult(row_index=1, ok=False, message="失败", error="字段验证不通过")
        assert result.ok is False
        assert result.error == "字段验证不通过"


class TestRowDispatcher:
    def test_init_default_concurrency(self):
        dispatcher = RowDispatcher()
        assert dispatcher.max_concurrency == 3

    def test_init_custom_concurrency(self):
        dispatcher = RowDispatcher(max_concurrency=5)
        assert dispatcher.max_concurrency == 5

    @pytest.mark.asyncio
    async def test_dispatch_single_row(self):
        """单行调度应正确返回结果。"""
        mock_handler = AsyncMock(return_value=RowResult(row_index=0, ok=True, message="完成"))
        dispatcher = RowDispatcher(max_concurrency=1)

        results = await dispatcher.dispatch(
            rows=[{"title": "商品1", "price": 99.9}],
            handler=mock_handler,
        )
        assert len(results) == 1
        assert results[0].ok is True
        assert results[0].row_index == 0

    @pytest.mark.asyncio
    async def test_dispatch_multiple_rows_concurrent(self):
        """多行应受信号量限制并发执行。"""
        async def slow_handler(row_index: int, row_data: dict) -> RowResult:
            await asyncio.sleep(0.05)
            return RowResult(row_index=row_index, ok=True, message="完成")

        dispatcher = RowDispatcher(max_concurrency=2)
        rows = [{"title": f"商品{i}"} for i in range(5)]

        results = await dispatcher.dispatch(rows=rows, handler=slow_handler)
        assert len(results) == 5
        assert all(r.ok for r in results)

    @pytest.mark.asyncio
    async def test_dispatch_row_failure_does_not_block_others(self):
        """单行失败不应阻塞其他行。"""
        async def flaky_handler(row_index: int, row_data: dict) -> RowResult:
            if row_index == 1:
                return RowResult(row_index=row_index, ok=False, message="失败", error="验证失败")
            return RowResult(row_index=row_index, ok=True, message="完成")

        dispatcher = RowDispatcher(max_concurrency=3)
        rows = [{"title": f"商品{i}"} for i in range(3)]

        results = await dispatcher.dispatch(rows=rows, handler=flaky_handler)
        assert len(results) == 3
        assert results[0].ok is True
        assert results[1].ok is False
        assert results[2].ok is True

    @pytest.mark.asyncio
    async def test_dispatch_empty_rows(self):
        """空行列表应返回空结果。"""
        dispatcher = RowDispatcher()
        results = await dispatcher.dispatch(rows=[], handler=AsyncMock())
        assert results == []

    @pytest.mark.asyncio
    async def test_concurrency_limit_respected(self):
        """并发数不应超过 max_concurrency。"""
        peak_concurrent = 0
        current_concurrent = 0

        async def tracking_handler(row_index: int, row_data: dict) -> RowResult:
            nonlocal peak_concurrent, current_concurrent
            current_concurrent += 1
            peak_concurrent = max(peak_concurrent, current_concurrent)
            await asyncio.sleep(0.05)
            current_concurrent -= 1
            return RowResult(row_index=row_index, ok=True, message="完成")

        dispatcher = RowDispatcher(max_concurrency=2)
        rows = [{"title": f"商品{i}"} for i in range(6)]

        await dispatcher.dispatch(rows=rows, handler=tracking_handler)
        assert peak_concurrent <= 2
