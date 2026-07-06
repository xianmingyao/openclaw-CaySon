"""异步重试工具。"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class RetryPolicy:
    """指数退避配置。"""

    max_attempts: int = 3
    base_delay_sec: float = 1.0
    max_delay_sec: float = 60.0

    def delay_for_attempt(self, attempt_index: int) -> float:
        """计算第 N 次失败后的等待时间。

        # attempt_index 从 0 开始，第一次失败等待 base_delay。
        # 每次失败后翻倍，超过 max_delay_sec 时按上限等待。
        # 该方法是纯函数，便于单元测试验证退避序列。
        """

        return min(self.max_delay_sec, self.base_delay_sec * (2**attempt_index))


async def retry_async(operation: Callable[[], Awaitable[T]], policy: RetryPolicy) -> T:
    """按策略重试异步操作。

    # 最后一次失败会原样抛出异常，调用方能记录真实错误。
    # 中间失败只负责等待和重试，不吞掉异常类型。
    # sleep 使用 asyncio.sleep，避免阻塞 GUI 主循环。
    """

    last_error: BaseException | None = None
    for attempt in range(policy.max_attempts):
        try:
            return await operation()
        except BaseException as exc:
            last_error = exc
            if attempt == policy.max_attempts - 1:
                break
            await asyncio.sleep(policy.delay_for_attempt(attempt))
    assert last_error is not None
    raise last_error
