"""数据抓取 worker。"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DataFetchJob:
    """数据抓取任务。"""

    product_id: str
    payload: dict[str, Any] = field(default_factory=dict)


class DataFetchWorker:
    """限制并发的数据抓取 worker。"""

    def __init__(self, handler: Callable[[DataFetchJob], Awaitable[dict[str, Any]]], concurrency: int = 3):
        """初始化 worker。"""

        # handler 由外部注入，真实实现可以是京东抓取。
        # concurrency 默认 3，对应设计文档的数据抓取并发上限。
        # semaphore 确保多个 process 调用也共享同一并发限制。
        self.handler = handler
        self.semaphore = asyncio.Semaphore(concurrency)

    async def process(self, jobs: list[DataFetchJob]) -> list[dict[str, Any]]:
        """处理一组抓取任务。"""

        # 每个 job 包装进 _run_one，统一套 semaphore。
        # gather 保持输入顺序，方便把结果写回对应 row。
        # handler 异常会向上传递，让 workflow halt 或重试。
        return await asyncio.gather(*(self._run_one(job) for job in jobs))

    async def _run_one(self, job: DataFetchJob) -> dict[str, Any]:
        """处理单个抓取任务。"""

        # semaphore 保护外部网站和本地资源。
        # async with 保证异常时释放并发槽。
        # 返回 handler 原始结果，worker 不做业务解释。
        async with self.semaphore:
            return await self.handler(job)
