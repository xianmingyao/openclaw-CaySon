"""读取命令。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jm_ufo_agent.commands.base import Command


@dataclass(frozen=True)
class ReadCommand:
    """读回字段命令构造器。"""

    target: str
    metadata: dict[str, Any] | None = None

    def to_command(self) -> Command:
        """转换为通用 Command。"""

        # read 命令用于读取 UI 当前值或截图 OCR 结果。
        # 它不修改界面，但仍进入统一命令模型。
        # metadata 可携带区域坐标和 OCR 参数。
        return Command(action="read", target=self.target, label="读回字段", metadata=self.metadata or {})
