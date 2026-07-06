"""多行并发调度器 — RowDispatcher。"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable


@dataclass
class RowResult:
    """单行执行结果。"""

    row_index: int
    ok: bool
    message: str = ""
    error: str = ""
    data: dict[str, Any] = field(default_factory=dict)


# handler 签名：(row_index, row_data) -> RowResult
RowHandler = Callable[[int, dict[str, Any]], Awaitable[RowResult]]


class RowDispatcher:
    """多行并发调度器，使用 asyncio.Semaphore 控制并发。"""

    def __init__(self, max_concurrency: int = 3):
        """初始化调度器。

        # max_concurrency 控制同时执行的行数。
        # 默认 3，平衡 GUI 压力和吞吐量。
        # GUI 操作（click/fill）由 GuiLock 串行化，不会并发冲突。
        """
        self.max_concurrency = max_concurrency

    async def dispatch(
        self,
        rows: list[dict[str, Any]],
        handler: RowHandler,
    ) -> list[RowResult]:
        """并发调度多行执行。

        # 使用 Semaphore 限制并发数，避免 GUI 过载。
        # 每行独立执行，单行失败不影响其他行。
        # 结果按 row_index 排序返回。
        """
        if not rows:
            return []

        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def _run_one(index: int, row: dict[str, Any]) -> RowResult:
            async with semaphore:
                try:
                    return await handler(index, row)
                except Exception as exc:
                    return RowResult(row_index=index, ok=False, message="异常", error=str(exc))

        tasks = [_run_one(i, row) for i, row in enumerate(rows)]
        results = await asyncio.gather(*tasks)
        return sorted(results, key=lambda r: r.row_index)
