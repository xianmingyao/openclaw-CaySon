"""GUI 主循环 worker。"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from jm_ufo_agent.runtime.locks import GuiLock


@dataclass(frozen=True)
class GuiJob:
    """GUI 操作任务。"""

    name: str
    payload: dict[str, Any] = field(default_factory=dict)


class GuiWorker:
    """串行 GUI 操作 worker。"""

    def __init__(self, handler: Callable[[GuiJob], Awaitable[dict[str, Any]]], gui_lock: GuiLock | None = None):
        """初始化 GUI worker。"""

        # handler 由外部注入，真实实现会调用 DesktopAgent。
        # gui_lock 默认新建进程内锁，确保同一进程串行操作 UI。
        # worker 不直接操作窗口，保持可测试。
        self.handler = handler
        self.gui_lock = gui_lock or GuiLock()

    async def process(self, job: GuiJob) -> dict[str, Any]:
        """在 GUI 锁内处理任务。"""

        # 所有 GUI job 都必须进入 GuiLock。
        # 使用闭包延迟执行 handler，确保锁内才触发动作。
        # 返回 handler 的业务结果。
        return await self.gui_lock.run(lambda: self.handler(job))
