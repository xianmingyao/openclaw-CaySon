"""点击命令。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jm_ufo_agent.commands.base import Command


@dataclass(frozen=True)
class ClickCommand:
    """点击命令构造器。"""

    target: str
    label: str = ""
    metadata: dict[str, Any] | None = None

    def to_command(self) -> Command:
        """转换为通用 Command。"""

        # 点击命令可能是普通按钮，也可能是保存草稿。
        # label 原样传递给 SafetyPolicy 做危险关键字识别。
        # metadata 可携带坐标、截图 hash 或窗口句柄摘要。
        return Command(action="click", target=self.target, label=self.label, metadata=self.metadata or {})
