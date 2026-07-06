"""填充命令。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jm_ufo_agent.commands.base import Command


@dataclass(frozen=True)
class FillCommand:
    """字段填充命令构造器。"""

    field_name: str
    value: Any
    label: str = ""
    metadata: dict[str, Any] | None = None

    def to_command(self) -> Command:
        """转换为通用 Command。"""

        # 具体命令对象只负责描述意图，不直接执行。
        # action 固定为 fill，便于 SafetyPolicy 和 backend 分流。
        # metadata 为空时统一转成空字典，避免下游判断 None。
        return Command(action="fill", target=self.field_name, label=self.label or f"填写字段:{self.field_name}", value=self.value, metadata=self.metadata or {})
