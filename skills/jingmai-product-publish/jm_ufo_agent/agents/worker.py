"""无状态 WorkerAgent。"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from jm_ufo_agent.agents.base import AgentContext, AgentResult, BaseAgent


class WorkerAgent(BaseAgent):
    """执行纯数据任务的 Agent。"""

    def __init__(self, name: str, handler: Callable[[AgentContext], Awaitable[dict[str, Any]]] | None = None):
        """初始化 WorkerAgent。"""

        # handler 是可注入的异步函数，真实抓取/转换逻辑后续接入这里。
        # 不传 handler 时返回空结果，保证 dry-run 可以完整走通。
        # 这种设计让测试不需要网络、浏览器或图片服务。
        super().__init__(name=name)
        self.handler = handler

    async def run(self, context: AgentContext) -> AgentResult:
        """执行一次 worker 任务。"""

        # 没有 handler 表示该能力尚未接入真实实现。
        # 有 handler 时只负责调用和包装结果，不在这里做业务决策。
        # 失败异常不吞掉，交给 workflow 的反思/中止节点处理。
        if self.handler is None:
            return AgentResult(ok=True, message=f"{self.name} dry-run", data={})
        data = await self.handler(context)
        return AgentResult(ok=True, message=f"{self.name} completed", data=data)
