"""结构化并发任务组 — 可取消的任务集合。

提供类似 asyncio.TaskGroup 的结构化并发控制，
支持超时、取消传播和结果收集。
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)


@dataclass
class TaskResult:
    """单个任务的执行结果。"""

    name: str
    ok: bool
    result: Any = None
    error: str = ""


class TaskGroup:
    """结构化并发任务组。

    # 参考 asyncio.TaskGroup（Python 3.11+），兼容 3.10。
    # 所有任务在组内运行，任一任务失败可取消其余任务。
    # 支持超时控制，超时后自动取消所有未完成任务。
    # 结果按任务名收集，便于后续汇总。
    """

    def __init__(
        self,
        name: str = "",
        cancel_on_error: bool = True,
        timeout_sec: float | None = None,
    ):
        """初始化任务组。"""
        self._name = name
        self._cancel_on_error = cancel_on_error
        self._timeout_sec = timeout_sec
        self._tasks: dict[str, asyncio.Task] = {}
        self._results: list[TaskResult] = []

    @property
    def name(self) -> str:
        """任务组名称。"""
        return self._name

    @property
    def results(self) -> list[TaskResult]:
        """所有已完成任务的结果。"""
        return list(self._results)

    def create_task(
        self,
        coro: Coroutine[Any, Any, Any],
        name: str = "",
    ) -> asyncio.Task:
        """创建并注册一个任务。"""
        task_name = name or f"task_{len(self._tasks)}"
        task = asyncio.create_task(coro, name=task_name)
        self._tasks[task_name] = task
        return task

    async def run_all(self) -> list[TaskResult]:
        """运行所有任务并等待完成。

        # cancel_on_error=True 时，任一任务失败则取消其余任务。
        # timeout_sec 超时后取消所有未完成任务。
        # 返回所有任务的 TaskResult 列表。
        """
        if not self._tasks:
            return []

        try:
            if self._timeout_sec is not None:
                await asyncio.wait_for(
                    self._run_with_error_handling(),
                    timeout=self._timeout_sec,
                )
            else:
                await self._run_with_error_handling()
        except asyncio.TimeoutError:
            logger.warning("TaskGroup %s 超时 (%.1fs)，取消剩余任务", self._name, self._timeout_sec)
            self._cancel_remaining()
            # 收集已完成任务的结果
            await self._collect_results()

        return self.results

    async def _run_with_error_handling(self) -> None:
        """运行所有任务，处理错误和取消传播。"""
        pending: set[asyncio.Task] = set(self._tasks.values())

        while pending:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

            for task in done:
                task_result = self._task_to_result(task)
                self._results.append(task_result)

                if not task_result.ok and self._cancel_on_error:
                    logger.warning(
                        "TaskGroup %s 任务 %s 失败: %s，取消剩余任务",
                        self._name, task_result.name, task_result.error,
                    )
                    self._cancel_remaining()
                    await self._collect_remaining()
                    return

    async def _collect_results(self) -> None:
        """收集所有已完成但未记录的任务结果。"""
        recorded_names = {r.name for r in self._results}
        for name, task in self._tasks.items():
            if name not in recorded_names and task.done():
                self._results.append(self._task_to_result(task))

    async def _collect_remaining(self) -> None:
        """等待被取消的任务完成并收集结果。"""
        remaining = [t for t in self._tasks.values() if not t.done()]
        if remaining:
            await asyncio.gather(*remaining, return_exceptions=True)
        await self._collect_results()

    def _cancel_remaining(self) -> None:
        """取消所有未完成任务。"""
        for task in self._tasks.values():
            if not task.done():
                task.cancel()

    @staticmethod
    def _task_to_result(task: asyncio.Task) -> TaskResult:
        """将 asyncio.Task 转为 TaskResult。"""
        name = task.get_name()
        try:
            result = task.result()
            return TaskResult(name=name, ok=True, result=result)
        except asyncio.CancelledError:
            return TaskResult(name=name, ok=False, error="cancelled")
        except Exception as exc:
            return TaskResult(name=name, ok=False, error=str(exc))
