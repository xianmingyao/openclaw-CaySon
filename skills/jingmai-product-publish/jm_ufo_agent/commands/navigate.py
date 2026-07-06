"""导航命令。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from jm_ufo_agent.commands.base import Command


@dataclass(frozen=True)
class NavigateCommand:
    """页面导航命令构造器。"""

    destination: str
    label: str = "导航"
    metadata: dict[str, Any] | None = None

    def to_command(self) -> Command:
        """转换为通用 Command。"""

        # 导航只表示进入某个页面或模块。
        # 不把导航建模成 submit，避免和发布/保存路径混淆。
        # destination 放入 target，便于 backend 定位执行方式。
        return Command(action="navigate", target=self.destination, label=self.label, metadata=self.metadata or {})
