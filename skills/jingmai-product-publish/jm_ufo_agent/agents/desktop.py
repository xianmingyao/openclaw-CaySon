"""桌面 Agent 与可替换 backend。"""

from __future__ import annotations

from typing import Protocol

from jm_ufo_agent.agents.base import AgentResult
from jm_ufo_agent.agents.stateful import StatefulAgent
from jm_ufo_agent.commands.base import Command
from jm_ufo_agent.safety.policy import SafetyPolicy


class DesktopBackend(Protocol):
    """桌面动作 backend 协议。"""

    async def execute(self, command: Command) -> AgentResult:
        """执行已经通过安全校验的命令。"""


class RecordingDesktopBackend:
    """只记录命令的 dry-run backend。"""

    def __init__(self):
        """初始化命令记录列表。"""

        # commands 用于测试和 dry-run 证据。
        # 不触碰真实窗口，避免误操作京麦。
        # 后续 UFO v1 适配层会实现同一个 execute 协议。
        self.commands: list[Command] = []

    async def execute(self, command: Command) -> AgentResult:
        """记录命令并返回成功。"""

        # 命令到达这里时已经通过 SafetyPolicy。
        # 记录完整 Command，便于断言 label/value/metadata。
        # 返回数据包含 action，方便 workflow 汇总执行轨迹。
        self.commands.append(command)
        return AgentResult(ok=True, message="dry-run command recorded", data={"action": command.action})


class DesktopAgent(StatefulAgent):
    """统一受 SafetyPolicy 保护的桌面 Agent。"""

    def __init__(self, name: str, safety_policy: SafetyPolicy | None = None, backend: DesktopBackend | None = None):
        """初始化桌面 Agent。"""

        # safety_policy 默认启用硬阻断策略。
        # backend 默认是记录型 dry-run，真实 GUI 能力必须显式注入。
        # 所有 click/fill/submit 都从这里集中校验，避免子类绕过。
        super().__init__(name=name)
        self.safety_policy = safety_policy or SafetyPolicy()
        self.backend = backend or RecordingDesktopBackend()

    async def click(self, target: str, label: str = "", metadata: dict | None = None) -> AgentResult:
        """执行点击动作。"""

        # 先构造标准 Command，让安全策略看到完整上下文。
        # assert_allowed 必须在 backend.execute 前执行。
        # metadata 用于携带窗口、坐标、证据等额外信息。
        command = Command(action="click", target=target, label=label, metadata=metadata or {})
        self.safety_policy.assert_allowed(command)
        return await self.backend.execute(command)

    async def fill(self, target: str, value: object, label: str = "", metadata: dict | None = None) -> AgentResult:
        """执行填充动作。"""

        # fill 也可能写价格或危险字段，所以同样走 SafetyPolicy。
        # value 保留原始对象，价格策略会自行转换 Decimal。
        # backend 只处理已经通过校验的动作。
        command = Command(action="fill", target=target, label=label, value=value, metadata=metadata or {})
        self.safety_policy.assert_allowed(command)
        return await self.backend.execute(command)

    async def submit(self, target: str, label: str = "", metadata: dict | None = None) -> AgentResult:
        """执行提交类动作。"""

        # submit 是高风险入口，必须统一建模。
        # 保存草稿允许通过，发布商品会被 SafetyPolicy 拦截。
        # 后续真实 backend 不能自行跳过这里。
        command = Command(action="submit", target=target, label=label, metadata=metadata or {})
        self.safety_policy.assert_allowed(command)
        return await self.backend.execute(command)
