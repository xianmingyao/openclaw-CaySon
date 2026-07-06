"""GUI 命令基础模型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Command:
    """一次即将执行的桌面动作。"""

    action: str
    target: str
    label: str = ""
    value: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def normalized_text(self) -> str:
        """返回用于安全策略匹配的归一化文本。

        # action/target/label 都可能承载“发布商品”等危险语义。
        # 统一转小写后拼接，SafetyPolicy 就能用同一套关键字判断。
        # value 可能包含商品标题或备注，也纳入检查以防提交类命令藏在值里。
        """

        parts = [self.action, self.target, self.label, "" if self.value is None else str(self.value)]
        return " ".join(part.strip().lower() for part in parts if part is not None)
