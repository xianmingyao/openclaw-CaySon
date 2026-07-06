"""有状态 Agent 基类。"""

from __future__ import annotations

from typing import Any

from jm_ufo_agent.agents.base import BaseAgent


class StatefulAgent(BaseAgent):
    """需要保存轻量运行状态的 Agent。"""

    def __init__(self, name: str):
        """初始化状态容器。"""

        # state 只保存进程内临时状态，不作为恢复依据。
        # 可恢复状态必须写入 MySQL/Repository。
        # 该边界能避免崩溃恢复依赖内存对象。
        super().__init__(name=name)
        self.state: dict[str, Any] = {}

    def remember(self, key: str, value: Any) -> None:
        """记录临时状态。"""

        # 该方法只用于缓存窗口句柄、最近截图等短期信息。
        # 不在这里做 JSON 序列化，因为它不是持久化层。
        # 调用方需要持久化时应写 Repository。
        self.state[key] = value

    def recall(self, key: str, default: Any = None) -> Any:
        """读取临时状态。"""

        # 读取不到时返回调用方给定默认值。
        # 不抛 KeyError，减少节点恢复时的分支噪音。
        # 真正必需的证据应通过 VerifyStrategy 校验。
        return self.state.get(key, default)
