"""运行时锁工具。"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class GuiLock:
    """串行化 GUI 操作的进程内锁。"""

    def __init__(self):
        """初始化 GUI 锁。"""

        # 京麦桌面 UI 不能被多个协程同时操作。
        # Phase 2 使用进程内 asyncio.Lock。
        # 跨进程锁后续由 Redis NX EX 实现。
        self._lock = asyncio.Lock()

    async def run(self, operation: Callable[[], Awaitable[T]]) -> T:
        """在 GUI 锁内运行异步操作。"""

        # async with 保证异常时也释放锁。
        # operation 是无参闭包，调用方可捕获上下文。
        # 返回值原样透传给调用方。
        async with self._lock:
            return await operation()
