"""图片处理 worker。"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ImageProcessJob:
    """图片处理任务。"""

    product_id: str
    assets: list[str] = field(default_factory=list)
    payload: dict[str, Any] = field(default_factory=dict)


class ImageProcessWorker:
    """串行图片处理 worker。"""

    def __init__(self, handler: Callable[[ImageProcessJob], Awaitable[dict[str, Any]]]):
        """初始化图片处理 worker。"""

        # 图片转换可能调用 VLM，必须串行控制成本。
        # queue maxsize=1 表达“同一时间只处理一个重任务”。
        # handler 外部注入，测试可用纯函数。
        self.handler = handler
        self.queue: asyncio.Queue[ImageProcessJob | None] = asyncio.Queue(maxsize=1)
        self.results: list[dict[str, Any]] = []

    async def enqueue(self, job: ImageProcessJob) -> None:
        """提交图片处理任务。"""

        # put 会在队列满时等待，形成自然背压。
        # job 不在这里执行，保持生产者/消费者分离。
        # None 保留给 stop 信号使用。
        await self.queue.put(job)

    async def stop(self) -> None:
        """提交停止信号。"""

        # None 是约定的停止哨兵。
        # 使用队列发送停止，保证消费者按顺序退出。
        # 该方法不取消任务，避免半处理状态。
        await self.queue.put(None)

    async def run(self) -> list[dict[str, Any]]:
        """消费队列直到收到停止信号。"""

        # 循环读取任务，None 表示优雅退出。
        # 每个结果追加到 results，方便测试和后续状态汇总。
        # task_done 保持 Queue 语义完整。
        while True:
            job = await self.queue.get()
            try:
                if job is None:
                    return self.results
                self.results.append(await self.handler(job))
            finally:
                self.queue.task_done()
